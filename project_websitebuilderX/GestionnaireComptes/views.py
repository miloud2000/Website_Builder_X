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
    GestionnaireForm,
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
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def homeGestionnairesComptes(request): 
    if request.user.is_authenticated:
        is_GestionnaireComptes = request.user.groups.filter(name='GestionnaireComptes').exists()
    else: 
        is_GestionnaireComptes= False  
    
    # if request.user.is_authenticated:
    #     new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    #     if new_demandes.exists():
    #         messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
           
    context = {"is_GestionnaireComptes":is_GestionnaireComptes}
 
    return render(request, "websitebuilder/GestionnaireComptes/homeGestionnaireComptes.html",context)



from django.utils import timezone
from django.utils.timezone import localtime
from itertools import chain
from operator import attrgetter
from django.urls import reverse

def get_dashboard_notifications_and_messages(request):
    demande_notifications = []
    ticket_messages = []

    # ✅ demandes à traiter
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        demande_notifications.append({
            'message': f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}.",
            'url': 'DemandeRechargerNotDoneyet',
            'time': time_str,
            'icon': 'fe-mail',
            'color': 'primary',
        })

    # ✅ tickets non traités : créés par le client, sans modification ni conversation
    tickets_non_traitées = Ticket.objects.filter(
        updated_by_gc__isnull=True,
        conversations__isnull=True
    ).distinct().order_by('-date_created')[:6]

    for ticket in tickets_non_traitées:
        time_str = localtime(ticket.date_created).strftime("%H:%M")
        code = ticket.code_Ticket or f"ID {ticket.id}"
        type_label = ticket.typeTicket or "Type inconnu"
        client_name = ticket.cliente.user.username if ticket.cliente and ticket.cliente.user else "Client inconnu"

        ticket_messages.append({
        'sender': client_name,
        'message': f"🕒 Nouveau ticket {code} — {type_label} sans réponse",
        'time': time_str,
        'avatar': 'img/default-icon.png',
        'status': 'non_traité',
        'url': reverse('ticket:details_ticket_GC', args=[ticket.code_Ticket]),    })

    # ✅ tickets traités par ce gestionnaire avec conversation
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    if gestionnaire:
        tickets_traitées_par_moi = Ticket.objects.filter(
            updated_by_gc=gestionnaire,
            conversations__isnull=False
        ).distinct().order_by('-date_created')[:6]

        for ticket in tickets_traitées_par_moi:
            time_str = localtime(ticket.date_created).strftime("%H:%M")
            code = ticket.code_Ticket or f"ID {ticket.id}"
            type_label = ticket.typeTicket or "Type inconnu"
            client_name = ticket.cliente.user.username if ticket.cliente and ticket.cliente.user else "Client inconnu"

            ticket_messages.append({
            'sender': client_name,
            'message': f"✅ Ticket {code} — {type_label} traité par vous",
            'time': time_str,
            'avatar': 'img/default-icon.png',
            'status': 'traité',
            'url': reverse('ticket:details_ticket_GC', args=[ticket.code_Ticket]),
            })


    return {
        'demande_notifications': demande_notifications,
        'ticket_messages': ticket_messages,
        'today': now(),
    }




