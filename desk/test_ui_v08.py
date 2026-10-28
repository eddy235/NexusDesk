"""Render and access regression tests for the NexusDesk v0.8 UI overhaul."""
from django.contrib.auth import get_user_model
from django.test import TestCase, SimpleTestCase, override_settings
from django.urls import reverse
from desk.models import Ticket, Asset

User = get_user_model()


class InternalInterfaceTests(TestCase):
    def setUp(self):
        self.employee = User.objects.create_user('design_employee', password='test-example-strong-pass')
        self.staff = User.objects.create_user('design_staff', password='test-example-strong-pass', is_staff=True)
        self.ticket = Ticket.objects.create(
            title='Test workstation problem', description='Keyboard issue',
            reporter=self.employee, priority='high'
        )
        self.asset = Asset.objects.create(
            asset_tag='UI-008', name='Design laptop', status='assigned',
            assigned_to=self.employee
        )

    def test_dashboard_uses_new_layout_and_cards(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Workspace overview')
        self.assertContains(response, 'metrics-secondary')
        self.assertContains(response, 'NexusDesk')
        self.assertContains(response, 'Test workstation problem')
        self.assertContains(response, 'aria-current="page"')

    def test_tickets_and_asset_pages_show_new_status_pills(self):
        self.client.force_login(self.employee)
        tickets = self.client.get(reverse('ticket_list'))
        self.assertContains(tickets, 'status-high')
        self.assertContains(tickets, 'status-open')
        assets = self.client.get(reverse('asset_list'))
        self.assertContains(assets, 'status-assigned')
        self.assertContains(assets, 'Design laptop')

    def test_ticket_discussion_and_staff_controls_preserved(self):
        self.client.force_login(self.employee)
        response = self.client.get(reverse('ticket_detail', args=[self.ticket.pk]))
        self.assertContains(response, 'Post comment')
        self.assertNotContains(response, 'Technician controls')
        self.client.force_login(self.staff)
        response = self.client.get(reverse('ticket_detail', args=[self.ticket.pk]))
        self.assertContains(response, 'Technician controls')
        self.assertContains(response, 'Update ticket')

    def test_login_page_does_not_display_private_navigation(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome back')
        self.assertNotContains(response, 'Asset inventory')


@override_settings(DEMO_MODE=True, DEBUG=False, SECURE_SSL_REDIRECT=False)
class PublicInterfaceTests(SimpleTestCase):
    def test_demo_retains_fictional_disclaimer_and_filters(self):
        response = self.client.get('/demo/')
        self.assertEqual(response.status_code, 200)
        for text in ('SYNTHETIC DATA ONLY', 'Filter examples',
                     'Every displayed ticket, asset, figure and team is fictional',
                     'Asset lifecycle', 'status-open', 'status-overdue'):
            self.assertContains(response, text)
        self.assertNotContains(response, 'Sign out')

    def test_demo_still_blocks_authenticated_workflows(self):
        self.assertEqual(self.client.get('/login/').status_code, 404)
        self.assertEqual(self.client.post('/tickets/new/', {}).status_code, 404)
