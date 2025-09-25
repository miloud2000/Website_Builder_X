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
    WebsiteForm,
    SupportForm,
    
)

from websitebuilder.decorators import (  
    notLoggedUsers,
    allowedUsers,
    forAdmins,
    user_not_authenticated,
    anonymous_required,
)

from websitebuilder.tokens import account_activation_token  



#Administrateur


# #Home of Administrateur
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Administrateur']) 
# def homeAdministrateur(request): 
#     if request.user.is_authenticated:
#         is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
#     else: 
#         is_Administrateur= False  
           
#     context = {"is_Administrateur":is_Administrateur}
 
#     return render(request, "websitebuilder/Administrateur/homeAdministrateur.html",context)


from django.db.models import Sum, Count
from django.core.paginator import Paginator

#DashbordHome of Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Administrateur']) 
def dashbordHomeAdministrateur(request):  
    today = timezone.now()
    start_week = today - timedelta(days=today.weekday())
    start_last_week = start_week - timedelta(days=7)
    end_last_week = start_week - timedelta(seconds=1)

    clients_this_week = User.objects.filter(groups__name='Cliente', date_joined__gte=start_week).count()
    clients_last_week = User.objects.filter(groups__name='Cliente', date_joined__range=(start_last_week, end_last_week)).count()
    client_growth = ((clients_this_week - clients_last_week) / clients_last_week * 100) if clients_last_week > 0 else (-100.0 if clients_this_week == 0 else 100.0)

    start_6_days_ago = today - timedelta(days=6)
    start_12_days_ago = today - timedelta(days=12)
    websites_now = Websites.objects.filter(date_created__gte=start_6_days_ago).count()
    websites_before = Websites.objects.filter(date_created__range=(start_12_days_ago, start_6_days_ago)).count()
    websites_growth = ((websites_now - websites_before) / websites_before * 100) if websites_before > 0 else (-100.0 if websites_now == 0 else 100.0)

    start_9_days_ago = today - timedelta(days=9)
    start_18_days_ago = today - timedelta(days=18)
    supports_now = Supports.objects.filter(date_created__gte=start_9_days_ago).count()
    supports_before = Supports.objects.filter(date_created__range=(start_18_days_ago, start_9_days_ago)).count()
    supports_growth = ((supports_now - supports_before) / supports_before * 100) if supports_before > 0 else (-100.0 if supports_now == 0 else 100.0)

    start_year = today.replace(month=1, day=1)
    solde_this_year = Cliente.objects.filter(date_created__gte=start_year).aggregate(Sum('solde'))['solde__sum'] or 0
    solde_before = Cliente.objects.filter(date_created__lt=start_year).aggregate(Sum('solde'))['solde__sum'] or 0
    solde_growth = ((solde_this_year - solde_before) / solde_before * 100) if solde_before > 0 else (-100.0 if solde_this_year == 0 else 100.0)

    total_sales = AchatWebsites.objects.aggregate(Sum('prix_achat'))['prix_achat__sum'] or 0
    total_orders = AchatWebsites.objects.count()
    delivered_orders = AchatWebsites.objects.filter(BuilderStatus='Builder').count()
    cancelled_orders = AchatWebsites.objects.filter(BuilderStatus='Not yet').count()

   
    
    latest_recharges = DemandeRecharger.objects.select_related('cliente__user').order_by('-date_created')[:6]
    
    total_achats = AchatWebsites.objects.count()
    
    website_achat_counts = (
    AchatWebsites.objects
    .values('websites__name')
    .annotate(count=Count('id'))
    )
    
    website_achat_percentages = []
    for entry in website_achat_counts:
        name = entry['websites__name']
        count = entry['count']
        percentage = round((count / total_achats) * 100, 2) if total_achats > 0 else 0
        website_achat_percentages.append({
            'name': name,
            'percentage': percentage
        })
        
        
    total_achat_supports = AchatSupport.objects.count()
    
    support_achat_counts = (
    AchatSupport.objects
    .values('support__name')
    .annotate(count=Count('id'))
    )
    
    support_achat_percentages = []
    for entry in support_achat_counts:
        name = entry['support__name']
        count = entry['count']
        percentage = round((count / total_achat_supports) * 100, 2) if total_achat_supports > 0 else 0
        support_achat_percentages.append({
            'name': name,
            'count': count,
            'percentage': percentage
        })
    
    
    clients = Cliente.objects.select_related('user').all()
    
    search_query = request.GET.get('search', '')
    per_page = request.GET.get('per_page', 10)

    clients = Cliente.objects.select_related('user')

    if search_query:
        clients = clients.filter(
            Q(nom__icontains=search_query) |
            Q(prenom__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    paginator = Paginator(clients, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    
    context = {
    'clients_this_week': clients_this_week,
    'client_growth': round(client_growth, 2),
    'websites_growth': round(websites_growth, 2),
    'supports_growth': round(supports_growth, 2),
    'solde_growth': round(solde_growth, 2),
    'total_website': Websites.objects.count(),
    'total_service': Supports.objects.count(),
    'total_solde': round(Cliente.objects.aggregate(Sum('solde'))['solde__sum'] or 0, 2),

    # Graph data for each chart

    'latest_recharges': latest_recharges,
    'website_achat_percentages': website_achat_percentages,
    'support_achat_percentages': support_achat_percentages,
    
    'clients': clients,
    
    'page_obj': page_obj,
    'search_query': search_query,
    'per_page': int(per_page),
    }
    return render(request, "Administrateur/dashbordHomeAdministrateur.html", context)



from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.models import User



@login_required
def liste_gestionnaires(request):
    gestionnaires = GestionnaireComptes.objects.all().order_by('-date_created')
    return render(request, 'Administrateur/liste_gestionnaires.html', {'gestionnaires': gestionnaires})




from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect

@login_required
def ajouter_gestionnaire(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Ce nom d'utilisateur existe déjà.")
        else:
            # Création du User
            user = User.objects.create_user(username=username, password=password, email=email)

            # Ajout au groupe "Gestionnaire"
            group = Group.objects.get(name="GestionnaireComptes")
            user.groups.add(group)

            # Création du modèle GestionnaireComptes
            gestionnaire = GestionnaireComptes.objects.create(
                user=user,
                name=name,
                email=email,
                phone=phone,
                Status='Active'
            )

            # Historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un gestionnaire",
                objet="GestionnaireComptes",
                details=f"Gestionnaire '{gestionnaire.name}' créé avec le compte '{user.username}'"
            )

            messages.success(request, "✅ Gestionnaire ajouté avec succès.")
            return redirect('liste_gestionnaires')

    return render(request, 'Administrateur/ajouter_gestionnaire.html')



from django.shortcuts import get_object_or_404

@login_required
def modifier_gestionnaire(request, gestionnaire_id):
    gestionnaire = get_object_or_404(GestionnaireComptes, id=gestionnaire_id)

    if request.method == 'POST':
        gestionnaire.name = request.POST.get('name')
        gestionnaire.email = request.POST.get('email')
        gestionnaire.phone = request.POST.get('phone')
        gestionnaire.Status = request.POST.get('Status')
        gestionnaire.save()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Modification d'un gestionnaire",
            objet="GestionnaireComptes",
            details=f"Gestionnaire '{gestionnaire.name}' modifié par '{request.user.username}'"
        )

        messages.success(request, "✅ Gestionnaire modifié avec succès.")
        return redirect('liste_gestionnaires')

    return render(request, 'Administrateur/modifier_gestionnaire.html', {'gestionnaire': gestionnaire})



@login_required
def supprimer_gestionnaire(request, gestionnaire_id):
    gestionnaire = get_object_or_404(GestionnaireComptes, id=gestionnaire_id)

    if request.method == 'POST':
        nom = gestionnaire.name
        gestionnaire.delete()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un gestionnaire",
            objet="GestionnaireComptes",
            details=f"Gestionnaire '{nom}' supprimé par '{request.user.username}'"
        )

        messages.success(request, "🗑️ Gestionnaire supprimé avec succès.")
        return redirect('liste_gestionnaires')

    return render(request, 'Administrateur/confirmer_suppression.html', {'gestionnaire': gestionnaire})




from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.contrib.auth.models import User
from django.utils.text import slugify


@login_required
def liste_support_technique(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    per_page = int(request.GET.get('per_page', 10))

    supports = SupportTechnique.objects.all().order_by('-date_created')

    if query:
        supports = supports.filter(
            Q(name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query) |
            Q(user__username__icontains=query)
        )

    if status_filter:
        supports = supports.filter(Status=status_filter)

    paginator = Paginator(supports, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'supports': page_obj.object_list,
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
        'per_page': per_page,
    }

    return render(request, 'Administrateur/liste_support_technique.html', context)




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.text import slugify

@login_required
def ajouter_support_technique(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if password1 != password2:
            messages.error(request, "❌ Les mots de passe ne sont pas identiques.")
            return redirect('ajouter_support_technique')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Ce nom d'utilisateur existe déjà.")
            return redirect('ajouter_support_technique')

        user = User.objects.create_user(username=username, password=password1, email=email)

        try:
            group = Group.objects.get(name="SupportTechnique")
            user.groups.add(group)
        except Group.DoesNotExist:
            messages.error(request, "❌ Le groupe 'SupportTechnique' n'existe pas.")
            return redirect('ajouter_support_technique')

        support = SupportTechnique.objects.create(
            user=user,
            name=name,
            email=email,
            phone=phone,
            Status='Active',
            slugSupportTechnique=slugify(username)
        )

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Ajout d'un support technique",
            objet="SupportTechnique",
            details=f"Support technique '{support.name}' créé avec le compte '{user.username}'"
        )

        messages.success(request, "✅ Support technique ajouté avec succès.")
        return redirect('liste_support_technique')

    return render(request, 'Administrateur/ajouter_support_technique.html')




from django.shortcuts import get_object_or_404

@login_required
def modifier_support_technique(request, support_id):
    support = get_object_or_404(SupportTechnique, id=support_id)

    if request.method == 'POST':
        support.name = request.POST.get('name')
        support.email = request.POST.get('email')
        support.phone = request.POST.get('phone')
        support.Status = request.POST.get('Status')
        support.save()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Modification d'un support technique",
            objet="SupportTechnique",
            details=f"Support '{support.name}' modifié par '{request.user.username}'"
        )

        messages.success(request, "✅ Support technique modifié avec succès.")
        return redirect('liste_support_technique')

    return render(request, 'Administrateur/modifier_support_technique.html', {'support': support})



@login_required
def supprimer_support_technique(request, support_id):
    support = get_object_or_404(SupportTechnique, id=support_id)

    if request.method == 'POST':
        nom = support.name
        support.delete()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un support technique",
            objet="SupportTechnique",
            details=f"Support '{nom}' supprimé par '{request.user.username}'"
        )

        messages.success(request, "🗑️ Support technique supprimé avec succès.")
        return redirect('liste_support_technique')

    return render(request, 'Administrateur/confirmer_suppression_support.html', {'support': support})



