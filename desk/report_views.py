"""Restricted reporting screens and data export for IT staff only."""
import csv

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET

from .reporting import get_report, report_period, report_tickets, csv_safe


def is_technician(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_technician, login_url='login')
@require_GET
def reports_overview(request):
    period = report_period(request.GET.get('period', '30'))
    context = get_report(period)
    return render(request, 'desk/reports.html', context)


@user_passes_test(is_technician, login_url='login')
@require_GET
def reports_export(request):
    period = report_period(request.GET.get('period', '30'))
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="nexusdesk-tickets-{period}.csv"'
    )
    response['Cache-Control'] = 'no-store'
    response.write('\ufeff')
    writer = csv.writer(response)
    writer.writerow([
        'Ticket ID', 'Title', 'Category', 'Priority', 'Status',
        'Assigned to', 'Created at', 'Due at', 'Overdue',
    ])
    tickets = report_tickets(period).order_by('created_at', 'pk')
    for ticket in tickets.iterator(chunk_size=500):
        writer.writerow([
            ticket.pk,
            csv_safe(ticket.title),
            csv_safe(ticket.category),
            ticket.get_priority_display(),
            ticket.get_status_display(),
            csv_safe(ticket.assigned_to.get_username() if ticket.assigned_to else 'Unassigned'),
            timezone.localtime(ticket.created_at).isoformat(timespec='minutes'),
            timezone.localtime(ticket.due_at).isoformat(timespec='minutes')
            if ticket.due_at else '',
            'Yes' if ticket.overdue else 'No',
        ])
    return response
