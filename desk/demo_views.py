from django.conf import settings
from django.http import Http404, JsonResponse
from django.shortcuts import render


def health(request):
    return JsonResponse({'status': 'ok', 'demo_mode': settings.DEMO_MODE})


def public_demo(request):
    if not settings.DEMO_MODE:
        raise Http404
    stats = {'open': 8, 'in_progress': 5, 'overdue': 2, 'assets': 37}
    tickets = [
        {'code': 'ND-1042', 'title': 'Laptop VPN connection intermittent', 'priority': 'High', 'status': 'In progress', 'owner': 'Support Team'},
        {'code': 'ND-1041', 'title': 'New starter workstation setup', 'priority': 'Medium', 'status': 'Open', 'owner': 'Unassigned'},
        {'code': 'ND-1040', 'title': 'Printer queue stuck on second floor', 'priority': 'Low', 'status': 'Open', 'owner': 'Helpdesk'},
        {'code': 'ND-1039', 'title': 'Wi-Fi access point needs review', 'priority': 'Critical', 'status': 'In progress', 'owner': 'Network Team'},
    ]
    assets = [
        {'tag': 'LAP-001', 'name': 'Staff Laptop', 'state': 'Assigned'},
        {'tag': 'NET-014', 'name': 'Wireless Access Point', 'state': 'Maintenance'},
        {'tag': 'MON-022', 'name': 'External Display', 'state': 'Available'},
    ]
    return render(request, 'desk/public_demo.html',
                  {'stats': stats, 'tickets': tickets, 'assets': assets})