@login_required
def liste_commercial(request):
    commerciaux = Commercial.objects.all().order_by('-date_created')
    return render(request, 'Administrateur/liste_commercial.html', {'commerciaux': commerciaux})



@login_required
def ajouter_commercial(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        status = request.POST.get('status')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Ce nom d'utilisateur existe déjà.")
        else:
            # Création du compte utilisateur
            user = User.objects.create_user(username=username, password=password, email=email)

            # Ajout au groupe "Commercial"
            group = Group.objects.get(name="Commercial")
            user.groups.add(group)

            # Création du modèle Commercial
            commercial = Commercial.objects.create(
                user=user,
                name=name,
                email=email,
                phone=phone,
                status=status,
                slugCommercial=slugify(username)
            )

            # Historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un commercial",
                objet="Commercial",
                details=f"Commercial '{commercial.name}' créé avec le compte '{user.username}'"
            )

            messages.success(request, "✅ Commercial ajouté avec succès.")
            return redirect('liste_commercial')

    return render(request, 'Administrateur/ajouter_commercial.html')



@login_required
def modifier_commercial(request, commercial_id):
    commercial = get_object_or_404(Commercial, id=commercial_id)

    if request.method == 'POST':
        commercial.name = request.POST.get('name')
        commercial.email = request.POST.get('email')
        commercial.phone = request.POST.get('phone')
        commercial.status = request.POST.get('status')
        commercial.save()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Modification d'un commercial",
            objet="Commercial",
            details=f"Commercial '{commercial.name}' modifié par '{request.user.username}'"
        )

        messages.success(request, "✅ Commercial modifié avec succès.")
        return redirect('liste_commercial')

    return render(request, 'Administrateur/modifier_commercial.html', {'commercial': commercial})


