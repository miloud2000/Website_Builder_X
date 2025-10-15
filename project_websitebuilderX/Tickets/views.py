from django.shortcuts import render

from websitebuilder.models import *

from websitebuilder.forms import (  
    ClienteForm,
)

from websitebuilder.decorators import (  
    notLoggedUsers,
    allowedUsers,
    forAdmins,
    user_not_authenticated,
    anonymous_required,
)





from itertools import chain
from django.utils.timezone import now
from collections import Counter
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.timesince import timesince
from itertools import chain

def get_user_notifications_and_messages(cliente):
    achats = AchatWebsites.objects.filter(cliente=cliente)
    locations = LocationWebsites.objects.filter(cliente=cliente)
    free_webs = GetFreeWebsites.objects.filter(cliente=cliente)
    supports = AchatSupport.objects.filter(cliente=cliente)

    raw_notifications = []

    for obj in achats:
        raw_notifications.append({
            'message': f"Achat du site {obj.websites.name}",
            'time': timesince(obj.date_created) + " ago",
            'icon': 'fe-shopping-cart',
            'color': 'primary',
            'date_created': obj.date_created
        })

    for obj in locations:
        raw_notifications.append({
            'message': f"Location du site {obj.websites.name}",
            'time': timesince(obj.date_created) + " ago",
            'icon': 'fe-home',
            'color': 'secondary',
            'date_created': obj.date_created
        })

    for obj in free_webs:
        raw_notifications.append({
            'message': f"Site gratuit : {obj.websites.name}",
            'time': timesince(obj.date_created) + " ago",
            'icon': 'fe-gift',
            'color': 'success',
            'date_created': obj.date_created
        })

    for obj in supports:
        raw_notifications.append({
            'message': f"Support acheté : {obj.support.name}",
            'time': timesince(obj.date_created) + " ago",
            'icon': 'fe-check-circle',
            'color': 'info',
            'date_created': obj.date_created
        })

    notifications = sorted(raw_notifications, key=lambda x: x['date_created'], reverse=True)[:6]

   
    recharges = DemandeRecharger.objects.filter(
        cliente=cliente,
        status__in=['done', 'inacceptable']
    ).order_by('-date_created')[:5]
    

    
    tickets = Ticket.objects.filter(
        Q(cliente=cliente) &
        (Q(updated_by_ts__isnull=False) | Q(updated_by_gc__isnull=False)) &
        Q(conversations__isnull=False)
    ).distinct().order_by('-date_updated')[:5]

    messages_dropdown = []

    for recharge in recharges:
        messages_dropdown.append({
        'type': 'Recharge',
        'title': f"Demande de recharge : {recharge.solde} MAD",
        'subtitle': f"Statut : {recharge.status}",
        'time': timesince(recharge.date_created) + " ago",
        'image': 'faces/1.jpg',
        'date_created': recharge.date_created,
    })


    for ticket in tickets:
        messages_dropdown.append({
        'type': 'Ticket',
        'title': f"Ticket mis à jour : {ticket.typeTicket}",
        'subtitle': f"Statut : {ticket.status}",
        'time': timesince(ticket.date_updated) + " ago",
        'image': 'faces/2.jpg',
        'date_created': ticket.date_updated,
        'code_Ticket': ticket.code_Ticket  
    })



    messages_dropdown = sorted(messages_dropdown, key=lambda x: x['date_created'], reverse=True)

    return notifications, messages_dropdown



from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def ticket_list(request):
    cliente = request.user.cliente 
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

    all_tickets = Ticket.objects.filter(cliente=cliente).order_by('-date_created')
    paginator = Paginator(all_tickets, 8)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    ticket_count = all_tickets.count()

    notifications, messages_dropdown = get_user_notifications_and_messages(cliente)
    
    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
        'tickets': page_obj,  
        'ticket_count': ticket_count,
        'notifications' : notifications,
        'messages_dropdown':messages_dropdown,
    }
    return render(request, "Tickets/ticket_list.html", context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def details_ticket(request, code_Ticket):
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')
    cliente = request.user.cliente
    notifications, messages_dropdown = get_user_notifications_and_messages(cliente)


    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        if message or image:
            # Determine the sender type and ID
            if hasattr(request.user, 'cliente'):
                sender_type = 'Cliente'
                sender_id = request.user.cliente.id
            else:
                sender_type = 'SupportTechnique'
                sender_id = request.user.supporttechnique.id
            
            # Create a new conversation
            Conversation.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                image=image  # Add image if provided
            )
            return redirect('ticket:details_ticket', code_Ticket=code_Ticket)

    context = {
        'ticket': ticket,
        'conversations': conversations,
        'notifications' : notifications,
        'messages_dropdown':messages_dropdown,
    }
    return render(request, 'Tickets/details_ticket.html', context)





