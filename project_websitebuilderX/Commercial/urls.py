from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    #Commercial
    
    path('dashbordHomeCommercial/',views.dashbordHomeCommercial, name="dashbordHomeCommercial"), 
    path('ClienteCommercial/',views.ClienteCommercial, name="ClienteCommercial"), 
    path('addCliente_c/',views.addCliente_c, name="addCliente_c"), 


    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)