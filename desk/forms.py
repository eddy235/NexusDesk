from django import forms
from .models import Ticket,Asset
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
        fields=['name','asset_tag','asset_type','serial_number','location','assigned_to','notes']
