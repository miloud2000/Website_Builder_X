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
    InfoSupportForm,
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


from django.utils.timezone import now
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timezone import localtime, now
from django.urls import reverse



def get_support_dashboard_notifications(request):
    demande_notifications = []
    ticket_messages = []

    # ✅ demandes à traiter (si le support doit les voir)
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        demande_notifications.append({
            'message': f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}.",
            'url': 'DemandeRechargerNotDoneyet',
            'time': time_str,
            'icon': 'fe-mail',
            'color': 'warning',
        })

    # ✅ tickets non traités : créés par le client, sans réponse du support
    tickets_non_traitées = Ticket.objects.filter(
        updated_by_ts__isnull=True,
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
            'url': reverse('ticket:details_ticket_ST', args=[ticket.code_Ticket]),
        })

    # ✅ tickets traités par ce support technique
    support = getattr(request.user, 'supporttechnique', None)
    if support:
        tickets_traitées_par_moi = Ticket.objects.filter(
            updated_by_ts=support,
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
                'url': reverse('ticket:details_ticket_ST', args=[ticket.code_Ticket]),
            })

    return {
        'demande_notifications': demande_notifications,
        'ticket_messages': ticket_messages,
        'today': now(),
    }



#DashbordHome of SupportTechnique
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def dashbordHomeSupportTechnique(request):  
    dashboard_data = get_support_dashboard_notifications(request)
        
        
    support_user = SupportTechnique.objects.get(user=request.user)
    demandes_count = DemandeSupport.objects.filter(updated_by=support_user).count()
    not_done_count = DemandeSupport.objects.filter(status='Not Done yet').count()
    total_supports = Supports.objects.count()
    
    today = now()
    start_of_month = today.replace(day=1)
    demandes_this_month = DemandeSupport.objects.filter(date_created__gte=start_of_month).count()

    latest_demande_supports = (
    DemandeSupport.objects
    .filter(updated_by=support_user)
    .select_related('cliente__user', 'achat_support__support')
    .order_by('-date_created')[:6]
    )
    
    
    latest_achat_supports = (
    AchatSupport.objects
    .select_related('cliente__user', 'support')
    .order_by('-date_created')[:6]
    )


    latest_tickets_by_me = (
    Ticket.objects
    .filter(updated_by_ts=support_user)
    .select_related('cliente__user', 'supportName')
    .order_by('-date_created')[:6]
    )

    support_user = SupportTechnique.objects.get(user=request.user)
    demandes_updated_by_me = (
    DemandeSupport.objects
    .filter(updated_by=support_user)
    .select_related('cliente__user', 'achat_support__support')
    .order_by('-date_created')
    )

    # 🔍 Recherche et pagination
    search_query = request.GET.get('search', '')
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page')

    demandes_qs = DemandeSupport.objects.filter(updated_by=support_user).select_related('cliente__user', 'achat_support__support')

    if search_query:
        demandes_qs = demandes_qs.filter(
            Q(cliente__nom__icontains=search_query) |
            Q(cliente__prenom__icontains=search_query) |
            Q(cliente__user__username__icontains=search_query) |
            Q(code_DemandeSupport__icontains=search_query) |
            Q(achat_support__support__name__icontains=search_query)
        )

    paginator = Paginator(demandes_qs.order_by('-date_created'), per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'demandes_count': demandes_count,
        'support_user':support_user,
        'not_done_count': not_done_count,
        'total_supports': total_supports,
        'demandes_this_month': demandes_this_month,
        'today': today,
        'latest_demande_supports': latest_demande_supports,
        'latest_achat_supports': latest_achat_supports,
        'latest_tickets_by_me': latest_tickets_by_me,
        'demandes_updated_by_me': demandes_updated_by_me,
        'page_obj': page_obj,
        'per_page': per_page,
        'search_query': search_query,
        **dashboard_data,
    }

    return render(request, "SupportTechnique/dashbordHomeSupportTechnique.html", context)





