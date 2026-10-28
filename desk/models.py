from django.db import models
from django.conf import settings
from django.utils import timezone

class Ticket(models.Model):
    PRIORITY=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')]
    STATUS=[('open','Open'),('in_progress','In progress'),('resolved','Resolved'),('closed','Closed')]
    title=models.CharField(max_length=180)
    description=models.TextField(max_length=4000)
    category=models.CharField(max_length=90,default='General')
    priority=models.CharField(max_length=12,choices=PRIORITY,default='medium')
    status=models.CharField(max_length=14,choices=STATUS,default='open')
    reporter=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='reported_tickets')
    assigned_to=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,blank=True,null=True,related_name='assigned_tickets')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    due_at=models.DateTimeField(null=True,blank=True)
    @property
    def overdue(self):
        return self.due_at is not None and self.status not in ('resolved','closed') and self.due_at < timezone.now()
    def __str__(self):
        return f'#{self.pk} {self.title}'

class Asset(models.Model):
    TYPE=[('laptop','Laptop'),('desktop','Desktop'),('printer','Printer'),('network','Network'),('other','Other')]
    name=models.CharField(max_length=120)
    asset_tag=models.CharField(max_length=70,unique=True)
    asset_type=models.CharField(max_length=20,choices=TYPE,default='laptop')
    serial_number=models.CharField(max_length=100,blank=True)
    location=models.CharField(max_length=120,blank=True)
    assigned_to=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,blank=True)
    notes=models.TextField(blank=True,max_length=2000)
    created_at=models.DateTimeField(auto_now_add=True)
    def __str__(self):return f'{self.asset_tag} · {self.name}'

class TicketEvent(models.Model):
    ticket=models.ForeignKey(Ticket,on_delete=models.CASCADE,related_name='events')
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True)
    event=models.CharField(max_length=200)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering=['-created_at']

class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='ticket_comments')
    body = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at', 'id']

    def __str__(self):
        return f'Comment #{self.pk} on ticket #{self.ticket_id}'