from django.shortcuts import render, redirect, get_object_or_404


def add_ticket(request):
    cliente = request.user.cliente
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    websites = Websites.objects.all()
    supports = Supports.objects.all()
    
    if request.method == 'POST':
        typeTicket = request.POST.get('type')
        Branche = request.POST.get('branch')
        message = request.POST.get('message')
        code_Demande = request.POST.get('code_Demande')
        nameWebsite_id = request.POST.get('nameWebsite')  # Fetch the Website ID
        nameSupport_id = request.POST.get('nameSupport')  # Fetch the Support ID
        attachment = request.FILES.get('attachment')

        if typeTicket and Branche and message:
            # Fetch the Websites instance if available
            if nameWebsite_id:
                nameWebsite = get_object_or_404(Websites, id=nameWebsite_id)
            else:
                nameWebsite = None

            # Fetch the Supports instance
            if nameSupport_id:
                nameSupport = get_object_or_404(Supports, id=nameSupport_id)
            else:
                nameSupport = None

            ticket = Ticket(
                cliente=cliente,
                description=message,
                status='Ouvert',
                typeTicket=typeTicket,
                Branche=Branche,
                code_Demande=code_Demande,
                websiteName=nameWebsite,
                supportName=nameSupport,
                pièce_joint=attachment
            )
            ticket.save()
            return redirect('ticket:ticket_list')  

    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
        'websites': websites, 
        'supports' : supports,
    }
    return render(request, "Tickets/add_ticket.html", context)



from django.core.paginator import Paginator
from django.db.models import Q
from datetime import datetime

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def list_ticket_ST(request):
    tickets = Ticket.objects.filter(typeTicket="Technique").order_by('-date_created')

    # 🔍 Filtrage
    code_ticket = request.GET.get('code_ticket', '')
    date_created = request.GET.get('date_created', '')
    username_client = request.GET.get('username_client', '')
    code_demande = request.GET.get('code_demande', '')
    branche = request.GET.get('branche', '')
    status_filter = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page')

    if code_ticket:
        tickets = tickets.filter(code_Ticket__icontains=code_ticket)
    if date_created:
        try:
            date_created = datetime.strptime(date_created, '%Y-%m-%d').date()
            tickets = tickets.filter(date_created__date=date_created)
        except ValueError:
            pass 
    if username_client:
        tickets = tickets.filter(cliente__user__username__icontains=username_client)
    if code_demande:
        tickets = tickets.filter(code_Demande__icontains=code_demande)
    if branche:
        tickets = tickets.filter(Branche=branche)
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    paginator = Paginator(tickets, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'code_ticket': code_ticket,
        'date_created': date_created,
        'username_client': username_client,
        'code_demande': code_demande,
        'branche': branche,
        'status_filter': status_filter,
    }

    return render(request, "Tickets/list_ticket_ST.html", context)




from datetime import datetime
from django.utils.timezone import localtime

@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def list_ticket_GC(request):
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        messages.info(
        request,
        f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    )
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

    # Filters
    code_ticket = request.GET.get('code_ticket', '')
    date_created = request.GET.get('date_created', '')
    username_client = request.GET.get('username_client', '')
    branche = request.GET.get('branche', '')
    status_filter = request.GET.get('status', '')

    tickets = Ticket.objects.filter(typeTicket="Facturation")

    if code_ticket:
        tickets = tickets.filter(code_Ticket__icontains=code_ticket)
    if date_created:
        try:
            date_created = datetime.strptime(date_created, '%Y-%m-%d').date()
            tickets = tickets.filter(date_created__date=date_created)
        except ValueError:
            pass
    if username_client:
        tickets = tickets.filter(cliente__user__username__icontains=username_client)
    if branche:
        tickets = tickets.filter(Branche=branche)
    if status_filter:
        tickets = tickets.filter(status=status_filter)

    tickets = tickets.order_by('-date_created')

    paginator = Paginator(tickets, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'per_page': per_page,
        'code_ticket': code_ticket,
        'date_created': date_created,
        'username_client': username_client,
        'branche': branche,
        'status_filter': status_filter,
    }

    return render(request, "Tickets/list_ticket_GC.html", context)



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique'])
def details_ticket_ST(request, code_Ticket):
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        status = request.POST.get('status')

        # 💬 Ajout de message
        if message or image:
            sender_type = 'SupportTechnique'
            sender_id = request.user.supporttechnique.id
            Conversation.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                image=image
            )
            messages.success(request, 'Message envoyé avec succès')

            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout de message",
                objet="Ticket",
                details=f"Message ajouté au ticket {ticket.code_Ticket} : « {message} »" + (" avec image" if image else "")  
            )

        # 🔄 Changement de statut
        if status:
            if status in dict(Ticket.STATUS_CHOICES).keys():
                ticket.status = status
                ticket.updated_by_ts = request.user.supporttechnique
                ticket.save()
                messages.success(request, 'Statut du ticket mis à jour')

                HistoriqueAction.objects.create(
                    utilisateur=request.user,
                    action="Modification du statut",
                    objet="Ticket",
                    details=f"Statut changé en '{ticket.get_status_display()}' pour le ticket {ticket.code_Ticket}"
                )
            else:
                messages.error(request, 'Statut invalide sélectionné')

        return redirect('ticket:details_ticket_ST', code_Ticket=code_Ticket)

    context = {
        'ticket': ticket,
        'conversations': conversations,
        'status_choices': Ticket.STATUS_CHOICES,
    }
    return render(request, 'Tickets/details_ticket_ST.html', context)



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.timezone import now