@login_required
def supprimer_commercial(request, commercial_id):
    commercial = get_object_or_404(Commercial, id=commercial_id)

    if request.method == 'POST':
        nom = commercial.name
        commercial.delete()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un commercial",
            objet="Commercial",
            details=f"Commercial '{nom}' supprimé par '{request.user.username}'"
        )

        messages.success(request, "🗑️ Commercial supprimé avec succès.")
        return redirect('liste_commercial')

    return render(request, 'Administrateur/confirmer_suppression_commercial.html', {'commercial': commercial})





@login_required
def liste_cliente(request):
    clientes = Cliente.objects.select_related('user').order_by('-date_created')

    context = {
        'clientes': clientes
    }
    return render(request, 'Administrateur/liste_cliente.html', context)



@login_required
def modifier_cliente(request, slugCliente):
    cliente = get_object_or_404(Cliente, slugCliente=slugCliente)

    if request.method == 'POST':
        cliente.prenom = request.POST.get('prenom')
        cliente.nom = request.POST.get('nom')
        cliente.email = request.POST.get('email')
        cliente.phone = request.POST.get('phone')
        cliente.address = request.POST.get('address')
        cliente.nom_entreprise = request.POST.get('nom_entreprise')
        cliente.numero_ice = request.POST.get('numero_ice')
        cliente.updated_by = request.user.gestionnairecomptes if hasattr(request.user, 'gestionnairecomptes') else None

        cliente.save()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Modification d'un client",
            objet="Cliente",
            details=f"Client '{cliente.nom} {cliente.prenom}' modifié"
        )

        messages.success(request, "✅ Client modifié avec succès.")
        return redirect('liste_cliente')

    return render(request, 'Administrateur/modifier_cliente.html', {'cliente': cliente})


