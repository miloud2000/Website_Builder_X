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
    path('administrateurs/<int:admin_id>/historique/', views.historique_administrateur, name='historique_administrateur'),
    path('administrateurs/<int:admin_id>/historique/pdf/', views.export_historique_pdf, name='export_historique_pdf'),


    path('GestionnaireComptesSuperAdmin/',views.GestionnaireComptesSuperAdmin, name="GestionnaireComptesSuperAdmin"), 
    path('addGestionnaireComptes/',views.addGestionnaireComptes, name="addGestionnaireComptes"), 
    path('gestionnaire/update/<int:pk>/', views.updateGestionnaireComptes, name='updateGestionnaireComptes'),
    path('gestionnaire/delete/<int:pk>/', views.deleteGestionnaireComptes, name='deleteGestionnaireComptes'),
    path('gestionnaires/export/csv/', views.export_gestionnaire_csv, name='export_gestionnaire_csv'),
    path('gestionnaires/export/excel/', views.export_gestionnaire_excel, name='export_gestionnaire_excel'),
    path('gestionnaires/export/pdf/', views.export_gestionnaire_pdf, name='export_gestionnaire_pdf'),
    
        
    path('SupportTechniqueSuperAdmin/',views.SupportTechniqueSuperAdmin, name="SupportTechniqueSuperAdmin"), 
    path('addSupportTechnique/',views.addSupportTechnique, name="addSupportTechnique"), 
    path('support/update/<int:pk>/', views.updateSupportTechnique, name='updateSupportTechnique'),
    path('support/delete/<int:pk>/', views.deleteSupportTechnique, name='deleteSupportTechnique'),
    path('support/export/csv/', views.export_support_csv, name='export_support_csv'),
    path('support/export/excel/', views.export_support_excel, name='export_support_excel'),
    path('support/export/pdf/', views.export_support_pdf, name='export_support_pdf'),

    
    
    
    path('ClienteSuperAdmin/', views.ClienteSuperAdmin, name='ClienteSuperAdmin'),
    path('addCliente/',views.addCliente, name="addCliente"), 
    path('cliente/update/<int:pk>/', views.updateCliente, name='updateCliente'),
    path('cliente/delete/<int:pk>/', views.deleteCliente, name='deleteCliente'),
    path('clientes/export/csv/', views.export_clientes_csv, name='export_clientes_csv'),
    path('clientes/export/excel/', views.export_clientes_excel, name='export_clientes_excel'),
    path('clientes/export/pdf/', views.export_clientes_pdf, name='export_clientes_pdf'),
    path('clientes/<int:cliente_id>/activites/', views.cliente_activity_dashboard, name='cliente_activity_dashboard'),


    
    path('commercial/delete/<int:pk>/', views.deleteCommercial, name='deleteCommercial'),
    path('CommercialSuperAdmin/', views.CommercialSuperAdmin, name='CommercialSuperAdmin'),
    path('add-commercial/', views.addCommercial, name='addCommercial'),
    path('commercial/update/<int:pk>/', views.updateCommercial, name='updateCommercial'),
    path('commercial/export/csv/', views.export_commercials_csv, name='export_commercials_csv'),
    path('commercial/export/pdf/', views.export_commercials_pdf, name='export_commercials_pdf'),
    path('commercial/export/excel/', views.export_commercials_excel, name='export_commercials_excel'),

    path('demandes-recharger/', views.all_demandes_recharger, name='all_demandes_recharger'),
    path('demandes/export/pdf/', views.export_demandes_pdf, name='export_demandes_pdf'),
    # path('demandes/export/csv/', views.export_demandes_csv, name='export_demandes_csv'),
    path('demandes/export/excel/', views.export_demandes_excel, name='export_demandes_excel'),

    path('full_size_image_Super_Admin/<int:traceDemandeRecharger_id>/',views.full_size_image_Super_Admin, name="full_size_image_Super_Admin"), 
    path('gestionnaire/<int:gestionnaire_id>/', views.gestionnaire_detail, name='gestionnaire_detail'),


    path('traceDemandeRechargerDone/',views.traceDemandeRechargerDone, name="traceDemandeRechargerDone"), 
    path('traceDemandeRechargerInacceptable/',views.traceDemandeRechargerInacceptable, name="traceDemandeRechargerInacceptable"), 


    path('DemandeRechargerNotDone/',views.DemandeRechargerNotDone, name="DemandeRechargerNotDone"), 
    path('full_size_image_NotDone_Super_Admin/<int:DemandeRecharger_id>/',views.full_size_image_NotDone_Super_Admin, name="full_size_image_NotDone_Super_Admin"), 


    path('DemandeSupportAll/',views.DemandeSupportAll, name="DemandeSupportAll"), 
    path('export-demande-support/<str:format>/', views.export_demande_support_filtered, name='export_demande_support_filtered'),

    path('DemandeSupportDoneSA/',views.DemandeSupportDoneSA, name="DemandeSupportDoneSA"), 
    path('DemandeSupportNotDoneyetSA/',views.DemandeSupportNotDoneyetSA, name="DemandeSupportNotDoneyetSA"), 

    
    path('history/', views.history, name='history'),
    path('history/export/pdf/', views.export_history_pdf, name='export_history_pdf'),
    path('history/export/excel/', views.export_history_excel, name='export_history_excel'),

    
    path('SuperAdmin/websites/', views.WebsitesListSuperAdmin, name='websites_list_superadmin'),
    path('SuperAdmin/websites/add/', views.add_website, name='add_website'),
    path('SuperAdmin/websites/<int:id>/', views.website_details, name='website_details'),
    path('SuperAdmin/websites/<int:id>/edit/', views.edit_website, name='edit_website'),
    path('SuperAdmin/websites/<int:id>/hide/', views.hide_website, name='hide_website'),


    path('SuperAdmin/supports/', views.supports_list_superadmin, name='supports_list_superadmin'),
    path('SuperAdmin/supports/add/', views.add_support, name='add_support'),
    path('SuperAdmin/supports/<int:id>/', views.support_details, name='support_details'),
    path('SuperAdmin/supports/<int:id>/edit/', views.edit_support, name='edit_support'),
    path('SuperAdmin/supports/<int:id>/hide/', views.hide_support, name='hide_support'),
    path('SuperAdmin/tickets/', views.tickets_list, name='tickets_list'),
    path('SuperAdmin/tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:ticket_id>/pdf/', views.ticket_pdf, name='ticket_pdf'),







    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)