@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def details_ticket_GC(request, code_Ticket):
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        messages.info(
        request,
        f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    )
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        status = request.POST.get('status')

        # ✅ Ajout d'une conversation
        if message or image:
            sender_type = 'GestionnaireComptes'
            sender_id = request.user.gestionnairecomptes.id

            Conversation.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                image=image
            )
            messages.success(request, 'Message envoyé avec succès.')

            # 🔍 Détail de l'action pour l'historique
            contenu_detail = f"Message ajouté au ticket #{ticket.code_Ticket} par le gestionnaire. "
            if message and image:
                contenu_detail += f"Contenu : « {message[:100]} » + image jointe."
            elif message:
                contenu_detail += f"Contenu : « {message[:100]} »"
            elif image:
                contenu_detail += "Message avec image uniquement."

            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un message dans un ticket",
                objet="Ticket",
                details=contenu_detail,
                date=now()
            )

        # ✅ Mise à jour du statut du ticket
        if status:
            if status in dict(Ticket.STATUS_CHOICES).keys():
                ticket.status = status
                ticket.updated_by_gc = request.user.gestionnairecomptes
                ticket.save()
                messages.success(request, 'Statut du ticket mis à jour avec succès.')

                HistoriqueAction.objects.create(
                    utilisateur=request.user,
                    action="Modification du statut d'un ticket",
                    objet="Ticket",
                    details=f"Statut du ticket #{ticket.code_Ticket} modifié en « {status} ».",
                    date=now()
                )
            else:
                messages.error(request, 'Statut sélectionné invalide.')

        return redirect('ticket:details_ticket_GC', code_Ticket=code_Ticket)

    context = {
        'ticket': ticket,
        'conversations': conversations,
        'status_choices': Ticket.STATUS_CHOICES,
    }
    return render(request, 'Tickets/details_ticket_GC.html', context)





from django.http import JsonResponse


def get_branch_options(request):
    if request.is_ajax() and request.method == "GET":
        branch = request.GET.get('branch', None)
        branch_options = {
            'Technique': ['Website', 'Application', 'Service', 'Autre'],
            'Commercial': ["Demande d'information", 'Demande de devis', 'Autre'],
            'Facturation': ['Probleme de paiement', 'Probleme de solde', 'Autre'],
        }
        data = branch_options.get(branch, [])
        return JsonResponse({'data': data})
    
    


@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique'])
def update_ticket_st(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    try:
        support_technique = request.user.supporttechnique
    except SupportTechnique.DoesNotExist:
        support_technique = None

    if request.method == 'POST':
        description_updated_by = request.POST.get('description_updated_by')
        status = request.POST.get('status')
        pièce_joint_updated_by = request.FILES.get('pièce_joint_updated_by')

        ticket.description_updated_by = description_updated_by
        ticket.status = status
        
        if pièce_joint_updated_by:
            ticket.pièce_joint_updated_by = pièce_joint_updated_by
        
        ticket.updated_by_ts = support_technique
        ticket.save()
        return redirect('ticket:details_ticket_ST', code_Ticket=ticket.code_Ticket)
    
    return render(request, 'details_ticket_ST.html', {'ticket': ticket})




@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def update_ticket_gc(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    try:
        gestionnaire_comptes = GestionnaireComptes.objects.get(user=request.user)
    except GestionnaireComptes.DoesNotExist:
        return redirect('/') 

    if request.method == 'POST':
        description_updated_by = request.POST.get('description_updated_by')
        status = request.POST.get('status')
        pièce_joint_updated_by = request.FILES.get('pièce_joint_updated_by')

        ticket.description_updated_by = description_updated_by
        ticket.status = status
        
        if pièce_joint_updated_by:
            ticket.pièce_joint_updated_by = pièce_joint_updated_by
        
        ticket.updated_by_gc = gestionnaire_comptes
        ticket.save()
        return redirect('ticket:details_ticket_GC', code_Ticket=ticket.code_Ticket)
    
    return render(request, 'details_ticket_GC.html', {'ticket': ticket})