#DashbordHome of GestionnaireComptes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def dashbordHomeGestionnaireComptes(request):  
    now = timezone.now()
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    demande_notifications = []
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        demande_notifications.append({
            'message': f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}.",
            'url': 'DemandeRechargerNotDoneyet',
            'time': time_str,
            'icon': 'fe-mail',
            'color': 'primary', 
        })

    # ✅ tickets modifiés par ce gestionnaire
    latest_tickets = Ticket.objects.filter(
        updated_by_gc__user=request.user
    ).order_by('-date_created')[:6]

    ticket_messages = []
    for ticket in latest_tickets:
        time_str = localtime(ticket.date_created).strftime("%H:%M")
        code = ticket.code_Ticket or f"ID {ticket.id}"
        type_label = ticket.typeTicket or "Type inconnu"
        client_name = ticket.cliente.user.username if ticket.cliente and ticket.cliente.user else "Client inconnu"

        ticket_messages.append({
            'sender': client_name,
            'message': f"🎫 Ticket {code} — {type_label}",
            'time': time_str,
            'avatar': 'img/default-icon.png',
        })

    # Comptage des demandes modifiées par le gestionnaire
    demandes_modifiees_count = DemandeRecharger.objects.filter(
        updated_by__user=request.user
    ).count()

    # Comptage des demandes en attente
    demandes_en_attente_count = new_demandes.count()

    # Comptage des demandes créées ce mois
    now = timezone.now()
    demandes_this_month = DemandeRecharger.objects.filter(
        date_created__year=now.year,
        date_created__month=now.month
    ).count()
    
    latest_demande_supports = DemandeRecharger.objects.filter(
    updated_by__user=request.user
    ).order_by('-date_created')[:6]
    
    # Derniers achats
    latest_achats = AchatWebsites.objects.select_related('cliente__user', 'websites').order_by('-date_created')[:6]

    # Dernières locations
    latest_locations = LocationWebsites.objects.select_related('cliente__user', 'websites').order_by('-date_created')[:6]

    # Fusionner les deux et trier par date
    latest_web_transactions = sorted(
        chain(latest_achats, latest_locations),
        key=attrgetter('date_created'),
        reverse=True
    )[:6]
    
    
    latest_tickets_by_me = Ticket.objects.filter(
    updated_by_gc__user=request.user
    ).order_by('-date_created')[:6]

    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'demandes_modifiees_count': demandes_modifiees_count,
        'demandes_en_attente_count': demandes_en_attente_count,
        'total_supports': DemandeRecharger.objects.count(),
        'demandes_this_month': demandes_this_month,
        'today': now,
        'latest_demande_supports': latest_demande_supports,
        'latest_web_transactions': latest_web_transactions,
        'latest_tickets_by_me': latest_tickets_by_me,
        # 'demande_notifications': demande_notifications,
        # 'ticket_messages': ticket_messages,
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }

    return render(request, "GestionnaireComptes/dashbordHomeGestionnaireComptes.html", context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def dashbordGestionnaireComptes(request):
    if request.user.is_authenticated:
        new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
        for demande in new_demandes:
            messages.info(
                request,
                f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter."
            )

    return render(request, "GestionnaireComptes/dashbordGestionnaireComptes.html")



from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def detailGestionnaire(request):  
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    if not gestionnaire:
        messages.error(request, "Profil Gestionnaire introuvable.")
        return redirect('login')

    # ✅ Formulaire de modification des infos
    form = GestionnaireForm(instance=gestionnaire)

    # ✅ Formulaire de changement de mot de passe
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_info' in request.POST:
            form = GestionnaireForm(request.POST, instance=gestionnaire)
            if form.is_valid():
                form.save()
                messages.success(request, "Informations mises à jour avec succès.")
                return redirect('detailGestionnaire')
            else:
                messages.error(request, "Erreur lors de la mise à jour des informations.")
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe modifié avec succès.")
                return redirect('detailGestionnaire')
            else:
                messages.error(request, "Erreur lors de la modification du mot de passe.")

    historique_actions = HistoriqueAction.objects.filter(
        utilisateur=request.user
    ).order_by('-date')[:20]

    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'gestionnaire': gestionnaire,
        'form': form,
        'password_form': password_form,
        'historique_actions': historique_actions,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }

    return render(request, "GestionnaireComptes/detailGestionnaire.html", context)




#GestionnaireComptes can show all details of DemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def details_DemandeRecharger(request, demande_recharger_id):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
        
    dashboard_data = get_dashboard_notifications_and_messages(request)

    return render(request, 'GestionnaireComptes/details_DemandeRecharger.html', {'demande_recharger': demande_recharger,
        'today': now,
        **dashboard_data,'gestionnaire': gestionnaire,})




#GestionnaireComptes can show details of the trace (image) of DemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def view_full_size_image(request, DemandeRecharger_id):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    image = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).image
    cliente = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).cliente.user.username
    solde = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).solde
    
    dashboard_data = get_dashboard_notifications_and_messages(request)


    return render(request, 'GestionnaireComptes/full_size_image.html', {'image': image,'cliente': cliente,'solde': solde,'today': now,
        **dashboard_data,'gestionnaire': gestionnaire,})




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