from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def detailSupportTechnique(request):  
    support = getattr(request.user, 'supporttechnique', None)
    support_user = SupportTechnique.objects.get(user=request.user)

    if not support:
        messages.error(request, "Profil Support Technique introuvable.")
        return redirect('login')

    # ✅ Formulaire de modification des infos
    form = InfoSupportForm(instance=support)

    # ✅ Formulaire de changement de mot de passe
    password_form = PasswordChangeForm(user=request.user)

    if request.method == 'POST':
        if 'update_info' in request.POST:
            form = InfoSupportForm(request.POST, instance=support)
            if form.is_valid():
                form.save()
                messages.success(request, "Informations mises à jour avec succès.")
                return redirect('detailSupportTechnique')
            else:
                messages.error(request, "Erreur lors de la mise à jour des informations.")
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=request.user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe modifié avec succès.")
                return redirect('detailSupportTechnique')
            else:
                messages.error(request, "Erreur lors de la modification du mot de passe.")

    historique_actions = HistoriqueAction.objects.filter(
        utilisateur=request.user
    ).order_by('-date')[:20]

    dashboard_data = get_support_dashboard_notifications(request)

    context = {
        'support': support,
        'form': form,
        'password_form': password_form,
        'historique_actions': historique_actions,
        **dashboard_data,
        'support_user':support_user,
    }

    return render(request, "SupportTechnique/detailSupportTechnique.html", context)






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
from django.core.paginator import Paginator
from django.db.models import Q

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def DemandeSupportNotDoneyet(request): 
    dashboard_data = get_support_dashboard_notifications(request)
    
    support_user = SupportTechnique.objects.get(user=request.user)

    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'Not Done yet')
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page')

    demandes_qs = DemandeSupport.objects.filter(status=status_filter).select_related('cliente__user', 'achat_support__support')

    if query:
        demandes_qs = demandes_qs.filter(
            Q(cliente__nom__icontains=query) |
            Q(cliente__prenom__icontains=query) |
            Q(cliente__user__username__icontains=query) |
            Q(code_DemandeSupport__icontains=query) |
            Q(achat_support__support__name__icontains=query)
        )

    paginator = Paginator(demandes_qs.order_by('-date_created'), per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'query': query,
        'status_filter': status_filter,
        'support_user':support_user,
        **dashboard_data,
    }

    return render(request, "SupportTechnique/DemandeSupportNotDoneyet.html", context)




#List of Demands Support Done [SupportTechnique]
from django.core.paginator import Paginator
from django.db.models import Q

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def DemandeSupportDone(request): 
    dashboard_data = get_support_dashboard_notifications(request)
    
    support_user = SupportTechnique.objects.get(user=request.user)

    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'Done')
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page')

    demandes_qs = DemandeSupport.objects.filter(status=status_filter, updated_by=support_user).select_related('cliente__user', 'achat_support__support')

    if query:
        demandes_qs = demandes_qs.filter(
            Q(cliente__nom__icontains=query) |
            Q(cliente__prenom__icontains=query) |
            Q(cliente__user__username__icontains=query) |
            Q(code_DemandeSupport__icontains=query) |
            Q(achat_support__support__name__icontains=query)
        )

    paginator = Paginator(demandes_qs.order_by('-date_created'), per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'query': query,
        'status_filter': status_filter,
        'support_user':support_user,
        **dashboard_data,
    }

    return render(request, "SupportTechnique/DemandeSupportDone.html", context)







@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def websites_liste(request):
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

    dashboard_data = get_support_dashboard_notifications(request)
    support_user = SupportTechnique.objects.get(user=request.user)

    return render(request, "SupportTechnique/websites_liste.html", {
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
        'support_user':support_user,
        **dashboard_data,
    })



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def details_website(request, id):
    website = get_object_or_404(Websites, id=id)
    dashboard_data = get_support_dashboard_notifications(request)
    support_user = SupportTechnique.objects.get(user=request.user)

    return render(request, 'SupportTechnique/details_website.html', {'website': website,**dashboard_data,'support_user':support_user,
})



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def supports_list_support(request):
    status = request.GET.get('status')

    supports = Supports.objects.all()
    if status:
        supports = supports.filter(status=status)

    supports = supports.order_by('-date_created')

    # ✅ Pagination
    paginator = Paginator(supports, 10)  # 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    dashboard_data = get_support_dashboard_notifications(request)
    support_user = SupportTechnique.objects.get(user=request.user)


    context = {
        'page_obj': page_obj,  # utilisé dans le template
        'status': status,
        'status_choices': ['Disponible', 'No Disponible'],
        **dashboard_data,
        'support_user':support_user,
    }
    return render(request, 'SupportTechnique/supports_list_support.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def details_support(request, id):
    support = get_object_or_404(Supports, id=id)
    dashboard_data = get_support_dashboard_notifications(request)
    support_user = SupportTechnique.objects.get(user=request.user)

    return render(request, 'SupportTechnique/details_support.html', {'support': support,**dashboard_data,'support_user':support_user,
})

