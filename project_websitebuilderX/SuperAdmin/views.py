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
    CommercialForm,
    UpdateAdministrateurForm,
    UpdateSupportTechniqueForm,
    UpdateGestionnaireComptesForm,
    ClienteUpdateFormSuperAdmin,
    CommercialUpdateForm,
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





from django.db.models import Q

#Superadmin can show all Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def AdministrateurSuperAdmin(request): 
    query = request.GET.get('q')
    status_filter = request.GET.get('status')

    Administrateurs = Administrateur.objects.all()

    if query:
        Administrateurs = Administrateurs.filter(
            Q(user__username__icontains=query) |
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        )

    if status_filter:
        Administrateurs = Administrateurs.filter(Status__icontains=status_filter)

    context = {'Administrateurs': Administrateurs}
    return render(request, "SuperAdmin/AdministrateurSuperAdmin.html", context)


import csv
from django.http import HttpResponse

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def export_admins_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="administrateurs.csv"'

    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Phone', 'Status', 'Date ajout'])

    for admin in Administrateur.objects.all():
        writer.writerow([
            admin.user.username,
            admin.email,
            admin.phone,
            admin.Status,
            admin.date_created.strftime('%d/%m/%Y %H:%M')
        ])

    return response


import openpyxl
from django.http import HttpResponse

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def export_admins_excel(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Administrateurs"

    headers = ['Username', 'Email', 'Phone', 'Status', 'Date ajout']
    ws.append(headers)

    for admin in Administrateur.objects.all():
        ws.append([
            admin.user.username,
            admin.email,
            admin.phone,
            admin.Status,
            admin.date_created.strftime('%d/%m/%Y %H:%M')
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="administrateurs.xlsx"'
    wb.save(response)
    return response


from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO

@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def export_admins_pdf(request):
    admins = Administrateur.objects.all()
    template = get_template('SuperAdmin/pdf_admins_template.html')
    html = template.render({'admins': admins})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="administrateurs.pdf"'

    pisa_status = pisa.CreatePDF(BytesIO(html.encode('utf-8')), dest=response)
    return response





@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def updateAdministrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, id=pk)
    form = UpdateAdministrateurForm(instance=administrateur)

    if request.method == 'POST':
        form = UpdateAdministrateurForm(request.POST, instance=administrateur)
        if form.is_valid():
            form.save()
            messages.success(request, "Administrateur mis à jour avec succès.")
            return redirect('AdministrateurSuperAdmin')

    context = {'form': form}
    return render(request, 'SuperAdmin/updateAdministrateur.html', context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def deleteAdministrateur(request, pk):
    administrateur = get_object_or_404(Administrateur, id=pk)
    user = administrateur.user

    if request.method == 'POST':
        user.delete() 
        messages.success(request, "Administrateur supprimé avec succès.")
        return redirect('AdministrateurSuperAdmin')

    context = {'administrateur': administrateur}
    return render(request, 'SuperAdmin/deleteAdministrateur.html', context)



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





@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def updateSupportTechnique(request, pk):
    support = get_object_or_404(SupportTechnique, id=pk)
    form = UpdateSupportTechniqueForm(instance=support)

    if request.method == 'POST':
        form = UpdateSupportTechniqueForm(request.POST, instance=support)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Support Technique mis à jour avec succès.")
            return redirect('SupportTechniqueSuperAdmin')

    context = {'form': form}
    return render(request, 'SuperAdmin/updateSupportTechnique.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def deleteSupportTechnique(request, pk):
    support = get_object_or_404(SupportTechnique, id=pk)
    user = support.user

    if request.method == 'POST':
        user.delete()
        messages.success(request, "🗑️ Support Technique supprimé avec succès.")
        return redirect('SupportTechniqueSuperAdmin')

    context = {'support': support}
    return render(request, 'SuperAdmin/deleteSupportTechnique.html', context)





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



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def updateGestionnaireComptes(request, pk):
    gestionnaire = get_object_or_404(GestionnaireComptes, id=pk)
    form = UpdateGestionnaireComptesForm(instance=gestionnaire)

    if request.method == 'POST':
        form = UpdateGestionnaireComptesForm(request.POST, instance=gestionnaire)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Gestionnaire mis à jour avec succès.")
            return redirect('GestionnaireComptesSuperAdmin')

    context = {'form': form}
    return render(request, 'SuperAdmin/updateGestionnaireComptes.html', context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin'])
def deleteGestionnaireComptes(request, pk):
    gestionnaire = get_object_or_404(GestionnaireComptes, pk=pk)

    if request.method == 'POST':
        if gestionnaire.user:
            gestionnaire.user.delete()
        gestionnaire.delete()
        messages.success(request, "✅ Le gestionnaire a été supprimé avec succès.")
        return redirect('GestionnaireComptesSuperAdmin')

    context = {'gestionnaire': gestionnaire}
    return render(request, 'SuperAdmin/deleteGestionnaireComptes.html', context)





#Superadmin can show all clientes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def ClienteSuperAdmin(request): 
    clientes = Cliente.objects.all()
    context = {'clientes': clientes} 
    return render(request, "SuperAdmin/ClienteSuperAdmin.html",context)




#Superadmin can show all Commercials
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def CommercialSuperAdmin(request): 
    commercials = Commercial.objects.all()
    context = {'commercials': commercials} 
    return render(request, "SuperAdmin/CommercialSuperAdmin.html", context)




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




@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def updateCliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        form = ClienteUpdateFormSuperAdmin(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Client modifié avec succès.")
            return redirect('ClienteSuperAdmin')
        else:
            messages.error(request, "❌ Erreur dans le formulaire.")
    else:
        form = ClienteUpdateFormSuperAdmin(instance=cliente)

    context = {'form': form, 'cliente': cliente}
    return render(request, 'SuperAdmin/updateCliente.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def deleteCliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)

    if request.method == 'POST':
        if cliente.user:
            cliente.user.delete()
        cliente.delete()
        messages.success(request, "✅ Client supprimé avec succès.")
        return redirect('ClienteSuperAdmin')

    context = {'cliente': cliente}
    return render(request, 'SuperAdmin/deleteCliente.html', context)





@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def addCommercial(request):
    if request.method == 'POST':
        form = CommercialForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data.get('username'),
                email=form.cleaned_data.get('email'),
                password=form.cleaned_data.get('password1')
            )

            Commercial.objects.create(
                user=user,
                name=form.cleaned_data.get('name'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone'),
                status=form.cleaned_data.get('status'),
            )

            group = Group.objects.get(name="Commercial")
            user.groups.add(group)

            messages.success(request, f"Le commercial {user.username} a été créé avec succès !")
            return redirect('CommercialSuperAdmin')
        else:
            messages.error(request, "Formulaire invalide. Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CommercialForm()
        
    context = {'form': form}
    return render(request, 'SuperAdmin/addCommercial.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def updateCommercial(request, pk):
    commercial = get_object_or_404(Commercial, pk=pk)

    if request.method == 'POST':
        form = CommercialUpdateForm(request.POST, instance=commercial)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Commercial modifié avec succès.")
            return redirect('CommercialSuperAdmin')
        else:
            messages.error(request, "❌ Erreur dans le formulaire.")
    else:
        form = CommercialUpdateForm(instance=commercial)

    context = {'form': form, 'commercial': commercial}
    return render(request, 'SuperAdmin/updateCommercial.html', context)



@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def deleteCommercial(request, pk):
    commercial = get_object_or_404(Commercial, pk=pk)

    if request.method == 'POST':
        if commercial.user:
            commercial.user.delete()
        commercial.delete()
        messages.success(request, "✅ Commercial supprimé avec succès.")
        return redirect('CommercialSuperAdmin')

    context = {'commercial': commercial}
    return render(request, 'SuperAdmin/deleteCommercial.html', context)



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