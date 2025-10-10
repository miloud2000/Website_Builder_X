from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    # path('',views.home2, name="home2"), 
    path('home',views.home, name="home"), 
    
    # path('ticket_list/',views.ticket_list, name="ticket_list"), 
    # path('get_priority_options/', views.get_priority_options, name='get_priority_options'),



    #Client
    path('dashboard/',views.dashboard, name="dashboard"), 
    path('',views.dashbordHome, name="dashbordHome"), 
    path('dashbordHome/',views.dashbordHome, name="dashbordHome"),
    path('editUser/',views.editUser, name="editUser"), 
    path('MesServices/',views.MesServices, name="MesServices"), 
    path('WebSites/',views.WebSites, name="WebSites"), 
    path('Services/',views.Services, name="Services"), 
    
    path('solde_et_facturation/',views.solde_et_facturation, name="solde_et_facturation"), 
    path('facturation_pdf/<int:facturation_id>/', views.generate_facturation_pdf, name='generate_facturation_pdf'),

    path('paiement/',views.paiement, name="paiement"), 
    # path('detail/',views.detail, name="detail"), 
    path('list_websites/',views.list_websites, name="list_websites"), 
    path('all_list_websites/',views.all_list_websites, name="all_list_websites"), 
    path('detail_website/<str:slugWebsites>/', views.detail_website, name="detail_website"),
    path('detail_support/<int:id>/', views.detail_support, name='detail_support'),

    path('list_services/',views.list_services, name="list_services"), 
    path('detailUser/',views.detailUser, name="detailUser"), 
    
    path('list_demande_recharger/', views.list_demande_recharger, name='list_demande_recharger'),
    path('create_demande_recharger/', views.create_demande_recharger, name='create_demande_recharger'),

    path('list_Demande_Recharger_En_attente/',views.list_Demande_Recharger_En_attente, name="list_Demande_Recharger_En_attente"), 
    path('list_Demande_Recharger_Complete/',views.list_Demande_Recharger_Complete, name="list_Demande_Recharger_Complete"), 
    path('list_Demande_Recharger_Annule/',views.list_Demande_Recharger_Annule, name="list_Demande_Recharger_Annule"), 

    path('Achat_website/<int:website_id>/', views.Achat_website, name='Achat_website'),
    path('confirm_Achat_website/', views.confirm_Achat_website, name='confirm_Achat_website'),
    path('GetFree_website/', views.GetFree_website, name='GetFree_website'),

    path('Achat_support/<int:support_id>/', views.Achat_support, name='Achat_support'),
    path('confirm_Achat_support/', views.confirm_Achat_support, name='confirm_Achat_support'),
    
    path('confirm_loyer_website/', views.confirm_loyer_website, name='confirm_loyer_website'),

    
    # path('consome_demande_support/<int:support_id>/', views.consome_demande_support, name='consome_demande_support'),
    path('confirm_consome_demande_support/', views.confirm_consome_demande_support, name='confirm_consome_demande_support'),


    path('add_websiteBuilder/', views.add_websiteBuilder, name='add_websiteBuilder'),
    path('add_locationWebsiteBuilder/', views.add_locationWebsiteBuilder, name='add_locationWebsiteBuilder'),
    path('add_GetFreeWebsiteBuilder/', views.add_GetFreeWebsiteBuilder, name='add_GetFreeWebsiteBuilder'),


    path('edite_website/<str:website_name>/', views.edite_website, name='edite_website'),
    path('edite_website_Location/<str:nameWebsite>/', views.edite_website_Location, name='edite_website_Location'),
    path('edite_free_website/<str:website_name>/', views.edite_free_website, name='edite_free_website'),


    # path('edite_website_Location/<int:website_id>/', views.edite_website_Location, name='edite_website_Location'),


    path('add_additional_info/', views.add_additional_info, name='add_additional_info'),
    path('update_cliente/', views.update_cliente, name='update_cliente'),
    
    path('change_password/', views.change_password, name='change_password'),
    
    path('add_website_resiliation/', views.add_website_resiliation, name='add_website_resiliation'),
    path('add_website_reprendre/', views.add_website_reprendre, name='add_website_reprendre'),

    path('add_website_suspendre/', views.add_website_suspendre, name='add_website_suspendre'),
    path('add_website_suspendre_reprendre/', views.add_website_suspendre_reprendre, name='add_website_suspendre_reprendre'),

    path('add_website_reset/', views.add_website_reset, name='add_website_reset'),
    # path('add_website_delete/', views.add_website_delete, name='add_website_delete'),

    path('add_period_location/<int:location_id>/', views.add_period_location, name='add_period_location'),
    path('add_period_hebergement/<int:achat_id>/', views.add_period_hebergement, name='add_period_hebergement'),
    path('add_period_free_hebergement/<int:free_id>/', views.add_period_free_hebergement, name='add_period_free_hebergement'),


    # path('update-wordpress/', views.update_wordpress_view, name='update_wordpress'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
