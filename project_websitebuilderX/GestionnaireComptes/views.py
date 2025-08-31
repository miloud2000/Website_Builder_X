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





#GestionnairesComptes



# #Home of GestionnairesComptes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def homeGestionnairesComptes(request): 
#     if request.user.is_authenticated:
#         is_GestionnaireComptes = request.user.groups.filter(name='GestionnaireComptes').exists()
#     else: 
#         is_GestionnaireComptes= False  
    
#     # if request.user.is_authenticated:
#     #     new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#     #     if new_demandes.exists():
#     #         messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
           
#     context = {"is_GestionnaireComptes":is_GestionnaireComptes}
 
#     return render(request, "websitebuilder/GestionnaireComptes/homeGestionnaireComptes.html",context)





#DashbordHome of GestionnaireComptes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def dashbordHomeGestionnaireComptes(request):  
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        if new_demandes.exists():
            messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
            
    return render(request, "GestionnaireComptes/dashbordHomeGestionnaireComptes.html")




@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def dashbordGestionnaireComptes(request):
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        if new_demandes.exists():
            messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')

    return render(request, "GestionnaireComptes/dashbordGestionnaireComptes.html")




#GestionnaireComptes can show all details of DemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def details_DemandeRecharger(request, demande_recharger_id):
    demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
    return render(request, 'GestionnaireComptes/details_DemandeRecharger.html', {'demande_recharger': demande_recharger})




#GestionnaireComptes can show details of the trace (image) of DemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def view_full_size_image(request, DemandeRecharger_id):
    image = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).image
    cliente = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).cliente.user.username
    solde = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).solde

    return render(request, 'GestionnaireComptes/full_size_image.html', {'image': image,'cliente': cliente,'solde': solde})




from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now

@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def confirm_demande_recharger(request, demande_recharger_id):
    demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
    demande_recharger.updated_by = request.user.gestionnairecomptes

    if request.method == 'POST':
        solde = request.POST.get('solde')
        image = request.FILES.get('image')

        # ✅ Mise à jour du solde client
        demande_recharger.cliente.solde += int(float(solde))
        demande_recharger.cliente.save()

        # ✅ Mise à jour de la demande
        demande_recharger.status = 'Done'
        demande_recharger.save()

        # ✅ Création de la trace
        LaTraceDemandeRecharger.objects.create(
            image=image,
            solde=solde,
            demande_recharger=demande_recharger,  
            cliente=demande_recharger.cliente,
            updated_by=request.user.gestionnairecomptes
        )

        # ✅ Enregistrement dans HistoriqueAction
        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Confirmation d'une demande de recharge",
            objet="DemandeRecharger",
            details=(
                f"Recharge confirmée pour le client « {demande_recharger.cliente.user.username} » "
                f"avec un montant de {solde} MAD. "
                f"Demande ID #{demande_recharger.id}."
            ),
            date=now()
        )

        messages.success(request, "Demande Recharger confirmée avec succès.")
        return redirect('DemandeRechargerDone')

    return render(request, 'GestionnaireComptes/details_DemandeRecharger.html', {
        'demande_recharger': demande_recharger
    })



@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def infirmer_demande_recharger(request, demande_recharger_id):
    demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
    demande_recharger.updated_by = request.user.gestionnairecomptes

    if request.method == 'POST':
        solde = request.POST.get('solde')
        image = request.FILES.get('image')
        motifNonAcceptation = request.POST.get('motifNonAcceptation')

        # ✅ Mise à jour de la demande
        demande_recharger.status = 'inacceptable'
        demande_recharger.motifNonAcceptation = motifNonAcceptation
        demande_recharger.save()

        # ✅ Création de la trace
        LaTraceDemandeRecharger.objects.create(
            image=image,
            solde=solde,
            demande_recharger=demande_recharger, 
            cliente=demande_recharger.cliente,
            updated_by=request.user.gestionnairecomptes
        )

        # ✅ Enregistrement dans HistoriqueAction
        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Refus d'une demande de recharge",
            objet="DemandeRecharger",
            details=(
                f"Demande ID #{demande_recharger.id} refusée pour le client « {demande_recharger.cliente.user.username} ». "
                f"Motif : {motifNonAcceptation}."
            ),
            date=now()
        )

        messages.success(request, "Demande Recharger refusée avec succès.")
        return redirect('DemandeRechargerInacceptable')

    return render(request, 'GestionnaireComptes/details_DemandeRecharger.html', {
        'demande_recharger': demande_recharger
    })




#List of Demandes Recharge Not Done yet [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerNotDoneyet(request):
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        if new_demandes.exists():
            messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
             
    DemandeRechargers = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    context = {'DemandeRechargers': DemandeRechargers} 
    return render(request, "GestionnaireComptes/DemandeRechargerNotDoneyet.html",context)




#List of Demandes Recharge Done [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerDone(request):
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        if new_demandes.exists():
            messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
             
    DemandeRechargers = DemandeRecharger.objects.filter(status='Done', updated_by__user=request.user).order_by('-date_created')
    context = {'DemandeRechargers': DemandeRechargers} 
    return render(request, "GestionnaireComptes/DemandeRechargerDone.html",context)




#List of Demandes Recharge inacceptable [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerInacceptable(request): 
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        if new_demandes.exists():
            messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
            
    DemandeRechargers = DemandeRecharger.objects.filter(status='inacceptable').order_by('-date_created')
    context = {'DemandeRechargers': DemandeRechargers} 
    return render(request, "GestionnaireComptes/DemandeRechargerInacceptable.html",context)

