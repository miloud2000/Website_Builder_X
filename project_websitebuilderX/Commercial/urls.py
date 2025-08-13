from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    #Commercial
    
    path('dashbordHomeCommercial/',views.dashbordHomeCommercial, name="dashbordHomeCommercial"), 
    path('ClienteCommercial/',views.ClienteCommercial, name="ClienteCommercial"), 
    path('addCliente_c/',views.addCliente_c, name="addCliente_c"), 
    path('list_websites_c/',views.list_websites_c, name="list_websites_c"), 
    path('detail_website_c/<str:slugWebsites>/',views.detail_website_c, name="detail_website_c"), 
    path('all_list_websites_c/',views.all_list_websites_c, name="all_list_websites_c"), 





    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)