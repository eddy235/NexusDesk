from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Count,Q
from django.shortcuts import get_object_or_404,redirect,render
from django.utils import timezone
from .models import Ticket,Asset,TicketEvent,TicketComment
from .forms import TicketForm,TicketUpdateForm,AssetForm,TicketCommentForm

def is_staff(user):return user.is_authenticated and user.is_staff

def visible_tickets(user):
    qs=Ticket.objects.select_related('reporter','assigned_to')
    return qs if user.is_staff else qs.filter(Q(reporter=user)|Q(assigned_to=user))

@login_required
def dashboard(request):
    tickets=visible_tickets(request.user)
    counts={key:tickets.filter(status=key).count() for key,_ in Ticket.STATUS}
    overdue=tickets.exclude(status__in=['resolved','closed']).filter(due_at__lt=timezone.now()).count()
    return render(request,'desk/dashboard.html',{'counts':counts,'overdue':overdue,'recent':tickets.order_by('-created_at')[:6],'unassigned':tickets.filter(assigned_to__isnull=True).exclude(status__in=['resolved','closed']).count(),'assets_count':Asset.objects.count() if request.user.is_staff else Asset.objects.filter(assigned_to=request.user).count()})

@login_required
def ticket_list(request):
    tickets=visible_tickets(request.user).order_by('-created_at')
    status=request.GET.get('status','')
    if status in dict(Ticket.STATUS):tickets=tickets.filter(status=status)
    query=request.GET.get('q','').strip()[:120]
    priority=request.GET.get('priority','')
    if query:tickets=tickets.filter(Q(title__icontains=query)|Q(description__icontains=query)|Q(category__icontains=query))
    if priority in dict(Ticket.PRIORITY):tickets=tickets.filter(priority=priority)
    return render(request,'desk/tickets.html',{'tickets':tickets,'selected_status':status,'statuses':Ticket.STATUS,'selected_priority':priority,'priorities':Ticket.PRIORITY,'query':query})

@login_required
def ticket_create(request):
    form=TicketForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        ticket=form.save(commit=False);ticket.reporter=request.user;ticket.save()
        TicketEvent.objects.create(ticket=ticket,actor=request.user,event='Ticket created')
        messages.success(request,'Ticket submitted successfully.')
        return redirect('ticket_detail',pk=ticket.pk)
    return render(request,'desk/form.html',{'form':form,'heading':'New support ticket'})

@login_required
def ticket_detail(request,pk):
    ticket=get_object_or_404(visible_tickets(request.user),pk=pk)
    form=TicketUpdateForm(instance=ticket) if request.user.is_staff else None
    comment_form=TicketCommentForm()
    if request.method=='POST':
        action=request.POST.get('action')
        if action=='comment':
            comment_form=TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment=comment_form.save(commit=False)
                comment.ticket=ticket
                comment.author=request.user
                comment.save()
                TicketEvent.objects.create(ticket=ticket,actor=request.user,event='Comment added')
                messages.success(request,'Comment added.')
                return redirect('ticket_detail',pk=pk)
        elif action=='update' and request.user.is_staff:
            old=(ticket.status,ticket.assigned_to_id,ticket.due_at)
            form=TicketUpdateForm(request.POST,instance=ticket)
            if form.is_valid():
                changed=form.save()
                if old!=(changed.status,changed.assigned_to_id,changed.due_at):
                    TicketEvent.objects.create(ticket=changed,actor=request.user,event='Assignment, status or deadline updated')
                messages.success(request,'Ticket updated.')
                return redirect('ticket_detail',pk=pk)
        else:
            return redirect('ticket_detail',pk=pk)
    return render(request,'desk/ticket_detail.html',{'ticket':ticket,'form':form,'comment_form':comment_form})

@login_required
def asset_list(request):
    assets=Asset.objects.select_related('assigned_to')
    if not request.user.is_staff:assets=assets.filter(assigned_to=request.user)
    return render(request,'desk/assets.html',{'assets':assets.order_by('asset_tag')})

@user_passes_test(is_staff,login_url='login')
def asset_create(request):
    form=AssetForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        form.save();messages.success(request,'Asset registered.')
        return redirect('asset_list')
    return render(request,'desk/form.html',{'form':form,'heading':'Register IT asset'})
