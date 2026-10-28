"""Staff-only operational reporting helpers.

Reporting reflects the current database state, not historical conversion
rates. Period filters use ticket creation time; asset counts are always current.
"""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from .models import Ticket, Asset


REPORT_PERIODS = (
    ('7', 'Last 7 days'),
    ('30', 'Last 30 days'),
    ('90', 'Last 90 days'),
    ('all', 'All time'),
)


def report_period(value):
    return value if value in dict(REPORT_PERIODS) else '30'


def report_tickets(period):
    """Return tickets created within the selected calendar-day lookback."""
    tickets = Ticket.objects.select_related('assigned_to')
    if period != 'all':
        tickets = tickets.filter(
            created_at__gte=timezone.now() - timedelta(days=int(period))
        )
    return tickets


def _ordered_breakdown(queryset, field, choices):
    grouped = {
        row[field]: row['total']
        for row in queryset.values(field).annotate(total=Count('pk'))
    }
    return [
        {'value': value, 'label': label, 'count': grouped.get(value, 0)}
        for value, label in choices
    ]


def get_report(period):
    """Summaries for a technician; no claims about historical time-to-close."""
    qs = report_tickets(period)
    active = qs.exclude(status__in=('resolved', 'closed'))
    now = timezone.now()
    ticket_count = qs.count()
    statuses = _ordered_breakdown(qs, 'status', Ticket.STATUS)
    priorities = _ordered_breakdown(qs, 'priority', Ticket.PRIORITY)
    categories = list(
        qs.values('category').annotate(count=Count('pk'))
        .order_by('-count', 'category')[:6]
    )
    assets = _ordered_breakdown(Asset.objects.all(), 'status', Asset.STATE)
    return {
        'period': period,
        'periods': REPORT_PERIODS,
        'ticket_count': ticket_count,
        'active_count': active.count(),
        'completed_count': qs.filter(status__in=('resolved', 'closed')).count(),
        'overdue_count': active.filter(due_at__lt=now).count(),
        'unassigned_count': active.filter(assigned_to__isnull=True).count(),
        'escalated_count': active.filter(sla_escalated_at__isnull=False).count(),
        'statuses': statuses,
        'priorities': priorities,
        'categories': categories,
        'asset_total': Asset.objects.count(),
        'asset_states': assets,
        'chart_max': ticket_count or 1,
    }


def csv_safe(value):
    """Neutralize leading spreadsheet formula characters in untrusted data."""
    cell = '' if value is None else str(value)
    if cell.lstrip(' \t\r\n\ufeff\u200b').startswith(('=', '+', '-', '@')):
        return "'" + cell
    if cell.startswith(('\t', '\r', '\n')):
        return "'" + cell
    return cell
