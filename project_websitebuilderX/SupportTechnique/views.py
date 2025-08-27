from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe


from websitebuilder.models import *

from websitebuilder.forms import (  
    ClienteForm,
    AdministrateurForm,
    SupportTechniqueForm,
    GestionnaireComptesForm,
    DemandeRechargerForm,
    AdditionalInfoForm,
    ClienteUpdateForm,
    ClientePasswordChangeForm,
)

from websitebuilder.decorators import (  
    notLoggedUsers,
    allowedUsers,
    forAdmins,
    user_not_authenticated,
    anonymous_required,
)

from websitebuilder.tokens import account_activation_token  



#SupportTechnique


# #Home of SupportTechnique
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique']) 
# def homeSupportTechnique(request): 
#     if request.user.is_authenticated:
#         is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
#     else: 
#         is_SupportTechnique= False  
           
#     context = {"is_SupportTechnique":is_SupportTechnique}
 
#     return render(request, "SupportTechnique/homeSupportTechnique.html",context)




#DashbordHome of SupportTechnique
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def dashbordHomeSupportTechnique(request):  
    return render(request, "SupportTechnique/dashbordHomeSupportTechnique.html")




#SupportTechnique can consume a demand support and update status to 'Consomé'
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def consome_support(request, demande_support_id):
    demande_support = DemandeSupport.objects.get(pk=demande_support_id)
    support_technique = request.user.supporttechnique
    if demande_support and support_technique:
        demande_support.status = 'Done'
        demande_support.updated_by = support_technique
        demande_support.save()
        if demande_support.achat_support:
            demande_support.achat_support.StatusConsomé = 'Consomé'
            demande_support.achat_support.updated_by = support_technique
            demande_support.achat_support.save()
    return redirect('DemandeSupportNotDoneyet')



#SupportTechnique can consume a demand support and update status to 'Consomé' with confirmation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique'])
def confirm_consome_support(request):
    if request.method == 'POST':
        demande_support_id = request.POST.get('demande_support_id')
        if not demande_support_id:
            messages.error(request, "ID de la demande introuvable.")
            return redirect('DemandeSupportNotDoneyet')

        demande_support = get_object_or_404(DemandeSupport, pk=demande_support_id)
        support_technique = getattr(request.user, 'supporttechnique', None)

        if not support_technique:
            messages.error(request, "Profil SupportTechnique introuvable.")
            return redirect('DemandeSupportNotDoneyet')

        # Mise à jour de la demande
        demande_support.status = 'Done'
        demande_support.updated_by = support_technique
        demande_support.save()

        # Historique pour la demande
        try:
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Consommation d'une demande de support",
                objet="DemandeSupport",
                details=f"Demande « {demande_support.code_DemandeSupport} » consommée par {support_technique.user.username}.",
                date=now()
            )
        except Exception as e:
            print("❌ Erreur historique demande :", e)
            messages.warning(request, "Demande mise à jour, mais historique non enregistré.")

        # Mise à jour de l’achat lié
        achat = getattr(demande_support, 'achat_support', None)
        if achat:
            achat.StatusConsomé = 'Consomé'
            achat.updated_by = support_technique
            achat.save()

            # Historique pour l’achat
            support_name = getattr(achat.support, 'name', 'Inconnu')
            try:
                HistoriqueAction.objects.create(
                    utilisateur=request.user,
                    action="Mise à jour d'un achat support",
                    objet="AchatSupport",
                    details=f"AchatSupport (ID {achat.pk}) pour « {support_name} » marqué comme « Consomé » par {support_technique.user.username}.",
                    date=now()
                )
            except Exception as e:
                print("❌ Erreur historique achat :", e)
                messages.warning(request, "Achat mis à jour, mais historique non enregistré.")
        else:
            messages.info(request, "Aucun achat lié à cette demande.")

        messages.success(request, "Demande consommée avec succès.")
        return redirect('DemandeSupportNotDoneyet')

    return redirect('DemandeSupportNotDoneyet')



#List of Demands Support Not Done yet [SupportTechnique]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def DemandeSupportNotDoneyet(request): 
    DemandeSupports = DemandeSupport.objects.filter(status='Not Done yet').order_by('-date_created')
    context = {'DemandeSupports': DemandeSupports} 
    return render(request, "SupportTechnique/DemandeSupportNotDoneyet.html",context)




#List of Demands Support Done [SupportTechnique]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def DemandeSupportDone(request): 
    DemandeSupports = DemandeSupport.objects.filter(status='Done').order_by('-date_created')
    context = {'DemandeSupports': DemandeSupports} 
    return render(request, "SupportTechnique/DemandeSupportDone.html",context)







