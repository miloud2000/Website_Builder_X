from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    
    path('dashbordHomeGestionnaireComptes/',views.dashbordHomeGestionnaireComptes, name="dashbordHomeGestionnaireComptes"), 
    path('homeGestionnairesComptes/',views.homeGestionnairesComptes, name="homeGestionnairesComptes"), 

    path('details_DemandeRecharger/<int:demande_recharger_id>/', views.details_DemandeRecharger, name='details_DemandeRecharger'),
    
    path('DemandeRechargerNotDoneyet/',views.DemandeRechargerNotDoneyet, name="DemandeRechargerNotDoneyet"), 
    path('DemandeRechargerDone/',views.DemandeRechargerDone, name="DemandeRechargerDone"), 
    path('DemandeRechargerInacceptable/',views.DemandeRechargerInacceptable, name="DemandeRechargerInacceptable"), 

    path('confirm_demande_recharger/<int:demande_recharger_id>/', views.confirm_demande_recharger, name='confirm_demande_recharger'),
    path('infirmer_demande_recharger/<int:demande_recharger_id>/', views.infirmer_demande_recharger, name='infirmer_demande_recharger'),

    path('full_size_image/<int:DemandeRecharger_id>/', views.view_full_size_image, name='full_size_image'),

    path('websites_liste_GestionnaireComptes/',views.websites_liste_GestionnaireComptes, name="websites_liste_GestionnaireComptes"), 
    path('details_website_GestionnaireComptes/<int:id>/', views.details_website_GestionnaireComptes, name='details_website_GestionnaireComptes'),

    path('supports_list_GestionnaireComptes/',views.supports_list_GestionnaireComptes, name="supports_list_GestionnaireComptes"), 
    path('details_support_GestionnaireComptes/<int:id>/', views.details_support_GestionnaireComptes, name='details_support_GestionnaireComptes'),

    
    # path('done_demande_recharger/<int:demande_recharger_id>/', views.done_demande_recharger, name='done_demande_recharger'),
    
    
    
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)