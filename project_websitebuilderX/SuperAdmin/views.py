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





@anonymous_required
def home2(request):
    return render(request, "websitebuilder/home2.html")


# def home(request):  
#     if request.user.is_authenticated:
#         is_Cliente = request.user.groups.filter(name='Cliente').exists()
#         is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
#         is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
#     else: 
#         is_Cliente= False  
#         is_SupportTechnique= False 
#         is_Administrateur= False  
           
#     context = {"is_Cliente": is_Cliente,"is_SupportTechnique":is_SupportTechnique,"is_Administrateur":is_Administrateur}
#     return render(request, "websitebuilder/home.html",context)









def AllWebsites_client_status(request):
    AllWebsites_client_status = Websites_client_statu.objects.all().order_by('-date_created')
    context = {"AllWebsites_client_status":AllWebsites_client_status}
    return render(request,"SuperAdmin/AllMergedWebsiteBuilder.html",context)



#SuperAdmin


# #Home SuperAdmin
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def homeSuperAdmin(request):  
    return render(request, "SuperAdmin/homeSuperAdmin.html")


from django.db.models import Sum


#DashbordHome SuperAdmin
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def dashbordHomeSuperAdmin(request):
    total_client = User.objects.filter(groups__name='Cliente').count()
    total_website = Websites.objects.all().count()
    total_service = Supports.objects.all().count()
    total_solde = Cliente.objects.aggregate(Sum('solde'))['solde__sum'] or 0 
    context = {
        'total_client': total_client,
        'total_website': total_website,
        'total_service': total_service,
        'total_solde': total_solde,
        }
    return render(request, "SuperAdmin/dashbordHomeSuperAdmin.html",context)




#The SuperAdmin can add a Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def addAdministrateur(request):
    form = AdministrateurForm()
    if request.method == 'POST':
        form = AdministrateurForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.save()

            Administrateur.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
            )

            # Add user to the 'Administrateur' group
            group = Group.objects.get(name="Administrateur")
            user.groups.add(group)

            messages.success(request, f"{user.username} created successfully!")
            return redirect('AdministrateurSuperAdmin')
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
    context = {'form': form}
    return render(request, 'SuperAdmin/addAdministrateur.html', context)




#Superadmin can show all Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def AdministrateurSuperAdmin(request): 
    Administrateurs = Administrateur.objects.all()
    context = {'Administrateurs': Administrateurs} 
    return render(request, "SuperAdmin/AdministrateurSuperAdmin.html",context)




#The SuperAdmin can add a SupportTechnique
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def addSupportTechnique(request):
    form = SupportTechniqueForm()
    if request.method == 'POST':
        form = SupportTechniqueForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  
            user.save()

            SupportTechnique.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
            )

            # Add user to the 'SupportTechnique' group
            group = Group.objects.get(name="SupportTechnique")
            user.groups.add(group)

            messages.success(request, f"{user.username} created successfully!")
            
            return redirect('SupportTechniqueSuperAdmin')
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
    context = {'form': form}
    return render(request, 'SuperAdmin/addSupportTechnique.html', context)





#Superadmin can show all SupportTechnique
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def SupportTechniqueSuperAdmin(request): 
    supportTechniques = SupportTechnique.objects.all()
    context = {'supportTechniques': supportTechniques} 
    return render(request, "SuperAdmin/SupportTechniqueSuperAdmin.html",context)





#The SuperAdmin can add a GestionnaireComptes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def addGestionnaireComptes(request):
    form = GestionnaireComptesForm()
    if request.method == 'POST':
        form = GestionnaireComptesForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False) 
            user.save()  

            GestionnaireComptes.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
            )

            # Add user to the 'GestionnaireComptes' group
            group = Group.objects.get(name="GestionnaireComptes")
            user.groups.add(group)

            messages.success(request, f"{user.username} created successfully!")
            
            return redirect('GestionnaireComptesSuperAdmin')
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
    context = {'form': form}
    return render(request, 'SuperAdmin/addGestionnaireComptes.html', context)




#Superadmin can show all clientes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def ClienteSuperAdmin(request): 
    clientes = Cliente.objects.all()
    context = {'clientes': clientes} 
    return render(request, "SuperAdmin/ClienteSuperAdmin.html",context)





