from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    #Commercial
    path('dashbordHomeCommercial/',views.dashbordHomeCommercial, name="dashbordHomeCommercial"), 
    path('ClienteCommercial/',views.ClienteCommercial, name="ClienteCommercial"), 
    path('addCliente_c/',views.addCliente_c, name="addCliente_c"), 
    path('commercial/cliente/update/<int:cliente_id>/', views.updateCliente_c, name='updateCliente_c'),
    path('commercial/cliente/delete/<int:cliente_id>/', views.deleteCliente_c, name='deleteCliente_c'),
    path('list_websites_c/',views.list_websites_c, name="list_websites_c"), 
    path('detail_website_c/<str:slugWebsites>/',views.detail_website_c, name="detail_website_c"),
     
    path('details_website_commercial/<int:id>/', views.details_website_commercial, name='details_website_commercial'),

    path('all_list_websites_c/',views.all_list_websites_c, name="all_list_websites_c"), 

    path('supports_list_commercial/',views.supports_list_commercial, name="supports_list_commercial"), 
    path('details_support_commercial/<int:id>/', views.details_support_commercial, name='details_support_commercial'),





    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)