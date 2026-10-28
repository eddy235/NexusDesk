from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from desk.models import SLAPolicy, Ticket, TicketEvent
from desk.sla import business_deadline

User = get_user_model()

class SLATests(TestCase):
    def setUp(self):
        self.person = User.objects.create_user('slaemployee', password='test-pass-123456xyz')
        self.policy = SLAPolicy.objects.create(priority='high', resolution_hours=4,
                                                open_hour=9, close_hour=17)

    def test_business_hours_roll_across_weekend(self):
        start = datetime(2026, 10, 30, 16, 0, tzinfo=ZoneInfo('UTC'))
        self.assertEqual(
            business_deadline(start, 4),
            datetime(2026, 11, 2, 12, 0, tzinfo=ZoneInfo('UTC'))
        )

    def test_ticket_creation_applies_matching_policy(self):
        self.client.force_login(self.person)
        response = self.client.post('/tickets/new/', {
            'title': 'Internet down', 'description': 'Connectivity outage',
            'category': 'Network', 'priority': 'high'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIsNotNone(Ticket.objects.get(title='Internet down').due_at)

    def test_missing_policy_leaves_deadline_unset(self):
        self.client.force_login(self.person)
        response = self.client.post('/tickets/new/', {
            'title': 'Small request', 'description': 'Mouse replacement',
            'category': 'Hardware', 'priority': 'low'
        })
        self.assertEqual(response.status_code, 302)
        self.assertIsNone(Ticket.objects.get(title='Small request').due_at)

    def test_escalation_command_is_repeat_safe(self):
        ticket = Ticket.objects.create(title='Late', description='Late work',
                                       reporter=self.person, priority='high',
                                       due_at=timezone.now()-timedelta(hours=3))
        call_command('check_sla')
        ticket.refresh_from_db()
        self.assertIsNotNone(ticket.sla_escalated_at)
        call_command('check_sla')
        self.assertEqual(TicketEvent.objects.filter(
            ticket=ticket, event__contains='breached').count(), 1)

    def test_resolved_ticket_does_not_escalate(self):
        ticket = Ticket.objects.create(title='Finished', description='Done',
                                       reporter=self.person, status='resolved',
                                       due_at=timezone.now()-timedelta(hours=3))
        call_command('check_sla')
        ticket.refresh_from_db()
        self.assertIsNone(ticket.sla_escalated_at)

    def test_policy_validation(self):
        from django.core.exceptions import ValidationError
        self.policy.open_hour=18
        self.policy.close_hour=9
        with self.assertRaises(ValidationError):
            self.policy.full_clean()
