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

from django.contrib.auth.decorators import login_required



@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def ticket_list(request):
    cliente = request.user.cliente 
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    tickets = Ticket.objects.filter(cliente=cliente).order_by('-date_created')
    ticket_count = Ticket.objects.filter(cliente=cliente).count()
    
    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
        'tickets' :tickets,
        'ticket_count': ticket_count,
    }
    return render(request, "Tickets/ticket_list.html",context)






@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def details_ticket(request, code_Ticket):
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')

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
            return redirect('details_ticket', code_Ticket=code_Ticket)

    context = {
        'ticket': ticket,
        'conversations': conversations,
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
            return redirect('ticket_list')  

    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
        'websites': websites, 
        'supports' : supports,
    }
    return render(request, "Tickets/add_ticket.html", context)





@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def list_ticket_ST(request):
    tickets = Ticket.objects.filter(typeTicket="Technique").order_by('-date_created')

    # Apply filters
    code_ticket = request.GET.get('code_ticket', '')
    date_created = request.GET.get('date_created', '')
    username_client = request.GET.get('username_client', '')
    code_demande = request.GET.get('code_demande', '')
    branche = request.GET.get('branche', '')
    status = request.GET.get('status', '')
    
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
        tickets = tickets.filter(code_Demande=code_demande)
    if branche:
        tickets = tickets.filter(Branche=branche)
    if status:
        tickets = tickets.filter(status=status)
    
    context = {
        'tickets' :tickets,
    }
    return render(request, "Tickets/list_ticket_ST.html",context)




from datetime import datetime


@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def list_ticket_GC(request):
    tickets = Ticket.objects.filter(typeTicket="Facturation").order_by('-date_created')
    
    # Apply filters
    code_ticket = request.GET.get('code_ticket', '')
    date_created = request.GET.get('date_created', '')
    username_client = request.GET.get('username_client', '')
    branche = request.GET.get('branche', '')
    status = request.GET.get('status', '')
    
    if code_ticket:
        tickets = tickets.filter(code_Ticket__icontains=code_ticket)
    if date_created:
        try:
            date_created = datetime.strptime(date_created, '%Y-%m-%d').date()
            tickets = tickets.filter(date_created__date=date_created)
        except ValueError:
            pass  # Handle invalid date format if necessary
    if username_client:
        tickets = tickets.filter(cliente__user__username__icontains=username_client)
    if branche:
        tickets = tickets.filter(Branche=branche)
    if status:
        tickets = tickets.filter(status=status)
    
    context = {
        'tickets': tickets,
    }
    return render(request, "Tickets/list_ticket_GC.html", context)




from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique'])
def details_ticket_ST(request, code_Ticket):
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        status = request.POST.get('status')
        
        # Handle conversation updates
        if message or image:
            sender_type = 'SupportTechnique'
            sender_id = request.user.supporttechnique.id
            Conversation.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                image=image  # Add image if provided
            )
            messages.success(request, 'Message sent successfully')

        # Handle status updates
        if status:
            if status in dict(Ticket.STATUS_CHOICES).keys():
                ticket.status = status
                ticket.updated_by_ts = request.user.supporttechnique
                ticket.save()
                messages.success(request, 'Ticket status updated successfully')
            else:
                messages.error(request, 'Invalid status selected')
        
        return redirect('details_ticket_ST', code_Ticket=code_Ticket)
    
    context = {
        'ticket': ticket,
        'conversations': conversations,
        'status_choices': Ticket.STATUS_CHOICES,
    }
    return render(request, 'Tickets/details_ticket_ST.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes'])
def details_ticket_GC(request, code_Ticket):
    ticket = get_object_or_404(Ticket, code_Ticket=code_Ticket)
    conversations = ticket.conversations.all().order_by('timestamp')

    if request.method == 'POST':
        message = request.POST.get('message')
        image = request.FILES.get('image')
        status = request.POST.get('status')  # Get the new status from the form

        # Handle conversation updates
        if message or image:
            sender_type = 'GestionnaireComptes'
            sender_id = request.user.gestionnairecomptes.id
            Conversation.objects.create(
                ticket=ticket,
                sender_type=sender_type,
                sender_id=sender_id,
                message=message,
                image=image  # Add image if provided
            )
            messages.success(request, 'Message sent successfully')

        # Handle status updates
        if status:
            if status in dict(Ticket.STATUS_CHOICES).keys():
                ticket.status = status
                ticket.updated_by_gc = request.user.gestionnairecomptes
                ticket.save()
                messages.success(request, 'Ticket status updated successfully')
            else:
                messages.error(request, 'Invalid status selected')

        return redirect('details_ticket_GC', code_Ticket=code_Ticket)

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
        return redirect('details_ticket_ST', code_Ticket=ticket.code_Ticket)
    
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
        return redirect('details_ticket_GC', code_Ticket=ticket.code_Ticket)
    
    return render(request, 'details_ticket_GC.html', {'ticket': ticket})
