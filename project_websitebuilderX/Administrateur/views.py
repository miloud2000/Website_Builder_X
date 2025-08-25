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




#DashbordHome of Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Administrateur']) 
def dashbordHomeAdministrateur(request):  
    return render(request, "Administrateur/dashbordHomeAdministrateur.html")


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
    supports = SupportTechnique.objects.all().order_by('-date_created')
    return render(request, 'Administrateur/liste_support_technique.html', {'supports': supports})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.text import slugify

@login_required
def ajouter_support_technique(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Ce nom d'utilisateur existe déjà.")
        else:
            # Création du compte utilisateur
            user = User.objects.create_user(username=username, password=password, email=email)

            # Ajout au groupe "SupportTechnique"
            group = Group.objects.get(name="SupportTechnique")
            user.groups.add(group)

            # Création du modèle SupportTechnique
            support = SupportTechnique.objects.create(
                user=user,
                name=name,
                email=email,
                phone=phone,
                Status='Active',
                slugSupportTechnique=slugify(username)
            )

            # Historique
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
