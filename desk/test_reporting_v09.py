"""Staff-only reporting and CSV export regression tests."""
import csv
from datetime import timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from .models import Asset, Ticket
from .reporting import csv_safe

User = get_user_model()


class ReportingTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            'report_staff', password='example-strong-password-123', is_staff=True
        )
        self.employee = User.objects.create_user(
            'report_employee', password='example-strong-password-123'
        )
        self.current = Ticket.objects.create(
            title='=HYPERLINK("https://example.invalid","Click")',
            description='Sensitive description not for export',
            category='+Network',
            priority='high',
            status='open',
            reporter=self.employee,
            assigned_to=None,
            due_at=timezone.now() - timedelta(days=1),
        )
        self.old = Ticket.objects.create(
            title='Old closed request',
            description='Older ticket',
            priority='low',
            status='closed',
            reporter=self.employee,
        )
        Ticket.objects.filter(pk=self.old.pk).update(
            created_at=timezone.now() - timedelta(days=120)
        )
        self.asset = Asset.objects.create(
            asset_tag='REPORT-001', name='Test router', status='maintenance'
        )

    def test_staff_report_renders_correct_period_and_counts(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('reports'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['period'], '30')
        self.assertEqual(response.context['ticket_count'], 1)
        self.assertEqual(response.context['active_count'], 1)
        self.assertEqual(response.context['overdue_count'], 1)
        self.assertEqual(response.context['unassigned_count'], 1)
        self.assertEqual(response.context['completed_count'], 0)
        self.assertEqual(response.context['asset_total'], 1)
        self.assertContains(response, 'Operations reports')
        self.assertContains(response, 'Export ticket CSV')
        self.assertContains(response, 'Tickets by priority')
        self.assertContains(response, 'status-maintenance')

    def test_period_filter_and_invalid_values(self):
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.get(reverse('reports'), {'period': 'all'}).context['ticket_count'], 2
        )
        self.assertEqual(
            self.client.get(reverse('reports'), {'period': '90'}).context['ticket_count'], 1
        )
        response = self.client.get(reverse('reports'), {'period': 'malicious'})
        self.assertEqual(response.context['period'], '30')
        self.assertEqual(response.context['ticket_count'], 1)

    def test_export_is_staff_only_and_does_not_leak_descriptions(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('reports_export'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/csv', response['Content-Type'])
        self.assertIn('attachment;', response['Content-Disposition'])
        self.assertEqual(response['Cache-Control'], 'no-store')
        csv_text = response.content.decode('utf-8-sig')
        self.assertNotIn('Sensitive description not for export', csv_text)
        self.assertNotIn('Old closed request', csv_text)
        rows = list(csv.reader(StringIO(csv_text)))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0][0], 'Ticket ID')
        self.assertTrue(rows[1][1].startswith("'=HYPERLINK"))
        self.assertEqual(rows[1][2], "'+Network")
        self.assertEqual(rows[1][-1], 'Yes')
        self.assertEqual(len(rows[1]), len(rows[0]))
        all_rows = list(csv.reader(StringIO(
            self.client.get(reverse('reports_export'), {'period': 'all'})
            .content.decode('utf-8-sig')
        )))
        self.assertEqual(len(all_rows), 3)

    def test_nonstaff_and_anonymous_cannot_access_reports_or_export(self):
        for user in (None, self.employee):
            if user:
                self.client.force_login(user)
            else:
                self.client.logout()
            for name in ('reports', 'reports_export'):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 302)
                self.assertIn('/login/', response['Location'])
            if user:
                self.assertNotContains(
                    self.client.get(reverse('dashboard')), 'Operations reports'
                )

    def test_export_rejects_post_even_for_staff(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.post(reverse('reports_export'), {}).status_code, 405)

    def test_formula_prefixes_with_leading_whitespace_are_neutralized(self):
        for unsafe in ('=1+1', '+2', '-3', '@SUM(1)', '  =cmd', '\t=cmd', '\r@cmd', '\n+cmd'):
            self.assertTrue(csv_safe(unsafe).startswith("'"), unsafe)
        self.assertEqual(csv_safe('Helpdesk request'), 'Helpdesk request')

    @override_settings(DEMO_MODE=True, DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_public_demo_cannot_access_reporting(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get('/reports/').status_code, 404)
        self.assertEqual(self.client.get('/reports/export.csv').status_code, 404)
        self.assertEqual(self.client.post('/reports/export.csv').status_code, 404)
