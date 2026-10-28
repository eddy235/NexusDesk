"""End-to-end workflow, CSRF, permissions and admin audit regressions for 1.0."""
from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import TicketUpdateForm
from .models import Asset, AssetEvent, Ticket, TicketEvent

User = get_user_model()


class ReleaseWorkflowTests(TestCase):
    def setUp(self):
        self.reporter = User.objects.create_user(
            'v1reporter', password='strong-example-12345'
        )
        self.other = User.objects.create_user(
            'v1other', password='strong-example-12345'
        )
        self.tech = User.objects.create_user(
            'v1technician', password='strong-example-12345', is_staff=True
        )
        self.inactive_tech = User.objects.create_user(
            'v1inactive', password='strong-example-12345',
            is_staff=True, is_active=False
        )

    def test_complete_reporter_to_technician_workflow(self):
        self.client.force_login(self.reporter)
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Employee laptop display issue',
            'description': 'External display is flickering',
            'category': 'Hardware',
            'priority': 'high',
        })
        self.assertEqual(response.status_code, 302)
        ticket = Ticket.objects.get(title='Employee laptop display issue')
        self.assertEqual(ticket.reporter, self.reporter)
        self.assertEqual(ticket.events.filter(event='Ticket created').count(), 1)

        response = self.client.post(reverse('ticket_detail', args=[ticket.pk]), {
            'action': 'comment',
            'body': 'The display cable was replaced without success.',
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ticket.comments.count(), 1)

        self.client.force_login(self.other)
        self.assertEqual(
            self.client.get(reverse('ticket_detail', args=[ticket.pk])).status_code,
            404
        )
        self.assertNotContains(
            self.client.get(reverse('ticket_list')), 'Employee laptop display issue'
        )

        self.client.force_login(self.tech)
        due_date = timezone.localtime(timezone.now() + timedelta(days=2))
        deadline = due_date.strftime('%Y-%m-%dT%H:%M')
        response = self.client.post(reverse('ticket_detail', args=[ticket.pk]), {
            'action': 'update',
            'status': 'in_progress',
            'assigned_to': self.tech.pk,
            'due_at': deadline,
        })
        self.assertEqual(response.status_code, 302)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'in_progress')
        self.assertEqual(ticket.assigned_to, self.tech)
        self.assertIsNotNone(ticket.due_at)
        self.assertTrue(
            ticket.events.filter(
                event='Assignment, status or deadline updated'
            ).exists()
        )
        edit_page = self.client.get(reverse('ticket_detail', args=[ticket.pk]))
        self.assertContains(edit_page, 'type="datetime-local"')
        self.assertContains(edit_page, 'value="' + deadline + '"')

        response = self.client.post(reverse('ticket_detail', args=[ticket.pk]), {
            'action': 'update',
            'status': 'resolved',
            'assigned_to': self.tech.pk,
            'due_at': deadline,
        })
        self.assertEqual(response.status_code, 302)
        ticket.refresh_from_db()
        self.assertEqual(ticket.status, 'resolved')
        self.assertFalse(ticket.overdue)

        report = self.client.get(reverse('reports'), {'period': 'all'})
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.context['completed_count'], 1)
        self.assertEqual(report.context['active_count'], 0)
        export = self.client.get(reverse('reports_export'), {'period': 'all'})
        self.assertIn('Employee laptop display issue', export.content.decode())

    def test_ticket_assignments_are_limited_to_active_technicians(self):
        ticket = Ticket.objects.create(
            title='Assignment policy check', description='Example',
            reporter=self.reporter
        )
        allowed = TicketUpdateForm(instance=ticket).fields['assigned_to'].queryset
        self.assertIn(self.tech, allowed)
        self.assertNotIn(self.reporter, allowed)
        self.assertNotIn(self.inactive_tech, allowed)

        self.client.force_login(self.tech)
        for invalid_user in (self.reporter, self.inactive_tech):
            response = self.client.post(
                reverse('ticket_detail', args=[ticket.pk]), {
                    'action': 'update', 'status': 'in_progress',
                    'assigned_to': invalid_user.pk, 'due_at': '',
                }
            )
            self.assertEqual(response.status_code, 200)
            ticket.refresh_from_db()
            self.assertIsNone(ticket.assigned_to)
            self.assertEqual(ticket.status, 'open')

    def test_all_write_actions_have_csrf_guard(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.reporter)
        uri = reverse('ticket_create')
        self.assertEqual(
            client.post(uri, {
                'title': 'Unauthorized write',
                'description': 'No CSRF submitted',
                'category': 'General',
                'priority': 'low',
            }).status_code,
            403
        )
        self.assertFalse(Ticket.objects.filter(title='Unauthorized write').exists())
        client.get(uri)
        token = client.cookies['csrftoken'].value
        self.assertEqual(
            client.post(uri, {
                'csrfmiddlewaretoken': token,
                'title': 'Authorized write',
                'description': 'Validated with CSRF token',
                'category': 'General',
                'priority': 'low',
            }).status_code,
            302
        )


class AuditAdminTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'v1admin', password='strong-example-12345'
        )
        self.request = RequestFactory().get('/admin/')
        self.request.user = self.superuser

    def test_activity_log_models_are_read_only_via_admin(self):
        for model in (TicketEvent, AssetEvent):
            handler = admin.site._registry[model]
            self.assertTrue(handler.has_view_permission(self.request))
            self.assertFalse(handler.has_add_permission(self.request))
            self.assertFalse(handler.has_change_permission(self.request))
            self.assertFalse(handler.has_delete_permission(self.request))

    def test_admin_restricts_ticket_assignees_to_active_staff(self):
        reporter = User.objects.create_user('regular_v1', password='strong-pass-12345')
        technician = User.objects.create_user(
            'active_v1tech', password='strong-pass-12345', is_staff=True
        )
        handler = admin.site._registry[Ticket]
        db_field = Ticket._meta.get_field('assigned_to')
        form_field = handler.formfield_for_foreignkey(db_field, self.request)
        self.assertIn(technician, form_field.queryset)
        self.assertNotIn(reporter, form_field.queryset)
