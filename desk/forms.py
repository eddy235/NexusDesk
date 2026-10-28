"""Forms for helpdesk and equipment management."""
from django import forms
from django.contrib.auth import get_user_model

from .models import Asset, Ticket, TicketComment


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'priority']
        widgets = {'description': forms.Textarea(attrs={'rows': 5})}


class TicketUpdateForm(forms.ModelForm):
    """Only active IT staff can be assigned to support tickets."""

    class Meta:
        model = Ticket
        fields = ['status', 'assigned_to', 'due_at']
        widgets = {
            'due_at': forms.DateTimeInput(
                format='%Y-%m-%dT%H:%M',
                attrs={'type': 'datetime-local'},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = (
            get_user_model().objects.filter(is_active=True, is_staff=True)
            .order_by('username')
        )
        self.fields['assigned_to'].help_text = (
            'Choose an active IT staff member, or leave unassigned.'
        )


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = [
            'name', 'asset_tag', 'asset_type', 'status',
            'serial_number', 'location', 'assigned_to', 'notes',
        ]


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Add an update for everyone on this ticket',
            }),
        }
        labels = {'body': 'Comment'}
