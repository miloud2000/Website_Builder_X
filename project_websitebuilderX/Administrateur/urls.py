from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('dashbordHomeAdministrateur/',views.dashbordHomeAdministrateur, name="dashbordHomeAdministrateur"), 
    # path('homeAdministrateur/',views.homeAdministrateur, name="homeAdministrateur"), 

    path('gestionnaires/ajouter/', views.ajouter_gestionnaire, name='ajouter_gestionnaire'),
    path('gestionnaires/liste/', views.liste_gestionnaires, name='liste_gestionnaires'),
    path('gestionnaires/modifier/<int:gestionnaire_id>/', views.modifier_gestionnaire, name='modifier_gestionnaire'),
    path('gestionnaires/supprimer/<int:gestionnaire_id>/', views.supprimer_gestionnaire, name='supprimer_gestionnaire'),

    path('support-technique/ajouter/', views.ajouter_support_technique, name='ajouter_support_technique'),
    path('support-technique/liste/', views.liste_support_technique, name='liste_support_technique'),
    path('support-technique/modifier/<int:support_id>/', views.modifier_support_technique, name='modifier_support_technique'),
    path('support-technique/supprimer/<int:support_id>/', views.supprimer_support_technique, name='supprimer_support_technique'),


    path('commercials/', views.liste_commercial, name='liste_commercial'),
    path('commercials/ajouter/', views.ajouter_commercial, name='ajouter_commercial'),
    path('commercial/modifier/<int:commercial_id>/', views.modifier_commercial, name='modifier_commercial'),
    path('commercial/supprimer/<int:commercial_id>/', views.supprimer_commercial, name='supprimer_commercial'),



    path('clientes/', views.liste_cliente, name='liste_cliente'),
    path('clientes/ajouter/', views.ajouter_cliente, name='ajouter_cliente'),
    path('clientes/modifier/<slug:slugCliente>/', views.modifier_cliente, name='modifier_cliente'),
    path('clientes/supprimer/<slug:slugCliente>/', views.supprimer_cliente, name='supprimer_cliente'),

    path('liste_demandes_recharge/', views.liste_demandes_recharge, name='liste_demandes_recharge'),
    path('demandes-recharge/<int:id>/',views.detail_demande_recharge,name='detail_demande_recharge'),

    path('demandes-support/',views.liste_demandes_support,name='liste_demandes_support'),
    path('demandes-support/<int:pk>/',views.detail_demande_support, name='detail_demande_support'),

    path('websites/', views.liste_websites, name='liste_websites'),
    path('websites/ajouter/', views.ajouter_website, name='ajouter_website'),
    path('websites/<int:pk>/modifier/',  views.modifier_website, name='modifier_website'),
    path('websites/<int:pk>/supprimer/', views.supprimer_website,name='supprimer_website'),



    path('supports/', views.liste_supports,   name='liste_supports'),
    path('supports/ajouter/',  views.ajouter_support,  name='ajouter_support'),
    path('supports/<int:pk>/modifier/',  views.modifier_support, name='modifier_support'),
    path('supports/<int:pk>/supprimer/', views.supprimer_support,name='supprimer_support'),

    path('tickets/', views.tickets_list,    name='tickets_list'),
    path('tickets/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),

    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)