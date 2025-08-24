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


    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)