from django.core.paginator import Paginator
from django.db.models import Q
#List of Demandes Recharge Not Done yet [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerNotDoneyet(request):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
        
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

    # Définir le queryset
    demandes_queryset = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')

    # Pagination
    paginator = Paginator(demandes_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }

    return render(request, "GestionnaireComptes/DemandeRechargerNotDoneyet.html", context)





#List of Demandes Recharge Done [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerDone(request):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

 
    demandes_queryset = DemandeRecharger.objects.filter(
        status='Done',
        updated_by__user=request.user
    ).order_by('-date_created')

    paginator = Paginator(demandes_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'query': '', 
        'status_filter': 'Done',
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }

    return render(request, "GestionnaireComptes/DemandeRechargerDone.html", context)





#List of Demandes Recharge inacceptable [GestionnaireComptes]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def DemandeRechargerInacceptable(request): 
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

    demandes_queryset = DemandeRecharger.objects.filter(
        status='inacceptable',
        updated_by__user=request.user
    ).order_by('-date_created')

    paginator = Paginator(demandes_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'query': '',  
        'status_filter': 'inacceptable',
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }

    return render(request, "GestionnaireComptes/DemandeRechargerInacceptable.html", context)






@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def websites_liste_GestionnaireComptes(request):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    status     = request.GET.get('status', '').strip()
    catégorie  = request.GET.get('catégorie', '').strip()
    CMS        = request.GET.get('CMS', '').strip()
    langues    = request.GET.get('langues', '').strip()
    plan       = request.GET.get('plan', '').strip()
    page       = request.GET.get('page', 1)
    per_page   = 10 

    websites = Websites.objects.filter(is_visible=True)

    if status:
        websites = websites.filter(status=status)
    if catégorie:
        websites = websites.filter(catégorie=catégorie)
    if CMS:
        websites = websites.filter(CMS=CMS)
    if langues:
        websites = websites.filter(langues=langues)
    if plan:
        websites = websites.filter(plan=plan)

    websites = websites.order_by('-date_created')

    paginator = Paginator(websites, per_page)
    page_obj = paginator.get_page(page)

    catégories_list = Websites.objects.values_list('catégorie', flat=True).distinct()
    cms_list        = Websites.objects.values_list('CMS', flat=True).distinct()
    langues_list    = Websites.objects.values_list('langues', flat=True).distinct()
    plans_list      = Websites.objects.values_list('plan', flat=True).distinct()

    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    return render(request, "GestionnaireComptes/websites_liste_GestionnaireComptes.html", {
        'websites': page_obj.object_list,
        'page_obj': page_obj,
        'status': status,
        'catégorie': catégorie,
        'CMS': CMS,
        'langues': langues,
        'plan': plan,
        'catégories_list': catégories_list,
        'cms_list': cms_list,
        'langues_list': langues_list,
        'plans_list': plans_list,
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    })


@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def details_website_GestionnaireComptes(request, id):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    website = get_object_or_404(Websites, id=id)
    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    return render(request, 'GestionnaireComptes/details_website_GestionnaireComptes.html', {'website': website,'today': now,
        **dashboard_data,'gestionnaire': gestionnaire,})



@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def supports_list_GestionnaireComptes(request):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    status = request.GET.get('status')

    supports = Supports.objects.all()
    if status:
        supports = supports.filter(status=status)

    supports = supports.order_by('-date_created')

    # ✅ Pagination
    paginator = Paginator(supports, 10)  # 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    context = {
        'page_obj': page_obj,  # utilisé dans le template
        'status': status,
        'status_choices': ['Disponible', 'No Disponible'],
        'today': now,
        **dashboard_data,
        'gestionnaire': gestionnaire,
    }
    return render(request, 'GestionnaireComptes/supports_list_GestionnaireComptes.html', context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def details_support_GestionnaireComptes(request, id):
    gestionnaire = getattr(request.user, 'gestionnairecomptes', None)
    # new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    # for demande in new_demandes:
    #     time_str = localtime(demande.date_created).strftime("%H:%M")
    #     messages.info(
    #     request,
    #     f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    # )
    support = get_object_or_404(Supports, id=id)
    
    dashboard_data = get_dashboard_notifications_and_messages(request)

    return render(request, 'GestionnaireComptes/details_support_GestionnaireComptes.html', {'support': support,'today': now,
        **dashboard_data,'gestionnaire': gestionnaire,})
