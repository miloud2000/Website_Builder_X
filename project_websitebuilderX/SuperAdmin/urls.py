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
    path('administrateur/update/<int:pk>/', views.updateAdministrateur, name='updateAdministrateur'),
    path('administrateur/delete/<int:pk>/', views.deleteAdministrateur, name='deleteAdministrateur'),
    
    
    path('administrateurs/export/csv/', views.export_admins_csv, name='export_admins_csv'),
    path('administrateurs/export/excel/', views.export_admins_excel, name='export_admins_excel'),
    path('administrateurs/export/pdf/', views.export_admins_pdf, name='export_admins_pdf'),



    path('GestionnaireComptesSuperAdmin/',views.GestionnaireComptesSuperAdmin, name="GestionnaireComptesSuperAdmin"), 
    path('addGestionnaireComptes/',views.addGestionnaireComptes, name="addGestionnaireComptes"), 
    path('gestionnaire/update/<int:pk>/', views.updateGestionnaireComptes, name='updateGestionnaireComptes'),
    
        
    path('SupportTechniqueSuperAdmin/',views.SupportTechniqueSuperAdmin, name="SupportTechniqueSuperAdmin"), 
    path('addSupportTechnique/',views.addSupportTechnique, name="addSupportTechnique"), 
    path('support/update/<int:pk>/', views.updateSupportTechnique, name='updateSupportTechnique'),
    path('support/delete/<int:pk>/', views.deleteSupportTechnique, name='deleteSupportTechnique'),
    path('gestionnaire/delete/<int:pk>/', views.deleteGestionnaireComptes, name='deleteGestionnaireComptes'),
    
    
    path('ClienteSuperAdmin/', views.ClienteSuperAdmin, name='ClienteSuperAdmin'),
    path('addCliente/',views.addCliente, name="addCliente"), 
    path('cliente/update/<int:pk>/', views.updateCliente, name='updateCliente'),
    path('cliente/delete/<int:pk>/', views.deleteCliente, name='deleteCliente'),
    path('commercial/delete/<int:pk>/', views.deleteCommercial, name='deleteCommercial'),
    
    
    path('CommercialSuperAdmin/', views.CommercialSuperAdmin, name='CommercialSuperAdmin'),
    path('add-commercial/', views.addCommercial, name='addCommercial'),
    path('commercial/update/<int:pk>/', views.updateCommercial, name='updateCommercial'),

    
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