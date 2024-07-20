from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    #SupportTechnique
    
    # path('homeSupportTechnique/',views.homeSupportTechnique, name="homeSupportTechnique"), 
    path('dashbordHomeSupportTechnique/',views.dashbordHomeSupportTechnique, name="dashbordHomeSupportTechnique"), 
    
    path('confirm_consome_support/',views.confirm_consome_support, name="confirm_consome_support"), 
    path('consome-support/<int:demande_support_id>/', views.consome_support, name='consome_support'),
    
    path('DemandeSupportDone/',views.DemandeSupportDone, name="DemandeSupportDone"), 
    path('DemandeSupportNotDoneyet/',views.DemandeSupportNotDoneyet, name="DemandeSupportNotDoneyet"), 
    

    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)