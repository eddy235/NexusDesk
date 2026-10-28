from django import forms
from .models import Ticket,Asset,TicketComment
class TicketForm(forms.ModelForm):
    class Meta:
        model=Ticket
        fields=['title','description','category','priority']
        widgets={'description':forms.Textarea(attrs={'rows':5})}
class TicketUpdateForm(forms.ModelForm):
    class Meta:
        model=Ticket
        fields=['status','assigned_to','due_at']
        widgets={'due_at':forms.DateTimeInput(attrs={'type':'datetime-local'})}
class AssetForm(forms.ModelForm):
    class Meta:
        model=Asset
        fields=['name','asset_tag','asset_type','status','serial_number','location','assigned_to','notes']

class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['body']
        widgets = {'body': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add an update for everyone on this ticket'})}
        labels = {'body': 'Comment'}
