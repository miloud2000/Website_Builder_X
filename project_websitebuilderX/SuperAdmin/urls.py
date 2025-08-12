from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    
    # path('',views.home2, name="home2"), 
    # path('home',views.home, name="home"), 

 
    # path('AllMergedWebsiteBuilder/', views.AllMergedWebsiteBuilder, name='AllMergedWebsiteBuilder'),
    path('AllWebsites_client_status/', views.AllWebsites_client_status, name='AllWebsites_client_status'),

    #SuperAdmin
    path('homeSuperAdmin/',views.homeSuperAdmin, name="homeSuperAdmin"), 
    path('dashbordHomeSuperAdmin/',views.dashbordHomeSuperAdmin, name="dashbordHomeSuperAdmin"),
    
    path('AdministrateurSuperAdmin/',views.AdministrateurSuperAdmin, name="AdministrateurSuperAdmin"), 
    path('addAdministrateur/',views.addAdministrateur, name="addAdministrateur"), 
    
    path('GestionnaireComptesSuperAdmin/',views.GestionnaireComptesSuperAdmin, name="GestionnaireComptesSuperAdmin"), 
    path('addGestionnaireComptes/',views.addGestionnaireComptes, name="addGestionnaireComptes"), 
        
    path('SupportTechniqueSuperAdmin/',views.SupportTechniqueSuperAdmin, name="SupportTechniqueSuperAdmin"), 
    path('addSupportTechnique/',views.addSupportTechnique, name="addSupportTechnique"), 
    
    
    path('ClienteSuperAdmin/', views.ClienteSuperAdmin, name='ClienteSuperAdmin'),
    path('addCliente/',views.addCliente, name="addCliente"), 
    
    
    path('CommercialSuperAdmin/', views.CommercialSuperAdmin, name='CommercialSuperAdmin'),
    path('add-commercial/', views.addCommercial, name='addCommercial'),

    
    path('traceDemandeRecharger/',views.traceDemandeRecharger, name="traceDemandeRecharger"), 
    path('full_size_image_Super_Admin/<int:traceDemandeRecharger_id>/',views.full_size_image_Super_Admin, name="full_size_image_Super_Admin"), 

    path('traceDemandeRechargerDone/',views.traceDemandeRechargerDone, name="traceDemandeRechargerDone"), 
    path('traceDemandeRechargerInacceptable/',views.traceDemandeRechargerInacceptable, name="traceDemandeRechargerInacceptable"), 


    path('DemandeRechargerNotDone/',views.DemandeRechargerNotDone, name="DemandeRechargerNotDone"), 
    path('full_size_image_NotDone_Super_Admin/<int:DemandeRecharger_id>/',views.full_size_image_NotDone_Super_Admin, name="full_size_image_NotDone_Super_Admin"), 


    path('DemandeSupportAll/',views.DemandeSupportAll, name="DemandeSupportAll"), 
    path('DemandeSupportDoneSA/',views.DemandeSupportDoneSA, name="DemandeSupportDoneSA"), 
    path('DemandeSupportNotDoneyetSA/',views.DemandeSupportNotDoneyetSA, name="DemandeSupportNotDoneyetSA"), 

    
    path('history/', views.history, name='history'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)