@login_required
def supprimer_cliente(request, slugCliente):
    cliente = get_object_or_404(Cliente, slugCliente=slugCliente)

    if request.method == 'POST':
        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un client",
            objet="Cliente",
            details=f"Client '{cliente.nom} {cliente.prenom}' supprimé"
        )
        cliente.delete()
        messages.success(request, "🗑 Client supprimé avec succès.")
        return redirect('liste_cliente')

    return render(request, 'Administrateur/supprimer_cliente.html', {'cliente': cliente})




@login_required
def ajouter_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        nom_entreprise = request.POST.get('nom_entreprise')
        numero_ice = request.POST.get('numero_ice')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Ce nom d'utilisateur existe déjà.")
        else:
            # Création du compte utilisateur
            user = User.objects.create_user(username=username, password=password, email=email)

            # Ajout au groupe "Cliente"
            group = Group.objects.get(name="Cliente")
            user.groups.add(group)

            # Création du modèle Cliente
            cliente = Cliente.objects.create(
                user=user,
                prenom=prenom,
                nom=nom,
                email=email,
                phone=phone,
                address=address,
                nom_entreprise=nom_entreprise,
                numero_ice=numero_ice,
                added_by=request.user,
                slugCliente=slugify(username),
                code_client=generate_cliente_code(nom, prenom)
            )

            # Historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un client",
                objet="Cliente",
                details=f"Client '{cliente.nom} {cliente.prenom}' créé avec le compte '{user.username}'"
            )

            messages.success(request, "✅ Client ajouté avec succès.")
            return redirect('liste_cliente')

    return render(request, 'Administrateur/ajouter_cliente.html')





