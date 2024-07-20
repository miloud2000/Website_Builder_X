from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('ticket_list/',views.ticket_list, name="ticket_list"), 
    path('get_branch_options/',views.get_branch_options, name='get_branch_options'),
    path('add_ticket/', views.add_ticket, name='add_ticket'),
    # path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('list_ticket_ST/',views.list_ticket_ST, name="list_ticket_ST"), 
    path('details_ticket_ST/<int:ticket_id>/',views.details_ticket_ST, name="details_ticket_ST"), 
    path('update_ticket_st/<int:ticket_id>/', views.update_ticket_st, name='update_ticket_st'),


    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
