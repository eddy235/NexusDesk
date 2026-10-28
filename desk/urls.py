from django.urls import path
from . import views
urlpatterns=[path('',views.dashboard,name='dashboard'),path('tickets/',views.ticket_list,name='ticket_list'),path('tickets/new/',views.ticket_create,name='ticket_create'),path('tickets/<int:pk>/',views.ticket_detail,name='ticket_detail'),path('assets/',views.asset_list,name='asset_list'),path('assets/new/',views.asset_create,name='asset_create'),path('assets/<int:pk>/edit/',views.asset_update,name='asset_update')]