# views.py

from django.shortcuts import render
from django.db.models import Q


def liste_demandes_recharge(request):
    qs = (DemandeRecharger.objects
          .select_related('cliente__user', 'updated_by__user')
          .all())

    # 1. Récupération des paramètres GET
    client      = request.GET.get('client', '').strip()
    statut      = request.GET.get('statut', '').strip()
    date_start  = request.GET.get('date_start', '')
    date_end    = request.GET.get('date_end', '')
    montant_min = request.GET.get('montant_min', '')
    montant_max = request.GET.get('montant_max', '')

    # 2. Construction dynamique du filtre
    if client:
        qs = qs.filter(cliente__user__username__icontains=client)

    if statut:
        qs = qs.filter(status=statut)

    if date_start:
        qs = qs.filter(date_created__date__gte=date_start)

    if date_end:
        qs = qs.filter(date_created__date__lte=date_end)

    if montant_min:
        qs = qs.filter(solde__gte=montant_min)

    if montant_max:
        qs = qs.filter(solde__lte=montant_max)

    demandes = qs.order_by('-date_created')

    # 3. On renvoie aussi les valeurs de filtre pour pré-remplissage
    return render(request, "Administrateur/liste_demandes.html", {
        'demandes': demandes,
        'filter_values': {
            'client':      client,
            'statut':      statut,
            'date_start':  date_start,
            'date_end':    date_end,
            'montant_min': montant_min,
            'montant_max': montant_max,
        }
    })




from django.shortcuts import render, get_object_or_404

def detail_demande_recharge(request, id):
    demande = get_object_or_404(
        DemandeRecharger.objects
            .select_related('cliente__user', 'updated_by__user'),
        id=id
    )
    traces_qs = demande.latracedemanderecharger_set.select_related(
        'updated_by__user'
    ).order_by('-date_created')

    # on transforme chaque trace en dict prêt à l’usage
    traces = [
        {
            "date": t.date_created.strftime("%d/%m/%Y %H:%M"),
            "gestionnaire": t.updated_by.user.username if t.updated_by else "—",
            "solde": f"{t.solde:.2f} MAD",
        }
        for t in traces_qs
    ]

    contexte = {
        'demande': {
            'code': demande.code_DemandeRecharger,
            'client': demande.cliente.user.username,
            'montant': f"{demande.solde:.2f} MAD",
            'statut': demande.status,
            'date': demande.date_created.strftime("%d/%m/%Y %H:%M"),
            'gestionnaire': (
                demande.updated_by.user.username
                if demande.updated_by else '—'
            ),
            'motif': demande.motifNonAcceptation or '',
            'image_url': demande.image.url if demande.image else None,
        },
        'traces': traces,
    }
    return render(request, 'Administrateur/detail_demande.html', contexte)



# support/views.py (ou dans votre views.py existant)


def liste_demandes_support(request):
    qs = (DemandeSupport.objects
          .select_related('cliente__user',
                          'achat_support__support',
                          'updated_by__user')
          .all())

    # Récupération des paramètres GET
    client       = request.GET.get('client', '').strip()
    statut       = request.GET.get('statut', '').strip()
    support_nom  = request.GET.get('support', '').strip()
    date_start   = request.GET.get('date_start', '')
    date_end     = request.GET.get('date_end', '')

    # Application dynamique des filtres
    if client:
        qs = qs.filter(cliente__user__username__icontains=client)
    if statut:
        qs = qs.filter(status=statut)
    if support_nom:
        qs = qs.filter(achat_support__support__name__icontains=support_nom)
    if date_start:
        qs = qs.filter(date_created__date__gte=date_start)
    if date_end:
        qs = qs.filter(date_created__date__lte=date_end)

    demandes = qs.order_by('-date_created')

    return render(request, "Administrateur/liste_demandes_support.html", {
        'demandes': demandes,
        'filter_values': {
            'client':     client,
            'statut':     statut,
            'support':    support_nom,
            'date_start': date_start,
            'date_end':   date_end,
        }
    })




