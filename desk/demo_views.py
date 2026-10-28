"""Synthetic, database-independent portfolio demonstration views."""
from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render


# All records below are fictional. This module must never query the live models.
SAMPLE_TICKETS = (
    ('ND-1042', 'Laptop VPN connection intermittent', 'High', 'In progress', 'Support Team', 'Due soon'),
    ('ND-1041', 'New starter workstation setup', 'Medium', 'Open', 'Unassigned', 'On track'),
    ('ND-1040', 'Printer queue stuck on second floor', 'Low', 'Open', 'Helpdesk', 'On track'),
    ('ND-1039', 'Wi-Fi access point needs review', 'Critical', 'In progress', 'Network Team', 'Overdue'),
    ('ND-1038', 'Email client authentication failure', 'High', 'Open', 'Support Team', 'Overdue'),
    ('ND-1037', 'Replacement keyboard request', 'Low', 'Resolved', 'Helpdesk', 'Complete'),
    ('ND-1036', 'Shared drive permission review', 'Medium', 'In progress', 'Helpdesk', 'On track'),
    ('ND-1035', 'Asset handover for design team', 'Medium', 'Open', 'Unassigned', 'On track'),
    ('ND-1034', 'Endpoint agent update required', 'High', 'In progress', 'Support Team', 'Due soon'),
    ('ND-1033', 'Password reset for demo account', 'Low', 'Resolved', 'Helpdesk', 'Complete'),
    ('ND-1032', 'Meeting room display offline', 'Medium', 'Open', 'Helpdesk', 'On track'),
    ('ND-1031', 'Network switch port diagnostics', 'High', 'In progress', 'Network Team', 'On track'),
)
SAMPLE_ASSETS = (
    ('LAP-001', 'Staff laptop', 'Assigned', 'Workstations'),
    ('NET-014', 'Wireless access point', 'Maintenance', 'Networking'),
    ('MON-022', 'External display', 'Available', 'Accessories'),
    ('LAP-003', 'Loan laptop', 'Available', 'Workstations'),
    ('PRN-011', 'Office laser printer', 'Assigned', 'Printing'),
    ('NET-020', 'Legacy switch', 'Retired', 'Networking'),
    ('DES-005', 'Reception workstation', 'Assigned', 'Workstations'),
)


def health(request):
    return JsonResponse({'status': 'ok', 'demo_mode': settings.DEMO_MODE})


def public_demo(request):
    if not settings.DEMO_MODE:
        raise Http404

    all_tickets = [
        dict(zip(('code', 'title', 'priority', 'status', 'owner', 'deadline'), row))
        for row in SAMPLE_TICKETS
    ]
    all_assets = [
        dict(zip(('tag', 'name', 'state', 'type'), row))
        for row in SAMPLE_ASSETS
    ]
    query = request.GET.get('q', '').strip()[:80]
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    asset_state = request.GET.get('asset_state', '')
    allowed_status = ('Open', 'In progress', 'Resolved')
    allowed_priority = ('Low', 'Medium', 'High', 'Critical')
    allowed_asset_states = ('Available', 'Assigned', 'Maintenance', 'Retired')
    status = status if status in allowed_status else ''
    priority = priority if priority in allowed_priority else ''
    asset_state = asset_state if asset_state in allowed_asset_states else ''
    tickets = [
        ticket for ticket in all_tickets
        if (not query or query.casefold() in
            (ticket['code'] + ' ' + ticket['title'] + ' ' + ticket['owner']).casefold())
        and (not status or ticket['status'] == status)
        and (not priority or ticket['priority'] == priority)
    ]
    assets = [asset for asset in all_assets
              if not asset_state or asset['state'] == asset_state]

    stats = {
        'open': sum(t['status'] == 'Open' for t in all_tickets),
        'in_progress': sum(t['status'] == 'In progress' for t in all_tickets),
        'overdue': sum(t['deadline'] == 'Overdue' for t in all_tickets),
        'due_soon': sum(t['deadline'] == 'Due soon' for t in all_tickets),
        'assets': len(all_assets),
    }
    return render(request, 'desk/public_demo.html', {
        'stats': stats, 'tickets': tickets, 'assets': assets,
        'ticket_count': len(tickets), 'asset_count': len(assets),
        'query': query, 'selected_status': status,
        'selected_priority': priority, 'selected_asset_state': asset_state,
        'statuses': allowed_status, 'priorities': allowed_priority,
        'asset_states': allowed_asset_states,
    })
