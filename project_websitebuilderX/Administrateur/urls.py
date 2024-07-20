from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('dashbordHomeAdministrateur/',views.dashbordHomeAdministrateur, name="dashbordHomeAdministrateur"), 
    # path('homeAdministrateur/',views.homeAdministrateur, name="homeAdministrateur"), 

    
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)