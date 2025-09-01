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




#Commercial




# #Home of Administrateur





#DashbordHome of Commercial
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def dashbordHomeCommercial(request):  
    return render(request, "Commercial/dashbordHomeCommercial.html")




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def ClienteCommercial(request): 
    clientes = Cliente.objects.all()
    context = {'clientes': clientes} 
    return render(request, "Commercial/ClienteCommercial.html",context)





from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User, Group
from django.utils.timezone import now

@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def addCliente_c(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            # ✅ Création du compte utilisateur
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            # ✅ Création du client
            cliente = Cliente.objects.create(
                user=user,
                prenom=form.cleaned_data['prenom'],
                nom=form.cleaned_data['nom'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                added_by=request.user
            )

            # ✅ Ajout au groupe "Cliente"
            group = Group.objects.get(name="Cliente")
            user.groups.add(group)

            # ✅ Historique d'ajout
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un nouveau client",
                objet="Cliente",
                details=(
                    f"Client « {cliente.prenom} {cliente.nom} » (username: {user.username}) ajouté par "
                    f"{request.user.username}."
                ),
                date=now()
            )

            messages.success(request, f"{user.username} ajouté avec succès !")
            return redirect('ClienteCommercial')
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = ClienteForm()

    return render(request, 'Commercial/addCliente.html', {'form': form})






@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def updateCliente_c(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    user = cliente.user

    if request.method == 'POST':
        form = ClienteUpdateForm(request.POST, instance=cliente)
        if form.is_valid():
            # Mise à jour de l'email du User
            user.email = form.cleaned_data['email']
            user.save()

            # Mise à jour du Cliente
            cliente = form.save(commit=False)
            cliente.email = form.cleaned_data['email']
            cliente.save()

            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Modification d'un client",
                objet="Cliente",
                details=f"Client « {cliente.prenom} {cliente.nom} » modifié par {request.user.username}.",
                date=now()
            )

            messages.success(request, "Client modifié avec succès.")
            return redirect('ClienteCommercial')
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = ClienteUpdateForm(instance=cliente)
        form.fields['email'].initial = user.email  # ✅ injecté ici

    return render(request, 'Commercial/updateCliente.html', {'form': form})







@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def deleteCliente_c(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)
    username = cliente.user.username
    nom_complet = f"{cliente.prenom} {cliente.nom}"

    if request.method == 'POST':
        cliente.user.delete()  # Supprime aussi le compte lié
        cliente.delete()

        # ✅ Historique de suppression
        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un client",
            objet="Cliente",
            details=(
                f"Client « {nom_complet} » (username: {username}) supprimé par {request.user.username}."
            ),
            date=now()
        )

        messages.success(request, "Client supprimé avec succès.")
        return redirect('ClienteCommercial')

    return render(request, 'Commercial/confirm_delete_cliente.html', {'cliente': cliente})




#List of websites that are displayed to the Commercial
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def list_websites_c(request): 
    websites = Websites.objects.all()
    context = {
        'websites': websites,
        }  
    return render(request, "Commercial/list_websites.html",context)






#More detail of website
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def detail_website_c(request, slugWebsites):
    if request.user.is_authenticated:
        is_Cliente = request.user.groups.filter(name='Cliente').exists()
        is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
        is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
        is_Commercial = request.user.groups.filter(name='Commercial').exists()
    else: 
        is_Cliente= False  
        is_SupportTechnique= False 
        is_Administrateur= False  
        is_Commercial= False
        
    website_info = get_object_or_404(Websites, slugWebsites=slugWebsites)
    
    context = {
        'website_info': website_info,
        "is_Cliente": is_Cliente,
        "is_SupportTechnique":is_SupportTechnique,
        "is_Administrateur":is_Administrateur,
        "is_Commercial" :is_Commercial
    }
    return render(request, "Commercial/detail_website.html", context)





#List of All websites that are displayed to the Commercial
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial'])
def all_list_websites_c(request):
    if request.user.is_authenticated:
        is_Cliente = request.user.groups.filter(name='Cliente').exists()
        is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
        is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
        is_Commercial = request.user.groups.filter(name='Commercial').exists()

    else:
        is_Cliente = False  
        is_SupportTechnique = False 
        is_Administrateur = False  
        is_Commercial= False


    category = request.GET.get('category', 'All')
    cms_filter = request.GET.get('cms', '')
    langues_filter = request.GET.get('langues', '')
    plan_filter = request.GET.get('plan', '')

    websites = Websites.objects.all()

    if category != 'All' and category != '*':
        websites = websites.filter(catégorie=category)
    
    if cms_filter:
        websites = websites.filter(CMS=cms_filter)
    
    if langues_filter:
        websites = websites.filter(langues=langues_filter)
    
    if plan_filter:
        websites = websites.filter(plan=plan_filter)
    
    context = {
        'websites': websites,
        "is_Cliente": is_Cliente,
        "is_SupportTechnique": is_SupportTechnique,
        "is_Administrateur": is_Administrateur,
        "is_Commercial" :is_Commercial,
        "selected_category": category,
        "cms_filter": cms_filter,
        "langues_filter": langues_filter,
        "plan_filter": plan_filter,
    }

    return render(request, 'Commercial/all_list_websites.html', context)

