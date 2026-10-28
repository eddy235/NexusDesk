"""Business-hour SLA calculations and idempotent escalation checks.

Schedules use Django's configured timezone; v0.4 supports a single daily work
window Monday–Friday (no holiday calendar or overnight shifts).
"""
from datetime import datetime, timedelta, time
from django.utils import timezone


def business_deadline(start, hours, open_hour=9, close_hour=17):
    if not (0 <= open_hour < close_hour <= 24):
        raise ValueError("Invalid business hours")
    if hours <= 0:
        raise ValueError("SLA hours must be positive")
    tz = timezone.get_current_timezone()
    current = timezone.localtime(start, tz)
    remaining = timedelta(hours=hours)
    while remaining > timedelta(0):
        day_start = timezone.make_aware(
            datetime.combine(current.date(), time(open_hour)), tz)
        day_end = timezone.make_aware(
            datetime.combine(current.date(), time(close_hour % 24)), tz)
        if close_hour == 24:
            day_end += timedelta(days=1)
        if current.weekday() >= 5 or current >= day_end:
            current = day_start + timedelta(days=1)
            continue
        if current < day_start:
            current = day_start
        available = day_end - current
        amount = min(remaining, available)
        current += amount
        remaining -= amount
        if remaining and current >= day_end:
            current = day_start + timedelta(days=1)
    return current.astimezone(start.tzinfo)


def apply_sla(ticket):
    """Assign a deadline when the ticket matches an enabled priority policy."""
    from .models import SLAPolicy
    policy = SLAPolicy.objects.filter(
        priority=ticket.priority, enabled=True).first()
    if policy and ticket.due_at is None:
        ticket.due_at = business_deadline(
            ticket.created_at or timezone.now(), policy.resolution_hours,
            policy.open_hour, policy.close_hour)
        ticket.save(update_fields=['due_at', 'updated_at'])
    return policy


def record_escalations(now=None):
    """Idempotent audit events for overdue active tickets, no notifications."""
    from .models import Ticket, TicketEvent
    from django.db import transaction
    now = now or timezone.now()
    changed = 0
    with transaction.atomic():
        tickets = Ticket.objects.select_for_update().filter(
            status__in=['open', 'in_progress'], due_at__lt=now,
            sla_escalated_at__isnull=True)
        for ticket in tickets:
            ticket.sla_escalated_at = now
            ticket.save(update_fields=['sla_escalated_at', 'updated_at'])
            TicketEvent.objects.create(
                ticket=ticket, event='SLA deadline breached — review required')
            changed += 1
    return changed
