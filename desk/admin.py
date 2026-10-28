"""Administrative configuration for internal support workflows."""
from django.contrib import admin

from .models import Asset, AssetEvent, SLAPolicy, Ticket, TicketEvent


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'priority', 'status', 'reporter', 'assigned_to', 'due_at']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description', 'reporter__username']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'assigned_to':
            from django.contrib.auth import get_user_model
            kwargs['queryset'] = get_user_model().objects.filter(
                is_active=True, is_staff=True
            ).order_by('username')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['asset_tag', 'name', 'asset_type', 'status', 'assigned_to']
    list_filter = ['status', 'asset_type']
    search_fields = ['asset_tag', 'name', 'serial_number']


class ReadOnlyEventAdmin(admin.ModelAdmin):
    """Activity logs can be inspected but not manually rewritten in admin."""
    def has_view_permission(self, request, obj=None):
        return request.user.is_active and request.user.is_staff

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TicketEvent)
class TicketEventAdmin(ReadOnlyEventAdmin):
    list_display = ['ticket', 'actor', 'event', 'created_at']
    search_fields = ['ticket__title', 'event']
    list_select_related = ['ticket', 'actor']


@admin.register(AssetEvent)
class AssetEventAdmin(ReadOnlyEventAdmin):
    list_display = ['asset', 'actor', 'event', 'created_at']
    search_fields = ['asset__asset_tag', 'event']
    list_select_related = ['asset', 'actor']


@admin.register(SLAPolicy)
class SLAPolicyAdmin(admin.ModelAdmin):
    list_display = ('priority', 'resolution_hours', 'open_hour', 'close_hour', 'enabled')
    list_editable = ('enabled',)