def detail_demande_support(request, pk):
    demande = get_object_or_404(
        DemandeSupport.objects
            .select_related('cliente__user',
                            'achat_support__support',
                            'updated_by__user'),
        pk=pk
    )
    return render(request, "Administrateur/detail_demande_support.html", {
        'demande': demande
    })



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect


@login_required
def liste_websites(request):
    """
    Liste simple des sites (visible uniquement).
    """
    websites = Websites.objects.filter(is_visible=True).order_by('-date_created')
    return render(request, "Administrateur/liste_websites.html", {
        'websites': websites
    })



@login_required
def ajouter_website(request):
    """
    Ajout d’un nouveau site via WebsiteForm + historique.
    """
    if request.method == 'POST':
        form = WebsiteForm(request.POST, request.FILES)
        if form.is_valid():
            site = form.save()  # slug et tout le reste sont gérés par save() du model

            # Création de l'entrée d'historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un site web",
                objet="Websites",
                details=(
                    f"Site '{site.name}' créé (slug: {site.slugWebsites}, "
                    f"prix: {site.prix} €)"
                )
            )

            messages.success(request, "Le site a été ajouté avec succès.")
            return redirect('liste_websites')
        else:
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
    else:
        form = WebsiteForm()

    return render(request, "Administrateur/ajouter_website.html", {
        'form': form
    })



from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404


@login_required
def modifier_website(request, pk):
    """
    Modifier un site existant et tracer l'action.
    """
    site = get_object_or_404(Websites, pk=pk, is_visible=True)

    if request.method == 'POST':
        form = WebsiteForm(request.POST, request.FILES, instance=site)
        if form.is_valid():
            ancien = Websites.objects.get(pk=pk)  # pour comparer si nécessaire
            site_modifie = form.save()

            # Historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Modification d'un site web",
                objet="Websites",
                details=(
                    f"Site '{site_modifie.name}' (ID : {site_modifie.pk}) modifié. "
                    f"Changements appliqués sur les champs."
                )
            )

            messages.success(request, "Le site a été mis à jour avec succès.")
            return redirect('liste_websites')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = WebsiteForm(instance=site)

    return render(request, "Administrateur/modifier_website.html", {
        'form': form,
        'site': site
    })


@login_required
def supprimer_website(request, pk):
    """
    Confirmation et suppression d'un site, puis historique.
    """
    site = get_object_or_404(Websites, pk=pk, is_visible=True)

    if request.method == 'POST':
        # On ne supprime pas physiquement pour auditabilité
        site.is_visible = False
        site.save()

        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un site web",
            objet="Websites",
            details=f"Site '{site.name}' (ID : {site.pk}) masqué (is_visible=False)."
        )

        messages.success(request, "Le site a été supprimé avec succès.")
        return redirect('liste_websites')

    return render(request, "Administrateur/confirmer_supprimer_website.html", {
        'site': site
    })





from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404



@login_required
def liste_supports(request):
    supports = Supports.objects.order_by('-date_created')
    return render(request, "Administrateur/liste_supports.html", {
        'supports': supports
    })

@login_required
def ajouter_support(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            support = form.save()
            # Historique
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Ajout d'un support",
                objet="Supports",
                details=f"Support « {support.name} » créé (prix : {support.prix} MAD)."
            )
            messages.success(request, "Le support a été ajouté avec succès.")
            return redirect('liste_supports')
        messages.error(request, "Merci de corriger les erreurs ci-dessous.")
    else:
        form = SupportForm()
    return render(request, "Administrateur/ajouter_support.html", {'form': form})

