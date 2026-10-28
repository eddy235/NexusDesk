from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Ticket, Asset, TicketComment
User=get_user_model()
class AccessTests(TestCase):
    def setUp(self):
        self.employee=User.objects.create_user('employee',password='strong-example-password-123')
        self.other=User.objects.create_user('other',password='strong-example-password-123')
        self.tech=User.objects.create_user('technician',password='strong-example-password-123',is_staff=True)
        self.ticket=Ticket.objects.create(title='Printer broken',description='Printer not working',reporter=self.other,priority='high')
        self.asset=Asset.objects.create(asset_tag='LAP-001',name='Staff laptop',assigned_to=self.other)
    def test_login_required(self):
        self.assertEqual(self.client.get(reverse('dashboard')).status_code,302)
    def test_employee_cannot_view_other_ticket(self):
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(reverse('ticket_detail',args=[self.ticket.pk])).status_code,404)
        self.assertNotContains(self.client.get(reverse('ticket_list')),'Printer broken')
    def test_employee_cannot_change_status(self):
        self.client.force_login(self.other)
        self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'update','status':'closed'})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status,'open')
    def test_employee_cannot_register_assets(self):
        self.client.force_login(self.employee)
        self.assertEqual(self.client.get(reverse('asset_create')).status_code,302)
        self.assertNotContains(self.client.get(reverse('asset_list')),'LAP-001')
    def test_employee_can_create_ticket(self):
        self.client.force_login(self.employee)
        response=self.client.post(reverse('ticket_create'),{'title':'Laptop issue','description':'Keyboard faulty','category':'Hardware','priority':'medium'})
        self.assertEqual(response.status_code,302)
        self.assertTrue(Ticket.objects.filter(reporter=self.employee,title='Laptop issue').exists())
    def test_technician_can_update_ticket(self):
        self.client.force_login(self.tech)
        response=self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'update','status':'resolved','assigned_to':self.tech.pk,'due_at':''})
        self.assertEqual(response.status_code,302)
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status,'resolved')
        self.assertEqual(self.ticket.events.count(),1)
    def test_overdue_calculated(self):
        self.ticket.due_at=timezone.now()-timedelta(hours=2)
        self.assertTrue(self.ticket.overdue)
        self.ticket.status='closed'
        self.assertFalse(self.ticket.overdue)

    def test_reporter_can_comment_and_event_logged(self):
        self.client.force_login(self.other)
        response=self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'comment','body':'Printer needs servicing'})
        self.assertEqual(response.status_code,302)
        self.assertTrue(TicketComment.objects.filter(ticket=self.ticket,author=self.other,body='Printer needs servicing').exists())
        self.assertTrue(self.ticket.events.filter(event='Comment added').exists())

    def test_other_employee_cannot_comment_on_hidden_ticket(self):
        self.client.force_login(self.employee)
        response=self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'comment','body':'Unauthorized'})
        self.assertEqual(response.status_code,404)
        self.assertEqual(TicketComment.objects.count(),0)

    def test_employee_cannot_assign_ticket(self):
        self.client.force_login(self.other)
        self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'update','status':'resolved','assigned_to':self.tech.pk,'due_at':''})
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status,'open')
        self.assertIsNone(self.ticket.assigned_to)

    def test_search_respects_ticket_access(self):
        Ticket.objects.create(title='Private network outage',description='Secret description',reporter=self.employee)
        self.client.force_login(self.other)
        page=self.client.get(reverse('ticket_list'),{'q':'network'})
        self.assertNotContains(page,'Private network outage')
        self.assertNotContains(page,'Secret description')

    def test_priority_and_status_filter(self):
        self.client.force_login(self.tech)
        page=self.client.get(reverse('ticket_list'),{'priority':'high','status':'open','q':'Printer'})
        self.assertContains(page,'Printer broken')
        page=self.client.get(reverse('ticket_list'),{'priority':'low'})
        self.assertNotContains(page,'Printer broken')

    def test_comment_empty_or_too_long_rejected(self):
        self.client.force_login(self.other)
        for body in ['', 'x'*2001]:
            result=self.client.post(reverse('ticket_detail',args=[self.ticket.pk]),{'action':'comment','body':body})
            self.assertEqual(result.status_code,200)
        self.assertFalse(TicketComment.objects.exists())
