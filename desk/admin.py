from django.contrib import admin
from .models import Ticket,Asset,TicketEvent
@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display=['id','title','priority','status','reporter','assigned_to','due_at']
    list_filter=['status','priority']
    search_fields=['title','description','reporter__username']
@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display=['asset_tag','name','asset_type','assigned_to']
    search_fields=['asset_tag','name','serial_number']
@admin.register(TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display=['ticket','actor','event','created_at']
    def has_add_permission(self,request):return False

from .models import SLAPolicy

@admin.register(SLAPolicy)
class SLAPolicyAdmin(admin.ModelAdmin):
    list_display = ('priority', 'resolution_hours', 'open_hour', 'close_hour', 'enabled')
    list_editable = ('enabled',)
