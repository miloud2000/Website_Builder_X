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






from itertools import chain 
#DashbordHome of Commercial
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def dashbordHomeCommercial(request):  
    clients_added_count = Cliente.objects.filter(added_by=request.user).count()
    demandes_en_attente_count = DemandeRecharger.objects.filter(status='Not Done yet').count()
    total_websites_count = Websites.objects.count()  
    total_supports = Supports.objects.count()
    total_clients = Cliente.objects.count()
    latest_clients = Cliente.objects.filter(added_by=request.user).order_by('-date_created')[:6]

    current_user = request.user

    my_clients = Cliente.objects.filter(added_by=current_user)

    achats = AchatWebsites.objects.filter(cliente__in=my_clients, date_created__isnull=False)
    locations = LocationWebsites.objects.filter(cliente__in=my_clients, date_created__isnull=False)
    free_webs = GetFreeWebsites.objects.filter(cliente__in=my_clients, date_created__isnull=False)

    combined = chain(achats, locations, free_webs)
    all_transactions = sorted(
        combined,
        key=lambda x: x.date_created or now(),
        reverse=True
    )[:6]
    
    
    latest_achat_supports = AchatSupport.objects.filter(
        cliente__in=my_clients
    ).order_by('-date_created')[:6]

    
    context = {
        'clients_added_count': clients_added_count,
        'demandes_en_attente_count': demandes_en_attente_count,
        'total_websites_count': total_websites_count,
        'total_supports': total_supports,
        'total_clients': total_clients,
        'latest_clients': latest_clients,
        'all_transactions': all_transactions,
        'latest_achat_supports': latest_achat_supports,
        }
    return render(request, "Commercial/dashbordHomeCommercial.html", context)




from django.core.paginator import Paginator
from django.db.models import Q
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def ClienteCommercial(request):  
    # paramètres GET
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 10))
    page_number = request.GET.get('page', 1)

    base_queryset = Cliente.objects.filter(added_by=request.user)

    if query:
        base_queryset = base_queryset.filter(
            Q(nom__icontains=query) |
            Q(prenom__icontains=query) |
            Q(email__icontains=query) |
            Q(user__username__icontains=query)
        )

    if status_filter:
        base_queryset = base_queryset.filter(status=status_filter)

    base_queryset = base_queryset.order_by('-date_created')

    
    paginator = Paginator(base_queryset, per_page)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'per_page': per_page,
    }
    return render(request, "Commercial/ClienteCommercial.html", context)





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

    # استلام الفلاتر من GET
    status     = request.GET.get('status', '').strip()
    catégorie  = request.GET.get('catégorie', '').strip()
    CMS        = request.GET.get('CMS', '').strip()
    langues    = request.GET.get('langues', '').strip()
    plan       = request.GET.get('plan', '').strip()
    page       = request.GET.get('page', 1)
    per_page   = int(request.GET.get('per_page', 10))

    # قاعدة البيانات
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

    # pagination
    paginator = Paginator(websites, per_page)
    page_obj = paginator.get_page(page)

    # استخراج القوائم المميزة
    catégories_list = Websites.objects.values_list('catégorie', flat=True).distinct()
    cms_list        = Websites.objects.values_list('CMS', flat=True).distinct()
    langues_list    = Websites.objects.values_list('langues', flat=True).distinct()
    plans_list      = Websites.objects.values_list('plan', flat=True).distinct()

    return render(request, "Commercial/list_websites.html", {
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
        'per_page': per_page,
    })



from django.utils.timezone import localtime

def details_website_commercial(request, id):
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        messages.info(
        request,
        f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    )
    website = get_object_or_404(Websites, id=id)
    return render(request, 'Commercial/details_website_commercial.html', {'website': website})




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






def supports_list_commercial(request):
    status = request.GET.get('status')

    supports = Supports.objects.all()
    if status:
        supports = supports.filter(status=status)

    supports = supports.order_by('-date_created')

    # ✅ Pagination
    paginator = Paginator(supports, 10)  # 10 éléments par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,  # utilisé dans le template
        'status': status,
        'status_choices': ['Disponible', 'No Disponible'],
    }
    return render(request, 'Commercial/supports_list_commercial.html', context)





def details_support_commercial(request, id):
    new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    for demande in new_demandes:
        time_str = localtime(demande.date_created).strftime("%H:%M")
        messages.info(
        request,
        f"Demande #{demande.code_DemandeRecharger} de {demande.cliente.user.username} — {demande.solde} MAD à traiter à {time_str}."
    )
    support = get_object_or_404(Supports, id=id)
    return render(request, 'Commercial/details_support_commercial.html', {'support': support})