@login_required
def modifier_support(request, pk):
    support = get_object_or_404(Supports, pk=pk)
    if request.method == 'POST':
        form = SupportForm(request.POST, instance=support)
        if form.is_valid():
            support_mod = form.save()
            HistoriqueAction.objects.create(
                utilisateur=request.user,
                action="Modification d'un support",
                objet="Supports",
                details=f"Support « {support_mod.name} » (ID {support_mod.pk}) modifié."
            )
            messages.success(request, "Le support a été mis à jour avec succès.")
            return redirect('liste_supports')
        messages.error(request, "Merci de corriger les erreurs ci-dessous.")
    else:
        form = SupportForm(instance=support)
    return render(request, "Administrateur/modifier_support.html", {
        'form': form,
        'support': support
    })



@login_required
def supprimer_support(request, pk):
    support = get_object_or_404(Supports, pk=pk)
    if request.method == 'POST':
        # Suppression définitive (ou basculez un flag 'actif' si vous préférez)
        support.delete()
        HistoriqueAction.objects.create(
            utilisateur=request.user,
            action="Suppression d'un support",
            objet="Supports",
            details=f"Support « {support.name} » (ID {support.pk}) supprimé."
        )
        messages.success(request, "Le support a été supprimé avec succès.")
        return redirect('liste_supports')
    return render(request, "Administrateur/confirmer_supprimer_support.html", {
        'support': support
    })








from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q

def tickets_list(request):
    tickets = Ticket.objects.all()

    # 🔍 Recherche rapide
    search_query = request.GET.get('search')
    if search_query:
        tickets = tickets.filter(
            Q(code_Ticket__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(typeTicket__icontains=search_query) |
            Q(Branche__icontains=search_query) |
            Q(cliente__user__username__icontains=search_query)
        )

    # ✅ Filtres
    status     = request.GET.get('status')
    typeTicket = request.GET.get('typeTicket')
    branche    = request.GET.get('Branche')
    cliente_id = request.GET.get('cliente')
    date_start = request.GET.get('date_start')
    date_end   = request.GET.get('date_end')

    if status and status != 'None':
        tickets = tickets.filter(status=status)
    if typeTicket and typeTicket != 'None':
        tickets = tickets.filter(typeTicket=typeTicket)
    if branche and branche != 'None':
        tickets = tickets.filter(Branche=branche)
    if cliente_id and cliente_id != 'None':
        tickets = tickets.filter(cliente_id=cliente_id)
    if date_start and date_end:
        tickets = tickets.filter(date_created__date__range=[date_start, date_end])

    # 🔃 Tri
    sort_by = request.GET.get('sort_by')
    if sort_by == 'date_asc':
        tickets = tickets.order_by('date_created')
    elif sort_by == 'date_desc':
        tickets = tickets.order_by('-date_created')
    else:
        tickets = tickets.order_by('-date_created')

    context = {
        'tickets'        : tickets,
        'status_choices' : Ticket.STATUS_CHOICES,
        'type_choices'   : Ticket.objects.values_list('typeTicket', flat=True).distinct(),
        'branche_choices': Ticket.objects.values_list('Branche',    flat=True).distinct(),
        'clientes'       : Ticket.objects.values_list('cliente__id','cliente__user__username').distinct(),
        'search_query'   : search_query,
        'status'         : status,
        'typeTicket'     : typeTicket,
        'branche'        : branche,
        'cliente_id'     : cliente_id,
        'date_start'     : date_start,
        'date_end'       : date_end,
        'sort_by'        : sort_by,
    }
    return render(request, 'Administrateur/tickets_list.html', context)




def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    conversations = ticket.conversations.order_by('timestamp')

    context = {
        'ticket': ticket,
        'conversations': conversations,
    }
    return render(request, 'Administrateur/ticket_detail.html', context)




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import io

def ticket_pdf(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    conversations = ticket.conversations.order_by('timestamp')

    template_path = 'Administrateur/detail_ticket_pdf.html'
    context = {'ticket': ticket, 'conversations': conversations}
    template = get_template(template_path)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{ticket.code_Ticket}.pdf"'

    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)

    if not pdf.err:
        response.write(result.getvalue())
        return response
    else:
        return HttpResponse("Erreur lors de la génération du PDF", status=500)
