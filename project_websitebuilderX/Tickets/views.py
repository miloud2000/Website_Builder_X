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




def ticket_list(request):
    cliente = request.user.cliente 
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    tickets = Ticket.objects.filter(cliente=cliente).order_by('-date_created')

    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
        'tickets' :tickets,
    }
    return render(request, "Tickets/ticket_list.html",context)




from django.shortcuts import render, redirect


def add_ticket(request):
    cliente = request.user.cliente
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

    if request.method == 'POST':
        typeTicket = request.POST.get('type')
        Branche = request.POST.get('branch')
        message = request.POST.get('message')
        code_Demande = request.POST.get('code_Demande')
        nameWebsite = request.POST.get('nameWebsite')
        nameSupport = request.POST.get('nameSupport')
        attachment = request.FILES.get('attachment')

        if typeTicket and Branche and message:
            ticket = Ticket(
                cliente=cliente,
                description=message,
                status='Ouvert',
                typeTicket=typeTicket,
                Branche=Branche,
                code_Demande=code_Demande,
                nameWebsite=nameWebsite,
                nameSupport=nameSupport,
                pièce_joint=attachment
            )
            ticket.save()
            return redirect('ticket_list')  

    context = {
        'cliente': cliente,
        'WebsiteBuilders': WebsiteBuilders,
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





from django.shortcuts import render, get_object_or_404


@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def details_ticket_ST(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    context = {
        'ticket': ticket,
    }
    return render(request, 'Tickets/details_ticket_ST.html', context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def details_ticket_GC(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    context = {
        'ticket': ticket,
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
        piècejoint_updated_by = request.FILES.get('piècejoint_updated_by')

        ticket.description_updated_by = description_updated_by
        ticket.status = status
        
        if piècejoint_updated_by:
            ticket.pièce_joint_updated_by = piècejoint_updated_by
        
        ticket.updated_by_ts = support_technique
        ticket.save()
        return redirect('details_ticket_ST', ticket_id=ticket.id)
    
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
        return redirect('details_ticket_GC', ticket_id=ticket.id)
    
    return render(request, 'details_ticket_GC.html', {'ticket': ticket})