#The SuperAdmin can add a clientes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def addCliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            # Create a new user
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password1')
            )

            # Create a new Cliente
            Cliente.objects.create(
                user=user,
                prenom=form.cleaned_data.get('prenom'),
                nom=form.cleaned_data.get('nom'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
            )

            # Add user to the 'Cliente' group
            group = Group.objects.get(name="Cliente")
            user.groups.add(group)

            messages.success(request, f"{user.username} created successfully!")
            return redirect('ClienteSuperAdmin')
        else:
            messages.error(request, "Invalid form submission. Please correct the errors below.")
    else:
        form = ClienteForm()
        
    context = {'form': form}
    return render(request, 'SuperAdmin/addCliente.html', context)






#Superadmin can show all GestionnaireComptes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def GestionnaireComptesSuperAdmin(request): 
    GestionnairesComptes = GestionnaireComptes.objects.all()
    context = {'GestionnairesComptes': GestionnairesComptes} 
    return render(request, "SuperAdmin/GestionnaireComptesSuperAdmin.html",context)




#SuperAdmin can show details of the trace (image) of traceDemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin'])
def full_size_image_Super_Admin(request, traceDemandeRecharger_id):
    trace_demande_recharger = get_object_or_404(LaTraceDemandeRecharger, pk=traceDemandeRecharger_id)
    image = trace_demande_recharger.image
    cliente = trace_demande_recharger.cliente.user.username
    solde = trace_demande_recharger.solde
    updated_by = trace_demande_recharger.demande_recharger.updated_by
    status = trace_demande_recharger.demande_recharger.status
    motif = trace_demande_recharger.demande_recharger.motifNonAcceptation

    return render(request, 'SuperAdmin/full_size_image_Super_Admin.html', {'image': image, 'cliente': cliente, 'solde': solde,'updated_by':updated_by,'status':status,'motif':motif})




#List of LaTraceDemandeRecharger Demandes Recharge  [SuperAdmin]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def traceDemandeRecharger(request): 
    traceDemandeRechargers = LaTraceDemandeRecharger.objects.order_by('-date_created')
    context = {'traceDemandeRechargers': traceDemandeRechargers} 
    return render(request, "SuperAdmin/traceDemandeRecharger.html",context)




#List of LaTraceDemandeRecharger Demandes Recharge  [Done]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def traceDemandeRechargerDone(request): 
    traceDemandeRechargers = LaTraceDemandeRecharger.objects.filter(demande_recharger__status='Done').order_by('-date_created')
    context = {'traceDemandeRechargers': traceDemandeRechargers} 
    return render(request, "SuperAdmin/traceDemandeRechargerDone.html",context)




#List of LaTraceDemandeRecharger Demandes Recharge  [inacceptable]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def traceDemandeRechargerInacceptable(request): 
    traceDemandeRechargers = LaTraceDemandeRecharger.objects.filter(demande_recharger__status='inacceptable').order_by('-date_created')
    context = {'traceDemandeRechargers': traceDemandeRechargers} 
    return render(request, "SuperAdmin/traceDemandeRechargerInacceptable.html",context)





#SuperAdmin can show details of the trace (image) of traceDemandeRecharger
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin'])
def full_size_image_NotDone_Super_Admin(request, DemandeRecharger_id):
    Demande_Recharger = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id)
    image = Demande_Recharger.image
    cliente = Demande_Recharger.cliente.user.username
    solde = Demande_Recharger.solde
    updated_by = Demande_Recharger.updated_by
    status = Demande_Recharger.status

    return render(request, 'SuperAdmin/full_size_image_Super_Admin.html', {'image': image, 'cliente': cliente, 'solde': solde,'updated_by':updated_by,'status':status})





@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def DemandeRechargerNotDone(request): 
    DemandeRechargerNotDones = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    context = {'DemandeRechargerNotDones': DemandeRechargerNotDones} 
    return render(request, "SuperAdmin/DemandeRechargerNotDone.html",context)





#List of Demands Support all [SuperAdmin]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def DemandeSupportAll(request): 
    DemandeSupports = DemandeSupport.objects.order_by('-date_created')
    context = {'DemandeSupports': DemandeSupports} 
    return render(request, "SuperAdmin/DemandeSupportAll.html",context)



#List of Demands Support Done [SuperAdmin]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def DemandeSupportDoneSA(request): 
    DemandeSupportsDone = DemandeSupport.objects.filter(status='Done').order_by('-date_created')
    # DemandeSupports = DemandeSupport.objects.order_by('-date_created')
    context = {'DemandeSupportsDone': DemandeSupportsDone} 
    return render(request, "SuperAdmin/DemandeSupportDoneSA.html",context)



#List of Demands Support Not Done yet [SuperAdmin]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def DemandeSupportNotDoneyetSA(request): 
    DemandeSupportsNotDoneyet = DemandeSupport.objects.filter(status='Not Done yet').order_by('-date_created')
    # DemandeSupports = DemandeSupport.objects.order_by('-date_created')
    context = {'DemandeSupportsNotDoneyet': DemandeSupportsNotDoneyet} 
    return render(request, "SuperAdmin/DemandeSupportNotDoneyetSA.html",context)







def history(request):
    history_entries = History.objects.all().order_by('-date_created')
    return render(request, 'SuperAdmin/history.html', {'history_entries': history_entries})