from django.shortcuts import render,redirect
from .models import *
from .forms import ClienteForm,AdministrateurForm,SupportTechniqueForm,GestionnaireComptesForm,DemandeRechargerForm,ClienteForm,AdditionalInfoForm,ClienteUpdateForm,ClientePasswordChangeForm
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .decorators import notLoggedUsers,allowedUsers,forAdmins
from django.contrib.auth import authenticate,logout
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .decorators import user_not_authenticated,anonymous_required
from django.contrib.auth import login, logout, authenticate, get_user_model
from .tokens import account_activation_token
from django.shortcuts import render, get_object_or_404
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.utils.html import strip_tags






@anonymous_required
def home2(request):
    return render(request, "websitebuilder/home2.html")




from websitebuilder.models import (
    DemandeRecharger, Cliente,
    AchatWebsites, LocationWebsites, GetFreeWebsites
)


@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def dashbordHome(request):  
    cliente = request.user.cliente
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    AchatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')[:5]
    context = {
        'WebsiteBuilders': WebsiteBuilders,
        'AchatSupports': AchatSupports,
    }
    return render(request, "clients/dashbordHome.html",context)





def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(request, "Thank you for your email confirmation. Now you can login your account.")
        return redirect('user_login')
    else:
        messages.error(request, "Activation link is invalid!")

    return redirect('home')





from django.utils.safestring import mark_safe


def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string("websitebuilder/template_activate_account.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        "protocol": 'https' if request.is_secure() else 'http'
    })
    
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        message = mark_safe(f'Dear <b>{user}</b>, please go to your email <b>{to_email}</b> inbox and click on \
                    received activation link to confirm and complete the registration. <b>Note:</b> Check your spam folder.')
        messages.success(request, message)  
    else:
        messages.error(request, f'Problem sending email to {to_email}, check if you typed it correctly.')
    
    
    
    
#Login and register and Logout

#register of cliente
@notLoggedUsers   
def register(request):
    form = ClienteForm()
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()
            cliente = Cliente.objects.create(
                user=user,
                prenom=form.cleaned_data.get('prenom'),
                nom=form.cleaned_data.get('nom'),
                email=form.cleaned_data.get('email'),
                phone=form.cleaned_data.get('phone')
            )

            group = Group.objects.get(name="Cliente")
            user.groups.add(group)
            activateEmail(request, user, form.cleaned_data.get('email'))
            return redirect('home')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

    else:
        form = ClienteForm()
        
    context = {'form': form}
    return render(request, "websitebuilder/register.html", context)


@notLoggedUsers
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Vérification des statuts pour les groupes restreints
            if user.groups.filter(name='SupportTechnique').exists():
                from websitebuilder.models import SupportTechnique
                try:
                    support = SupportTechnique.objects.get(user=user)
                    if support.Status != 'Active':
                        messages.error(request, "Votre compte SupportTechnique n'est pas actif.")
                        return redirect('user_login')
                except SupportTechnique.DoesNotExist:
                    messages.error(request, "Compte SupportTechnique introuvable.")
                    return redirect('user_login')

            elif user.groups.filter(name='GestionnaireComptes').exists():
                from websitebuilder.models import GestionnaireComptes
                try:
                    gestionnaire = GestionnaireComptes.objects.get(user=user)
                    if gestionnaire.Status != 'Active':
                        messages.error(request, "Votre compte GestionnaireComptes n'est pas actif.")
                        return redirect('user_login')
                except GestionnaireComptes.DoesNotExist:
                    messages.error(request, "Compte GestionnaireComptes introuvable.")
                    return redirect('user_login')

            elif user.groups.filter(name='Administrateur').exists():
                from websitebuilder.models import Administrateur
                try:
                    admin = Administrateur.objects.get(user=user)
                    if admin.Status != 'Active':
                        messages.error(request, "Votre compte Administrateur n'est pas actif.")
                        return redirect('user_login')
                except Administrateur.DoesNotExist:
                    messages.error(request, "Compte Administrateur introuvable.")
                    return redirect('user_login')

            elif user.groups.filter(name='Commercial').exists():
                from websitebuilder.models import Commercial
                try:
                    commercial = Commercial.objects.get(user=user)
                    if commercial.status != 'Active':
                        messages.error(request, "Votre compte Commercial n'est pas actif.")
                        return redirect('user_login')
                except Commercial.DoesNotExist:
                    messages.error(request, "Compte Commercial introuvable.")
                    return redirect('user_login')

            # ✅ Si tout est bon, on connecte
            login(request, user)

            if user.groups.filter(name='Cliente').exists():
                return redirect('/dashbordHome')
            if user.groups.filter(name='SupportTechnique').exists():
                return redirect('/homeSupportTechnique')
            if user.groups.filter(name='GestionnaireComptes').exists():
                return redirect('/homeGestionnairesComptes')
            if user.groups.filter(name='Administrateur').exists():
                return redirect('/homeAdministrateur')
            if user.groups.filter(name='Commercial').exists():
                return redirect('/homeCommercial')
            if user.groups.filter(name='SuperAdmin').exists():
                return redirect('homeSuperAdmin')

        else:
            messages.error(request, 'Email ou mot de passe invalide.')

    return render(request, "websitebuilder/login.html")




from django.contrib.auth.decorators import login_required

#Logout for all
def userLogout(request):
   logout(request)
   return redirect('home2')






# #Cliente


# #DashbordHome of Cliente
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def dashbordHome(request):  
#     cliente = request.user.cliente
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     AchatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')[:5]
#     context = {
#         'WebsiteBuilders': WebsiteBuilders,
#         'AchatSupports': AchatSupports,
#     }
#     return render(request, "websitebuilder/Cliente/dashbordHome.html",context)



# # def dashboard(request):  
# #     latest_website_builders = []

# #     if request.user.is_authenticated:
# #         for achat in request.user.cliente.achatwebsites_set.filter(BuilderStatus='Builder'):
# #             latest_website_builders.extend(achat.websitebuilder_set.all())

# #     # Slice the list to get only the latest 5 instances
# #     latest_website_builders = latest_website_builders[-2:]

# #     context = {
# #         'latest_website_builders': latest_website_builders,
# #     }
# #     return render(request, "websitebuilder/Cliente/dashboard2.html",context)



# def dashboard(request):  
#     return render(request, "websitebuilder/Cliente/dashboard.html")



# # def dashboard2(request): 
# #     cliente = request.user.cliente
# #     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:5]
# #     context = {
# #         'WebsiteBuilders': WebsiteBuilders,
# #     } 
# #     return render(request, "websitebuilder/Cliente/dashboard2.html",context)


# def editUser(request):  
#     return render(request, "websitebuilder/Cliente/editUser.html")


# #Edit and display client information
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def detailUser(request):  
#     cliente = request.user.cliente 
#     AchatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')[:2]
#     AchatWebsitess = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')[:2]
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

#     context = {
#         'cliente': cliente,
#         'AchatSupports': AchatSupports,
#         'AchatWebsitess': AchatWebsitess,
#         'WebsiteBuilders': WebsiteBuilders,
#     }
#     return render(request, "websitebuilder/Cliente/detailUser.html", context)



# #Edit client more information [address,nom_entreprise,...]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_additional_info(request):
#     if request.method == 'POST':
#         address = request.POST.get('address')
#         nom_entreprise = request.POST.get('nom_entreprise')
#         numero_ice = request.POST.get('numero_ice')

#         cliente = request.user.cliente
#         cliente.address = address
#         cliente.nom_entreprise = nom_entreprise
#         cliente.numero_ice = numero_ice
#         cliente.save()

#         messages.success(request, "Additional information added successfully!")
#         return redirect('detailUser')
#     else:
#         form = AdditionalInfoForm()

#     return render(request, 'websitebuilder/Cliente/detailUser.html', {'form': form})




# #Edit client more information [nom,prenom,...]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def update_cliente(request):
#     cliente = request.user.cliente  
#     if request.method == 'POST':
#         prenom = request.POST.get('prenom')
#         nom = request.POST.get('nom')
#         email = request.POST.get('email')
#         phone = request.POST.get('phone')

#         cliente = request.user.cliente
#         cliente.prenom = prenom
#         cliente.nom = nom
#         cliente.email = email
#         cliente.phone = phone
#         cliente.save()
        
#         messages.success(request, "Client updated successfully!")
#         return redirect('detailUser')
#     else:
#         cliente_form = ClienteUpdateForm()

#     return render(request, 'websitebuilder/Cliente/detailUser.html', {'cliente_form': cliente_form})



# from django.contrib.auth import update_session_auth_hash


# #Edit password for client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def change_password(request):
#     cliente = request.user.cliente 

#     if request.method == 'POST':
#         form = ClientePasswordChangeForm(request.user, request.POST)  
#         if form.is_valid():
#             form.save()
#             update_session_auth_hash(request, request.user)  
#             messages.success(request, 'Your password was successfully updated!')
#             return redirect('/detailUser')  
#         else:
#             messages.error(request, 'Please rewrite old password is not correct.')
#             return redirect('/detailUser')  
#     else:
#         form = ClientePasswordChangeForm(request.user)  
    
#     return render(request, 'websitebuilder/Cliente/detailUser.html', {'form': form})




# #List of websites that are displayed to the client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_websites(request): 
#     cliente = request.user.cliente  
#     websites = Websites.objects.all()
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'websites': websites,
#         'WebsiteBuilders': WebsiteBuilders,
#         }  
#     return render(request, "websitebuilder/Cliente/list_websites.html",context)




# #More detail of website
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def detail_website(request, slugWebsites):
#     if request.user.is_authenticated:
#         is_Cliente = request.user.groups.filter(name='Cliente').exists()
#         is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
#         is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
#     else: 
#         is_Cliente= False  
#         is_SupportTechnique= False 
#         is_Administrateur= False  
        
#     website_info = get_object_or_404(Websites, slugWebsites=slugWebsites)
    
#     context = {
#         'website_info': website_info,
#         "is_Cliente": is_Cliente,
#         "is_SupportTechnique":is_SupportTechnique,
#         "is_Administrateur":is_Administrateur
#     }
#     return render(request, "websitebuilder/Cliente/detail_website.html", context)




# #List of All websites that are displayed to the client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def all_list_websites(request):
#     if request.user.is_authenticated:
#         is_Cliente = request.user.groups.filter(name='Cliente').exists()
#         is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
#         is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
#     else:
#         is_Cliente = False  
#         is_SupportTechnique = False 
#         is_Administrateur = False  

#     category = request.GET.get('category', 'All')
#     cms_filter = request.GET.get('cms', '')
#     langues_filter = request.GET.get('langues', '')
#     plan_filter = request.GET.get('plan', '')

#     websites = Websites.objects.all()

#     if category != 'All' and category != '*':
#         websites = websites.filter(catégorie=category)
    
#     if cms_filter:
#         websites = websites.filter(CMS=cms_filter)
    
#     if langues_filter:
#         websites = websites.filter(langues=langues_filter)
    
#     if plan_filter:
#         websites = websites.filter(plan=plan_filter)
    
#     context = {
#         'websites': websites,
#         "is_Cliente": is_Cliente,
#         "is_SupportTechnique": is_SupportTechnique,
#         "is_Administrateur": is_Administrateur,
#         "selected_category": category,
#         "cms_filter": cms_filter,
#         "langues_filter": langues_filter,
#         "plan_filter": plan_filter,
#     }

#     return render(request, 'websitebuilder/Cliente/all_list_websites.html', context)



# #List of Supports that are displayed to the client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_services(request):
#     cliente = request.user.cliente  
#     supports = Supports.objects.all()
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'supports': supports,
#         'WebsiteBuilders': WebsiteBuilders,
#         } 
#     return render(request, "websitebuilder/Cliente/list_services.html",context)


# from itertools import chain


# #List of all services owned by the registered client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def MesServices(request):  
#     cliente = request.user.cliente
#     achat_supports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')
#     achat_websites = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     location_websites = LocationWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     getfree_website = GetFreeWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

#     combined_websites = sorted(
#         chain(
#             achat_websites,
#             location_websites,
#             getfree_website
#         ),
#         key=lambda instance: instance.date_created,
#         reverse=True
#     )

#     context = {
#         'achat_supports': achat_supports,
#         'achat_websites': achat_websites,
#         'location_websites': location_websites,
#         'getfree_website': getfree_website,
#         'combined_websites': combined_websites,
#         'WebsiteBuilders': WebsiteBuilders,
#     }
#     return render(request, "websitebuilder/Cliente/MesServices.html", context)




# #List of all webSites owned by the registered client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def WebSites(request): 
#     cliente = request.user.cliente
#     achats = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     locations = LocationWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     frees = GetFreeWebsites.objects.filter(cliente=cliente).order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

#     website_builders = WebsiteBuilder.objects.filter(cliente=cliente)
#     location_website_builders = LocationWebsiteBuilder.objects.filter(cliente=cliente)
#     free_website_builders = GetFreeWebsiteBuilder.objects.filter(cliente=cliente)


#     context = {
#         'achats': achats,
#         'locations': locations,
#         'website_builders': website_builders,
#         'location_website_builders':location_website_builders,
#         'WebsiteBuilders': WebsiteBuilders,
#         'free_website_builders' :free_website_builders,
#         'frees': frees,
#     } 
#     return render(request, "websitebuilder/Cliente/WebSites.html", context)






# #List of all supports owned by the registered client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def Services(request):
#     cliente = request.user.cliente
#     achatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'achatSupports': achatSupports,
#         'WebsiteBuilders': WebsiteBuilders,
#     }   
#     return render(request, "websitebuilder/Cliente/Services.html",context)




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def solde_et_facturation(request): 
#     cliente = request.user.cliente   
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     facturations = Facturations.objects.filter(cliente=cliente).order_by('-date_created')
#     context = {
#         'WebsiteBuilders': WebsiteBuilders,
#         'facturations': facturations,
#     } 
#     return render(request, "websitebuilder/Cliente/solde_et_facturation.html",context)




# from django.http import HttpResponse
# from django.template.loader import get_template
# from django.shortcuts import get_object_or_404
# from weasyprint import HTML, CSS
# from django.contrib.auth.decorators import login_required


# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def generate_facturation_pdf(request, facturation_id):
#     facturation = get_object_or_404(Facturations, id=facturation_id)
#     template_path = 'websitebuilder/Cliente/facturation_pdf_template.html'
#     context = {'facturation': facturation}

#     # Render the template to HTML
#     html_template = get_template(template_path)
#     html_string = html_template.render(context)

#     # Create a PDF file
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename="facturation_{facturation.cliente.user.username}_{facturation.code_facturation}.pdf"'

#     # Load CSS separately to ensure it is applied
#     # css_urls = [
#     #     'https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0-alpha.6/css/bootstrap.min.css',
#     # ]
#     # css_stylesheets = [CSS(url) for url in css_urls]

#     HTML(string=html_string).write_pdf(response)

#     return response




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def paiement(request):  
#     cliente = request.user.cliente   
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'WebsiteBuilders': WebsiteBuilders,
#     } 
#     return render(request, "websitebuilder/Cliente/paiement.html",context)




# #Can the client create request Reload "Demande Recharger"
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def create_demande_recharger(request):
#     cliente = request.user.cliente  
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     if request.method == 'POST':
#         form = DemandeRechargerForm(request.POST, request.FILES)
#         if form.is_valid():
#             demande_recharger = form.save(commit=False)
#             demande_recharger.cliente = request.user.cliente
#             demande_recharger.save()
#             messages.success(request, "Demande Recharger in progress, please wait ...")
#             return redirect('list_demande_recharger')
#         else:
#             messages.error(request, "There was an error with your form. Please check the details and try again.")
#     else:
#         form = DemandeRechargerForm()
    
#     return render(request, 'websitebuilder/Cliente/create_demande_recharger.html', {'form': form,'WebsiteBuilders':WebsiteBuilders})



# #List of all request Reload "Demande Recharger" owned by the registered client
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_demande_recharger(request):
#     cliente = request.user.cliente
#     list_demande_rechargers = DemandeRecharger.objects.filter(cliente=cliente).order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'list_demande_rechargers': list_demande_rechargers,
#         'WebsiteBuilders': WebsiteBuilders,
#     }
   
#     return render(request, 'websitebuilder/Cliente/list_demande_recharger.html',context)





# #List of all Demande Recharger owned by the registered client and status is "not done yet"
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_Demande_Recharger_En_attente(request): 
#     cliente = request.user.cliente
#     DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='Not Done yet').order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'DemandeRechargers': DemandeRechargers,
#         'WebsiteBuilders': WebsiteBuilders,
#         } 
#     return render(request, "websitebuilder/Cliente/list_Demande_Recharger_En_attente.html",context)




# #List of all Demande Recharger owned by the registered client and status is "done"
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_Demande_Recharger_Complete(request): 
#     cliente = request.user.cliente
#     DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='Done').order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'DemandeRechargers': DemandeRechargers,
#         'WebsiteBuilders': WebsiteBuilders,
#         } 
#     return render(request, "websitebuilder/Cliente/list_Demande_Recharger_Complete.html",context)




# #List of all Demande Recharger owned by the registered client and status is "inacceptable"
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def list_Demande_Recharger_Annule(request): 
#     cliente = request.user.cliente
#     DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='inacceptable').order_by('-date_created')
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
#     context = {
#         'DemandeRechargers': DemandeRechargers,
#         'WebsiteBuilders': WebsiteBuilders,
#         } 
#     return render(request, "websitebuilder/Cliente/list_Demande_Recharger_Annule.html",context)




# from django.db.models import F

# #The client can buy a website ,Maybe i need deleted this becuase i use just confirm_Achat_website
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def Achat_website(request, website_id):
#     try:
#         website = Websites.objects.get(pk=website_id)
#         cliente = request.user.cliente  
#         if cliente.solde >= website.prix:
#             # Create a table in the Achat model
#             AchatWebsites.objects.create(cliente=cliente, websites=website, solde=website.prix)
#             messages.success(request, f"Website {website.name} Achat successfully!")
            
#             #Need deleted from this code because I add it in models.py
#             # cliente.solde -= website.prix  
#             # cliente.save()  
#             return redirect('/WebSites')
#         else:
#             messages.error(request, "Insufficient balance to purchase this website.")
#             return redirect('/list_websites')
#     except Websites.DoesNotExist:
#         messages.error(request, "Website does not exist.")
#     except Cliente.DoesNotExist:
#         messages.error(request, "Client does not exist.")
#     return redirect('/WebSites')



# from django.utils import formats



# # Email sending function send_email_Achat_website
# def send_email_Achat_website(request, cliente, websiteName,websiteDate,websitePrix):
#     mail_subject = "Achat Website successfully"
#     formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
#     formatted_price = formats.number_format(websitePrix)
    
#     message = render_to_string("websitebuilder/send_email_Achat_website.html", {
#         'user': cliente.user.username,
#         'name_website': websiteName,
#         'date_website': formatted_date,
#         'prix_website': formatted_price,
#         'domain': get_current_site(request).domain,
#         "protocol": 'https' if request.is_secure() else 'http'
#     })

#     email = EmailMessage(mail_subject, message, to=[cliente.user.email])
#     email.content_subtype = "html"  
    
#     if email.send():
#         success_message = mark_safe(
#             f'Dear <b>{cliente.user.username}</b>, Website Achat<b>{websiteName}</b> has been successfully . '
#             f'Please check your email <b>{cliente.user.email}</b> for more details.'
#         )
#         messages.success(request, success_message)
#     else:
#         messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




# #The client can buy a website, but after confirming
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def confirm_Achat_website(request):
#     if request.method == 'POST':
#         website_id = request.POST.get('website_id')
#         try:
#             website = Websites.objects.get(pk=website_id)
#             cliente = Cliente.objects.get(user=request.user)
#             if cliente.solde >= website.prix:
#                 # Create a table in the AchatWebsites model
#                 achat_website = AchatWebsites.objects.create(cliente=cliente, websites=website, prix_achat=website.prix)
#                 # Send email
#                 send_email_Achat_website(request, cliente, website.name, achat_website.date_created, achat_website.prix_achat)

#                 # messages.success(request, f"Website {website.name} purchased successfully!")
#             else:
#                 messages.error(request, "Insufficient balance to purchase this website.")
#                 return redirect('/list_websites')
#         except Cliente.DoesNotExist:
#             messages.error(request, "Client does not exist.")
#         except Websites.DoesNotExist:
#             messages.error(request, "Website does not exist.")
#     return redirect('/WebSites')






# # Email sending function send_email_GetFree_website
# def send_email_GetFree_website(request, cliente, websiteName,websiteDate,websitePrix):
#     mail_subject = "Get Free Website successfully"
#     formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
#     formatted_price = formats.number_format(websitePrix)
    
#     message = render_to_string("websitebuilder/send_email_GetFree_website.html", {
#         'user': cliente.user.username,
#         'name_website': websiteName,
#         'date_website': formatted_date,
#         'prix_website': formatted_price,
#         'domain': get_current_site(request).domain,
#         "protocol": 'https' if request.is_secure() else 'http'
#     })

#     email = EmailMessage(mail_subject, message, to=[cliente.user.email])
#     email.content_subtype = "html"  
    
#     if email.send():
#         success_message = mark_safe(
#             f'Dear <b>{cliente.user.username}</b>, Website Achat<b>{websiteName}</b> has been successfully . '
#             f'Please check your email <b>{cliente.user.email}</b> for more details.'
#         )
#         messages.success(request, success_message)
#     else:
#         messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')



# # The client can Get it Free a website
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def GetFree_website(request):
#     if request.method == 'POST':
#         website_id = request.POST.get('website_id')
#         try:
#             website = Websites.objects.get(pk=website_id)
#             cliente = Cliente.objects.get(user=request.user)
#             if cliente.solde >= website.prix:
#                 try:
#                     getfree_website = GetFreeWebsites.objects.create(cliente=cliente, websites=website, prix_free=website.prix)
#                     messages.success(request, f"Website {website.name} purchased successfully!")
#                     # Send email
#                     send_email_GetFree_website(request, cliente, website.name, getfree_website.date_created, getfree_website.prix_free)
#                 except ValidationError as e:
#                     #Error for get more than 1 website Free
#                     error_message = e.messages[0]
#                     messages.error(request, error_message)
#             else:
#                 messages.error(request, "Insufficient balance to purchase this website.")
#                 return redirect('/list_websites')
#         except Cliente.DoesNotExist:
#             messages.error(request, "Client does not exist.")
#         except Websites.DoesNotExist:
#             messages.error(request, "Website does not exist.")
#     return redirect('/WebSites')





# # Email sending function send_email_loyer_website
# def send_email_loyer_website(request, cliente, websiteName,websiteDate,websiteDateFine,websitePrix):
#     mail_subject = "Location Website successfully"
#     formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
#     formatted_dateFin = formats.date_format(websiteDateFine, "DATETIME_FORMAT")
#     formatted_price = formats.number_format(websitePrix)
    
#     message = render_to_string("websitebuilder/send_email_loyer_website.html", {
#         'user': cliente.user.username,
#         'name_website': websiteName,
#         'date_website': formatted_date,
#         'DateFine_website': formatted_dateFin,
#         'prix_website': formatted_price,
#         'domain': get_current_site(request).domain,
#         "protocol": 'https' if request.is_secure() else 'http'
#     })

#     email = EmailMessage(mail_subject, message, to=[cliente.user.email])
#     email.content_subtype = "html"  
    
#     if email.send():
#         success_message = mark_safe(
#             f'Dear <b>{cliente.user.username}</b>, Website Location <b>{websiteName}</b> has been successfully . '
#             f'Please check your email <b>{cliente.user.email}</b> for more details.'
#         )
#         messages.success(request, success_message)
#     else:
#         messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




# #confirm_loyer_website loyer website with chose period of loyer with prix 
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def confirm_loyer_website(request):
#     if request.method == 'POST':
#         website_id = request.POST.get('website_id')
#         rental_period = int(request.POST.get('rental_period', 1))  # Default to 1 month if not provided
#         website = get_object_or_404(Websites, pk=website_id)
#         cliente = request.user.cliente
        
#         total_price = website.prix_loyer * rental_period

#         # Check if the cliente has enough solde
#         if cliente.solde < total_price:
#             messages.error(request, "You do not have enough solde to rent this website.")
#             return redirect('list_websites')  
        
#         # Create the LocationWebsites
#         date_debut = timezone.now()
#         date_fin = date_debut + timedelta(days=30 * rental_period)
#         Location_website = LocationWebsites.objects.create(
#             cliente=cliente,
#             websites=website,
#             prix_loyer=total_price,
#             date_debut=date_debut,
#             date_fin=date_fin
#         )
        
#         cliente.solde -= total_price
#         cliente.save()
        
#         # Send email
#         send_email_loyer_website(request, cliente, website.name, date_debut, date_fin, total_price)
#         messages.success(request, "Website rented successfully.")
#         return redirect('WebSites')  
#     else:
#         messages.error(request, "Invalid request.")
#         return redirect('list_websites')




# #The client can buy a support, Maybe i need deleted this because i use just confirm_Achat_support
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def Achat_support(request, support_id):
#     if request.user.is_authenticated:
#         try:
#             support = Supports.objects.get(pk=support_id)
#             cliente = Cliente.objects.get(user=request.user)
#             if cliente.solde >= support.prix:
#                 # Create a table in the AchatSupport model
#                 AchatSupport.objects.create(cliente=cliente, support=support, solde=support.prix)
#                 messages.success(request, f"Support {support.name} purchased successfully!")
#                 return redirect('/Services')
#             else:
#                 messages.error(request, "Insufficient balance to purchase this support.")
#                 return redirect('/list_services')
#         except Supports.DoesNotExist:
#             messages.error(request, "Support does not exist.")
#             return redirect('/list_services')
#         except Cliente.DoesNotExist:
#             messages.error(request, "Client does not exist.")
#             return redirect('/list_services')
#     else:
#         messages.error(request, "You need to be logged in to purchase a Support.")
#         return redirect('/Services')




# #The client can buy a support, but after confirming
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def confirm_Achat_support(request):
#     if request.method == 'POST':
#         support_id = request.POST.get('support_id')
#         try:
#             support = Supports.objects.get(pk=support_id)
#             cliente = Cliente.objects.get(user=request.user)
#             if cliente.solde >= support.prix:
#                 # Create a table in the AchatSupport model
#                 AchatSupport.objects.create(cliente=cliente, support=support, prix=support.prix)
#                 messages.success(request, f"Support {support.name} purchased successfully!")
#                 return redirect('/Services')
#             else:
#                 messages.error(request, "Insufficient balance to purchase this support.")
#         except Cliente.DoesNotExist:
#             messages.error(request, "Client does not exist.")
#         except Supports.DoesNotExist:
#             messages.error(request, "Support does not exist.")
#     return redirect('/Services')




# # # The client can activate a support
# # @login_required(login_url='login')
# # @allowedUsers(allowedGroups=['Cliente'])
# # def consome_demande_support(request, support_id):
# #     if request.method == 'POST':
# #         try:
# #             cliente = Cliente.objects.get(user=request.user)
# #             achat_support = AchatSupport.objects.get(pk=support_id)
            
# #             if achat_support.Status == 'No Active':
# #                 achat_support.Status = 'Active'
# #                 achat_support.save()
                
# #                 # Create DemandeSupport
# #                 code_DemandeSupport = generate_DemandeSupport_code(cliente.nom, cliente.prenom, achat_support.support.name)
# #                 demande_support = DemandeSupport.objects.create(
# #                     cliente=cliente,
# #                     achat_support=achat_support,
# #                     status='Not Done yet', 
# #                     code_DemandeSupport=code_DemandeSupport
# #                 )

# #                 # Send email to the client
# #                 # Uncomment and customize the send_email_support_active function as needed
# #                 # send_email_support_active(request, cliente, demande_support.code_DemandeSupport)

# #                 messages.success(request, "Support consumed successfully and email sent to the client.")
# #                 return redirect('/Services') 
# #             else:
# #                 messages.error(request, "Support is already consumed.")
# #         except AchatSupport.DoesNotExist:
# #             messages.error(request, "AchatSupport with the specified ID does not exist.")
# #         except Cliente.DoesNotExist:
# #             messages.error(request, "Cliente with the specified ID does not exist.")

# #     return redirect('/Services')




# # Email sending send_email_support_active function
# def send_email_support_active(request, cliente, code_DemandeSupport):
#     mail_subject = "Support Active Confirmation"
#     message = render_to_string("websitebuilder/send_email_support_active.html", {
#         'user': cliente.user.username,
#         'support_code': code_DemandeSupport,
#         'domain': get_current_site(request).domain,
#         "protocol": 'https' if request.is_secure() else 'http'
#     })

#     email = EmailMessage(mail_subject, message, to=[cliente.user.email])
#     email.content_subtype = "html"  
    
#     if email.send():
#         success_message = mark_safe(
#             f'Dear <b>{cliente.user.username}</b>, the support with code <b>{code_DemandeSupport}</b> has been successfully activated. '
#             f'Please check your email <b>{cliente.user.email}</b> for more details.'
#         )
#         messages.success(request, success_message)
#     else:
#         messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def confirm_consome_demande_support(request):
#     if request.method == 'POST':
#         support_id = request.POST.get('support_id')
#         try:
#             achat_support = AchatSupport.objects.get(pk=support_id)
#             cliente = Cliente.objects.get(user=request.user)

#             if achat_support.Status == 'No Active':
#                 achat_support.Status = 'Active'
#                 achat_support.save()

#                 # Create DemandeSupport
#                 code_DemandeSupport = generate_DemandeSupport_code(cliente.nom, cliente.prenom, achat_support.support.name)
#                 demande_support = DemandeSupport.objects.create(
#                     cliente=cliente,
#                     achat_support=achat_support,
#                     status='Not Done yet',
#                     code_DemandeSupport=code_DemandeSupport
#                 )

#                 # Send confirmation email
#                 send_email_support_active(request, cliente, demande_support.code_DemandeSupport)
#                 messages.success(request, "Support activated successfully and email sent with the Demande Support code.")
#             else:
#                 messages.error(request, "Support is already active.")
#         except AchatSupport.DoesNotExist:
#             messages.error(request, "AchatSupport with the specified ID does not exist.")
#         except Cliente.DoesNotExist:
#             messages.error(request, "Cliente with the specified ID does not exist.")

#     return redirect('/Services')



# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def add_websiteBuilder(request):
#     if request.method == 'POST':
#         name_website = request.POST.get('nameWebsite')
#         cliente_id = request.POST.get('cliente_id')
#         achat_website_id = request.POST.get('website_id')
        
#         # Check if the nameWebsite already exists
#         if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
#             messages.error(request, 'A Name of a website with this name already exists choose another name of your website.')
#             return redirect('WebSites') 
        
#         achat_website = get_object_or_404(AchatWebsites, pk=achat_website_id)
        
#         # Create a new WebsiteBuilder
#         website_builder = WebsiteBuilder.objects.create(
#             nameWebsite=name_website,
#             cliente_id=cliente_id,
#             achat_website=achat_website
#         )
        
        
#         # Create a new MergedWebsiteBuilder
#         MergedWebsiteBuilder.objects.create(
#             cliente_id=cliente_id,
#             website_builder=website_builder,
#             website=achat_website.websites
#         )
        
#         achat_website.BuilderStatus = 'in progress'
#         achat_website.save()
        
        
#         messages.success(request, 'Website in the progress of builder please wait 1 minute and your website will be built.')
#         return redirect('WebSites') 
#     else:
#         return render(request, 'websitebuilder/Cliente/WebSites.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def add_GetFreeWebsiteBuilder(request):
#     if request.method == 'POST':
#         name_website = request.POST.get('nameWebsite')
#         cliente_id = request.POST.get('cliente_id')
#         getfree_website_id = request.POST.get('website_id')
        
#         if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
#             messages.error(request, 'A Name of a website with this name already exists choose another name of your website.')
#             return redirect('WebSites') 
        
#         getfree_website = get_object_or_404(GetFreeWebsites, pk=getfree_website_id)
        
#         # Create a new GetFreeWebsiteBuilder
#         getfree_website_builder = GetFreeWebsiteBuilder.objects.create(
#             nameWebsite=name_website,
#             cliente_id=cliente_id,
#             getfree_website=getfree_website
#         )
        
#         # Create a new MergedWebsiteBuilder
#         MergedWebsiteBuilder.objects.create(
#             cliente_id=cliente_id,
#             getfree_website_builder=getfree_website_builder,
#             website=getfree_website_builder.website
#         )
        
#         getfree_website.BuilderStatus = 'in progress'
#         getfree_website.save()

#         messages.success(request, 'Website in the progress of builder please wait 1 minute and your website will be built.')
#         return redirect('WebSites') 
#     else:
#         return render(request, 'websitebuilder/Cliente/WebSites.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def add_locationWebsiteBuilder(request):
#     if request.method == 'POST':
#         name_website = request.POST.get('nameWebsite')
#         cliente_id = request.POST.get('cliente_id')
#         location_website_id = request.POST.get('website_id')
        
#         # Check if the nameWebsite already exists
#         if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
#             messages.error(request, 'A website with this name already exists, please choose another name.')
#             return redirect('WebSites')
        
#         location_website = get_object_or_404(LocationWebsites, pk=location_website_id)
        
#         # Create a new LocationWebsiteBuilder
#         location_website_builder = LocationWebsiteBuilder.objects.create(
#             nameWebsite=name_website,
#             cliente_id=cliente_id,
#             location_website=location_website
#         )
        
#         # Create a new MergedWebsiteBuilder
#         MergedWebsiteBuilder.objects.create(
#                 cliente_id=cliente_id,
#                 location_website_builder=location_website_builder,
#                 website=location_website.websites
#             )
            
#         location_website.BuilderStatus = 'in progress'
#         location_website.save()
    
#         messages.success(request, 'Website building is in progress, please wait a minute for your website to be built.')
#         return redirect('WebSites')
#     else:
#         return render(request, 'websitebuilder/Cliente/WebSites.html')





# def edite_website(request, website_name):
#     cliente = request.user.cliente  
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
#     website_builder = get_object_or_404(WebsiteBuilder, nameWebsite=website_name)
#     merged_website_builder = MergedWebsiteBuilder.objects.filter(website_builder=website_builder).first()

#     suspendre_exists = Website_need_suspendre.objects.filter(website_builder=website_builder).exists()
#     reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(website_builder=website_builder).exists()
    
#     reset_request = website_need_reset.objects.filter(website_builder=website_builder).first()
#     reset_status = reset_request.statut if reset_request else None
    
#     delete_exists = Websites_Need_Delete.objects.filter(website_builder=website_builder).first()
#     delete_status = delete_exists.statut if delete_exists else None
    
    
#     context = {
#         'website_builder': website_builder,
#         'merged_website_builder': merged_website_builder,
#         'suspendre_exists':suspendre_exists,
#         'reprendre_suspendre_exists':reprendre_suspendre_exists,  
#         'reset_request' : reset_request,
#         'reset_status': reset_status,
#         'delete_exists':delete_exists,
#         'delete_status':delete_status,
#         'WebsiteBuilders':WebsiteBuilders,     
#     }
#     return render(request, "websitebuilder/Cliente/EditeWebsite.html", context)





# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente']) 
# def edite_free_website(request, website_name):
#     cliente = request.user.cliente  
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
#     getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, nameWebsite=website_name)
#     merged_website_builder = MergedWebsiteBuilder.objects.filter(getfree_website_builder=getfree_website_builder).first()

#     suspendre_exists = Website_need_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).exists()
#     reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).exists()
    
#     reset_request = website_need_reset.objects.filter(getfree_website_builder=getfree_website_builder).first()
#     reset_status = reset_request.statut if reset_request else None
    
#     delete_exists = Websites_Need_Delete.objects.filter(getfree_website_builder=getfree_website_builder).first()
#     delete_status = delete_exists.statut if delete_exists else None
    
#     context = {
#         'getfree_website_builder': getfree_website_builder,
#         'merged_website_builder': merged_website_builder,
#         'suspendre_exists': suspendre_exists,
#         'reprendre_suspendre_exists': reprendre_suspendre_exists,  
#         'reset_request': reset_request,
#         'reset_status': reset_status,
#         'delete_exists': delete_exists,
#         'delete_status': delete_status,
#         'WebsiteBuilders': WebsiteBuilders,     
#     }
#     return render(request, "websitebuilder/Cliente/EditeWebsiteGetFree.html", context)





# def edite_website_Location(request, nameWebsite):
#     cliente = request.user.cliente  
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
#     website_builder_location = get_object_or_404(LocationWebsiteBuilder, nameWebsite=nameWebsite)
#     merged_website_builder = MergedWebsiteBuilder.objects.filter(location_website_builder=website_builder_location).first()
    
#     current_datetime = timezone.now()
    
#     date_fin_date = website_builder_location.location_website.date_fin.date()

#     current_date = current_datetime.date()
    
#     expiration_delta = current_date - date_fin_date
    
#     # Compare if the expiration date has passed
#     expiration_passed = expiration_delta.days < 0

#     # Check if a resiliation exists
#     resiliation_exists = Website_need_resiliation.objects.filter(location_website_builder=website_builder_location).exists()
#     reprendre_exists = Website_reprendre_resiliation.objects.filter(location_website_builder=website_builder_location).exists()

#     suspendre_exists = Website_need_suspendre.objects.filter(location_website_builder=website_builder_location).exists()
#     reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(location_website_builder=website_builder_location).exists()

#     reset_request = website_need_reset.objects.filter(location_website_builder=website_builder_location).first()
#     reset_status = reset_request.statut if reset_request else None

#     delete_exists = Websites_Need_Delete.objects.filter(location_website_builder=website_builder_location).first()
#     delete_status = delete_exists.statut if delete_exists else None
    
#     context = {
#         'website_builder_location': website_builder_location,
#         'merged_website_builder': merged_website_builder,
#         'expiration_passed': expiration_passed,
#         'resiliation_exists': resiliation_exists,
#         'reprendre_exists': reprendre_exists,
#         'suspendre_exists':suspendre_exists,
#         'reprendre_suspendre_exists':reprendre_suspendre_exists,
#         'reset_request' : reset_request,
#         'reset_status': reset_status,
#         'delete_exists':delete_exists,
#         'delete_status':delete_status,
#         'WebsiteBuilders':WebsiteBuilders,     
#     }
#     return render(request, "websitebuilder/Cliente/EditeWebsiteLocation.html", context)




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_website_resiliation(request):
#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente_id')
#         location_website_builder_id = request.POST.get('location_website_builder_id')
#         website_id = request.POST.get('website_id')

#         cliente = get_object_or_404(Cliente, pk=cliente_id)
#         location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
#         website = get_object_or_404(Websites, pk=website_id)
        
#         # Check if a Website_need_resiliation is exists for this location_website_builder
#         if Website_reprendre_resiliation.objects.filter(location_website_builder=location_website_builder).exists():
#             Website_reprendre_resiliation.objects.filter(location_website_builder=location_website_builder).delete()

#         Website_need_resiliation.objects.create(
#             cliente=cliente,
#             location_website_builder=location_website_builder,
#             statut='0', 
#             website=website
#         )
        
#         location_website_builder.Statu_du_website = '3'
#         location_website_builder.save()

#         messages.success(request, 'La demande de Résiliation a été envoyée.')
        
#         if location_website_builder_id:
#             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
          
#         # return redirect('WebSites')  
#     else:
#         return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')



# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_website_reprendre(request):
#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente_id')
#         location_website_builder_id = request.POST.get('location_website_builder_id')
#         website_id = request.POST.get('website_id')

#         cliente = get_object_or_404(Cliente, pk=cliente_id)
#         location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
#         website = get_object_or_404(Websites, pk=website_id)

#         # Check if a Website_need_resiliation is exists for this location_website_builder
#         if Website_need_resiliation.objects.filter(location_website_builder=location_website_builder).exists():
#             Website_need_resiliation.objects.filter(location_website_builder=location_website_builder).delete()

#         Website_reprendre_resiliation.objects.create(
#             cliente=cliente,
#             location_website_builder=location_website_builder,
#             statut='0',  
#             website=website
#         )
        
#         location_website_builder.Statu_du_website = '1' 
#         location_website_builder.save()

#         messages.success(request, 'La demande de Reprendre a été envoyée.')
        
#         if location_website_builder_id:
#             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
          
#         # return redirect('WebSites')  
#     else:
#         return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_website_suspendre(request):
#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente_id')
#         location_website_builder_id = request.POST.get('location_website_builder_id')
#         getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
#         website_builder_id = request.POST.get('website_builder_id')

#         cliente = get_object_or_404(Cliente, pk=cliente_id)

#         location_website_builder = None
#         website_builder = None
#         getfree_website_builder = None  

#         if location_website_builder_id:
#             location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)

#         if website_builder_id:
#             website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)
            
#         if getfree_website_builder_id:
#             getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)  # Corrected here


#         # Delete existing Website_reprendre_suspendre records if they exist
#         if location_website_builder:
#             Website_reprendre_suspendre.objects.filter(location_website_builder=location_website_builder).delete()
#         if website_builder:
#             Website_reprendre_suspendre.objects.filter(website_builder=website_builder).delete()
#         if getfree_website_builder:
#             Website_reprendre_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).delete()


#         Website_need_suspendre.objects.create(
#             cliente=cliente,
#             location_website_builder=location_website_builder,
#             website_builder=website_builder,
#             getfree_website_builder=getfree_website_builder, 
#             statut='0', 
#         )

#         if location_website_builder:
#             location_website_builder.Statu_du_website = '2'  
#             location_website_builder.save()
            
#         if website_builder:
#             website_builder.Statu_du_website = '2' 
#             website_builder.save()
            
#         if getfree_website_builder:
#             getfree_website_builder.Statu_du_website = '2' 
#             getfree_website_builder.save()

#         messages.success(request, 'La demande de suspendre a été envoyée.')
        
#         if location_website_builder_id:
#             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
#         if website_builder_id:
#             return redirect('edite_website', website_name=website_builder.nameWebsite)
        
#         if getfree_website_builder_id:
#             return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
#     # return redirect('WebSites')  # Redirect to WebSites if none of the conditions are met
#     # else:
#     #     return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_website_suspendre_reprendre(request):
#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente_id')
#         location_website_builder_id = request.POST.get('location_website_builder_id')
#         getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
#         website_builder_id = request.POST.get('website_builder_id')

#         cliente = get_object_or_404(Cliente, pk=cliente_id)

#         location_website_builder = None
#         website_builder = None
#         getfree_website_builder = None 

#         if location_website_builder_id:
#             try:
#                 location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
#             except LocationWebsiteBuilder.DoesNotExist:
#                 pass  

#         if website_builder_id:
#             try:
#                 website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)
#             except WebsiteBuilder.DoesNotExist:
#                 pass  
        
#         if getfree_website_builder_id:
#             try:
#                 getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)
#             except WebsiteBuilder.DoesNotExist:
#                 pass


#         if location_website_builder:
#             Website_need_suspendre.objects.filter(location_website_builder=location_website_builder).delete()
#         if website_builder:
#             Website_need_suspendre.objects.filter(website_builder=website_builder).delete()
#         if getfree_website_builder:
#             Website_need_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).delete()


#         if location_website_builder or website_builder or getfree_website_builder :
#             Website_reprendre_suspendre.objects.create(
#                 cliente=cliente,
#                 location_website_builder=location_website_builder,
#                 getfree_website_builder=getfree_website_builder, 
#                 website_builder=website_builder,
#                 statut='0', 
#             )


#             if location_website_builder:
#                 location_website_builder.Statu_du_website = '1' 
#                 location_website_builder.save()

#             if website_builder:
#                 website_builder.Statu_du_website = '1' 
#                 website_builder.save()
                
#             if getfree_website_builder:
#                 getfree_website_builder.Statu_du_website = '1' 
#                 getfree_website_builder.save()

#             messages.success(request, 'La demande de Reprendre de suspendre a été envoyée.')
#         else:
#             messages.error(request, 'Required fields are missing.')
            
#         if location_website_builder_id:
#             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
#         if website_builder_id:
#             return redirect('edite_website', website_name=website_builder.nameWebsite)

#         if getfree_website_builder_id:
#             return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)

#         # return redirect('WebSites')
#     else:
#         return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_website_reset(request):
#     if request.method == 'POST':
#         cliente_id = request.POST.get('cliente_id')
#         location_website_builder_id = request.POST.get('location_website_builder_id')
#         getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
#         website_builder_id = request.POST.get('website_builder_id')

#         cliente = get_object_or_404(Cliente, pk=cliente_id)

#         location_website_builder = None
#         website_builder = None
#         getfree_website_builder = None 


#         if location_website_builder_id:
#             location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)

#         if website_builder_id:
#             website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)

#         if getfree_website_builder_id:
#             getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)


#         website_need_reset.objects.create(
#             cliente=cliente,
#             location_website_builder=location_website_builder,
#             getfree_website_builder=getfree_website_builder, 
#             website_builder=website_builder,
#             statut='0', 
#         )

#         # if location_website_builder:
#         #     location_website_builder.Statu_du_website = '2'  
#         #     location_website_builder.save()
            
            
#         # if website_builder:
#         #     website_builder.Statu_du_website = '2' 
#         #     website_builder.save()


#         messages.success(request, 'La demande de Reset a été envoyée.')
#         if location_website_builder_id:
#             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
#         if website_builder_id:
#             return redirect('edite_website', website_name=website_builder.nameWebsite) 
        
#         if getfree_website_builder_id:
#             return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
#     else:
#         return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')



# #supprime this def from project we don't need it
# # @login_required(login_url='login')
# # @allowedUsers(allowedGroups=['Cliente'])
# # def add_website_delete(request):
# #     if request.method == 'POST':
# #         cliente_id = request.POST.get('cliente_id')
# #         location_website_builder_id = request.POST.get('location_website_builder_id')
# #         website_builder_id = request.POST.get('website_builder_id')

# #         cliente = get_object_or_404(Cliente, pk=cliente_id)

# #         location_website_builder = None
# #         website_builder = None


# #         if location_website_builder_id:
# #             location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)

# #         if website_builder_id:
# #             website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)

      
# #         Websites_Need_Delete.objects.create(
# #             cliente=cliente,
# #             location_website_builder=location_website_builder,
# #             website_builder=website_builder,
# #             Statu_du_website='0', 
# #         )

# #         if location_website_builder:
# #             location_website_builder.Statu_du_website = '7'  
# #             location_website_builder.save()
            
            
# #         if website_builder:
# #             website_builder.Statu_du_website = '6' 
# #             website_builder.save()

# #         messages.success(request, 'This website its deleted.')
        
# #         if location_website_builder_id:
# #             return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
# #         if website_builder_id:
# #             return redirect('edite_website', website_name=website_builder.nameWebsite)
        
# #         # return redirect('WebSites')

# #     else:
# #         return render(request, 'websitebuilder/Cliente/EditeWebsiteLocation.html')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_period_location(request, location_id):
#     if request.method == 'POST':
#         location = get_object_or_404(LocationWebsites, pk=location_id)
#         website_builder_location = request.POST.get('website_builder_location_id')
#         rental_period = request.POST.get('rental_period')
        
#         try:
#             rental_period = int(rental_period)
#         except ValueError:
#             messages.error(request, "Invalid rental period.")
#             return redirect('list_websites')
        
#         cliente = request.user.cliente
#         total_price = location.websites.prix_loyer * rental_period

#         if cliente.solde < total_price:
#             messages.error(request, "You do not have enough solde to extend this rental period.")
#             return redirect('edite_website_Location', nameWebsite=website_builder_location)
        
#         # new_end_date = timezone.now() + timedelta(days=30 * rental_period)
#         new_end_date = location.date_fin + timedelta(days=30 * rental_period)

#         location.date_fin = new_end_date
#         location.save()
        
#         cliente.solde -= total_price
#         cliente.save()

#         messages.success(request, f"Rental period extended by {rental_period} months.")
#         return redirect('edite_website_Location', nameWebsite=website_builder_location)
#     else:
#         messages.error(request, "Invalid request.")
#         return redirect('WebSites')




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_period_hebergement(request, achat_id):
#     if request.method == 'POST':
#         achat = get_object_or_404(AchatWebsites, pk=achat_id)
#         website_builder_id = request.POST.get('website_builder_id')
#         hebergement_period = request.POST.get('hebergement_period')
        
#         try:
#             hebergement_period = int(hebergement_period)
#         except ValueError:
#             messages.error(request, "Invalid hebergement_period period.")
#             return redirect('list_websites')
        
#         website_builder = get_object_or_404(WebsiteBuilder, nameWebsite=website_builder_id)

#         cliente = request.user.cliente
#         total_price = achat.websites.prix_hebergement * hebergement_period

#         if cliente.solde < total_price:
#             messages.error(request, "You do not have enough solde to extend this hebergement_period period.")
#             return redirect('edit_website_location', nameWebsite=website_builder_id)
        
#         new_end_date = website_builder.date_fin_hebergement + timedelta(days=30 * hebergement_period)

#         website_builder.date_fin_hebergement = new_end_date
#         website_builder.save()
        
#         cliente.solde -= total_price
#         cliente.save()

#         messages.success(request, f"Hebergement period extended by {hebergement_period} months.")
#         return redirect('edite_website', website_name=website_builder.nameWebsite) 
        
#     else:
#         messages.error(request, "Invalid request.")
#         return redirect('WebSites')
 
 
 
 
 
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def add_period_free_hebergement(request, free_id):
#     if request.method == 'POST':
#         free = get_object_or_404(GetFreeWebsites, pk=free_id)
#         getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
#         hebergement_period = request.POST.get('hebergement_period')
        
#         try:
#             hebergement_period = int(hebergement_period)
#         except ValueError:
#             messages.error(request, "Invalid hebergement_period period.")
#             return redirect('list_websites')
        
#         getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)

#         cliente = request.user.cliente
#         total_price = free.websites.prix_hebergement * hebergement_period

#         if cliente.solde < total_price:
#             messages.error(request, "You do not have enough solde to extend this hebergement period.")
#             return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
#         new_end_date = getfree_website_builder.date_fin_hebergement + timedelta(days=30 * hebergement_period)

#         getfree_website_builder.date_fin_hebergement = new_end_date
#         getfree_website_builder.save()
        
#         cliente.solde -= total_price
#         cliente.save()

#         messages.success(request, f"Hebergement period extended by {hebergement_period} months.")
#         return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
#     else:
#         messages.error(request, "Invalid request.")
#         return redirect('WebSites')

    


from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.core.management import call_command
import os


@require_POST
def update_wordpress_view(request):
    title = request.POST.get('title')
    description = request.POST.get('description')
    # logo_url = request.POST.get('logo_url')
    # new_text = request.POST.get('new_text')
    admin_email = request.POST.get('admin_email')
    website_builder_id = request.POST.get('website_builder_id')
    website_builder_location_id = request.POST.get('website_builder_location_id')

    name = "testupdates"
    user = "Mohamed"
    password = "Mohamed"
    host = "localhost"
    
    db_name = request.POST.get('db_name') or os.getenv('WORDPRESS_DB_NAME', name)
    db_user = request.POST.get('db_user') or os.getenv('WORDPRESS_DB_USER', user)
    db_password = request.POST.get('db_password') or os.getenv('WORDPRESS_DB_PASSWORD', password)
    db_host = request.POST.get('db_host') or os.getenv('WORDPRESS_DB_HOST', host)

    call_command('update_wordpress',
                 title=title,
                 description=description,
                #  logo_url=logo_url,
                #  new_text=new_text,
                 admin_email=admin_email,
                 db_name=db_name,
                 db_user=db_user,
                 db_password=db_password,
                 db_host=db_host)

    if website_builder_id:
        website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)
        return redirect('edite_website', website_name=website_builder.nameWebsite)
        
    if website_builder_location_id:
        website_builder_location = get_object_or_404(LocationWebsiteBuilder, pk=website_builder_location_id)
        return redirect('edite_website_Location', nameWebsite=website_builder_location.nameWebsite)

    # return redirect('success_page')  
    





#AI CHATGPT
from django.shortcuts import render
import openai, os
from dotenv import load_dotenv

load_dotenv()

# api_key = os.getenv("OPENAI_KEY", None)

# def chatbot(request):
#     chatbot_response = None
#     if api_key is not None and request.method == 'POST':
#         openai.api_key = api_key
#         user_input = request.POST.get('user_input')        
#         prompt = user_input
        
#         response = openai.ChatCompletion.create(
#             model = 'gpt-3.5-turbo',
#             messages = [
#                 {"role": "system", "content": "You are a helpful assistant."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens = 256,
#             temperature = 0.5
#         )
        
#         chatbot_response = response.choices[0].message['content'].strip()
#         print(response)
#     return render(request, 'websitebuilder/Cliente/IntegratingEnter.html', {'chatbot_response': chatbot_response})

        
        
        


from .forms import InputForm


def generateur_description(request):
    form = InputForm()
    return render(request, 'websitebuilder/Cliente/IntegratingEnter.html', {'form': form})



def get_description(request):
    print("Received request method:", request.method)  
    if request.method == 'POST':
        form = InputForm(request.POST)
        if form.is_valid():
            input_text = form.cleaned_data['input_text']
            print("Received input text:", input_text)  
            description = get_gpt3_description(input_text)
            return render(request, 'websitebuilder/Cliente/IntegratingResultr.html', {'description': description})
        else:
            print("Form is not valid")  
    else:
        print("Not a POST request")  
        form = InputForm()
    return render(request, 'websitebuilder/Cliente/IntegratingEnter.html', {'form': form})


def get_gpt3_description(input_text):
    openai.api_key = os.getenv('OPENAI_API_KEY')
    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=f"Describe the following input: {input_text}",
        max_tokens=100
    )
    return response.choices[0].text.strip()




#test
# def AllMergedWebsiteBuilder(request):
#     AllMergedWebsiteBuilders = MergedWebsiteBuilder.objects.all()
#     context = {"AllMergedWebsiteBuilders":AllMergedWebsiteBuilders}
#     return render(request,"websitebuilder/SuperAdmin/AllMergedWebsiteBuilder.html",context)



# def AllWebsites_client_status(request):
#     AllWebsites_client_status = Websites_client_statu.objects.all().order_by('-date_created')
#     context = {"AllWebsites_client_status":AllWebsites_client_status}
#     return render(request,"websitebuilder/SuperAdmin/AllMergedWebsiteBuilder.html",context)




#Administrateur


#Home of Administrateur
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Administrateur']) 
def homeAdministrateur(request): 
    if request.user.is_authenticated:
        is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
    else: 
        is_Administrateur= False  
           
    context = {"is_Administrateur":is_Administrateur}
 
    return render(request, "websitebuilder/Administrateur/homeAdministrateur.html",context)




# #DashbordHome of Administrateur
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Administrateur']) 
# def dashbordHomeAdministrateur(request):  
#     return render(request, "websitebuilder/Administrateur/dashbordHomeAdministrateur.html")


@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def homeCommercial(request): 
    if request.user.is_authenticated:
        is_Commercial = request.user.groups.filter(name='Commercial').exists()
    else: 
        is_Commercial= False  
           
    context = {"is_Commercial":is_Commercial}
 
    return render(request, "websitebuilder/Commercial/homeCommercial.html",context)


# #SuperAdmin


#Home SuperAdmin
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SuperAdmin']) 
def homeSuperAdmin(request):  
    return render(request, "websitebuilder/SuperAdmin/homeSuperAdmin.html")

# from django.db.models import Sum


# #DashbordHome SuperAdmin
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def dashbordHomeSuperAdmin(request):
#     total_client = User.objects.filter(groups__name='Cliente').count()
#     total_website = Websites.objects.all().count()
#     total_service = Supports.objects.all().count()
#     total_solde = Cliente.objects.aggregate(Sum('solde'))['solde__sum'] or 0 
#     context = {
#         'total_client': total_client,
#         'total_website': total_website,
#         'total_service': total_service,
#         'total_solde': total_solde,
#         }
#     return render(request, "websitebuilder/SuperAdmin/dashbordHomeSuperAdmin.html",context)




# #The SuperAdmin can add a Administrateur
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def addAdministrateur(request):
#     form = AdministrateurForm()
#     if request.method == 'POST':
#         form = AdministrateurForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)  
#             user.save()

#             Administrateur.objects.create(
#                 user=user,
#                 name=form.cleaned_data.get('name'),
#                 email=form.cleaned_data.get('email'),
#                 phone=form.cleaned_data.get('phone'),
#             )

#             # Add user to the 'Administrateur' group
#             group = Group.objects.get(name="Administrateur")
#             user.groups.add(group)

#             messages.success(request, f"{user.username} created successfully!")
#             return redirect('/AdministrateurSuperAdmin')
#         else:
#             messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
#     context = {'form': form}
#     return render(request, 'websitebuilder/SuperAdmin/addAdministrateur.html', context)




# #Superadmin can show all Administrateur
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def AdministrateurSuperAdmin(request): 
#     Administrateurs = Administrateur.objects.all()
#     context = {'Administrateurs': Administrateurs} 
#     return render(request, "websitebuilder/SuperAdmin/AdministrateurSuperAdmin.html",context)




# #The SuperAdmin can add a SupportTechnique
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def addSupportTechnique(request):
#     form = SupportTechniqueForm()
#     if request.method == 'POST':
#         form = SupportTechniqueForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)  
#             user.save()

#             SupportTechnique.objects.create(
#                 user=user,
#                 name=form.cleaned_data.get('name'),
#                 email=form.cleaned_data.get('email'),
#                 phone=form.cleaned_data.get('phone'),
#             )

#             # Add user to the 'SupportTechnique' group
#             group = Group.objects.get(name="SupportTechnique")
#             user.groups.add(group)

#             messages.success(request, f"{user.username} created successfully!")
            
#             return redirect('/SupportTechniqueSuperAdmin')
#         else:
#             messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
#     context = {'form': form}
#     return render(request, 'websitebuilder/SuperAdmin/addSupportTechnique.html', context)





# #Superadmin can show all SupportTechnique
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def SupportTechniqueSuperAdmin(request): 
#     supportTechniques = SupportTechnique.objects.all()
#     context = {'supportTechniques': supportTechniques} 
#     return render(request, "websitebuilder/SuperAdmin/SupportTechniqueSuperAdmin.html",context)





# #The SuperAdmin can add a GestionnaireComptes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def addGestionnaireComptes(request):
#     form = GestionnaireComptesForm()
#     if request.method == 'POST':
#         form = GestionnaireComptesForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False) 
#             user.save()  

#             GestionnaireComptes.objects.create(
#                 user=user,
#                 name=form.cleaned_data.get('name'),
#                 email=form.cleaned_data.get('email'),
#                 phone=form.cleaned_data.get('phone'),
#             )

#             # Add user to the 'GestionnaireComptes' group
#             group = Group.objects.get(name="GestionnaireComptes")
#             user.groups.add(group)

#             messages.success(request, f"{user.username} created successfully!")
            
#             return redirect('/GestionnaireComptesSuperAdmin')
#         else:
#             messages.error(request, "Invalid form submission. Please correct the errors below.")  
        
#     context = {'form': form}
#     return render(request, 'websitebuilder/SuperAdmin/addGestionnaireComptes.html', context)




# #Superadmin can show all clientes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def ClienteSuperAdmin(request): 
#     clientes = Cliente.objects.all()
#     context = {'clientes': clientes} 
#     return render(request, "websitebuilder/SuperAdmin/ClienteSuperAdmin.html",context)





# #The SuperAdmin can add a clientes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def addCliente(request):
#     if request.method == 'POST':
#         form = ClienteForm(request.POST)
#         if form.is_valid():
#             # Create a new user
#             user = User.objects.create_user(
#                 username=form.cleaned_data.get('username'),
#                 email=form.cleaned_data.get('email'),
#                 password=form.cleaned_data.get('password1')
#             )

#             # Create a new Cliente
#             Cliente.objects.create(
#                 user=user,
#                 prenom=form.cleaned_data.get('prenom'),
#                 nom=form.cleaned_data.get('nom'),
#                 email=form.cleaned_data.get('email'),
#                 phone=form.cleaned_data.get('phone'),
#             )

#             # Add user to the 'Cliente' group
#             group = Group.objects.get(name="Cliente")
#             user.groups.add(group)

#             messages.success(request, f"{user.username} created successfully!")
#             return redirect('/ClienteSuperAdmin')
#         else:
#             messages.error(request, "Invalid form submission. Please correct the errors below.")
#     else:
#         form = ClienteForm()
        
#     context = {'form': form}
#     return render(request, 'websitebuilder/SuperAdmin/addCliente.html', context)






# #Superadmin can show all GestionnaireComptes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def GestionnaireComptesSuperAdmin(request): 
#     GestionnairesComptes = GestionnaireComptes.objects.all()
#     context = {'GestionnairesComptes': GestionnairesComptes} 
#     return render(request, "websitebuilder/SuperAdmin/GestionnaireComptesSuperAdmin.html",context)




# #SuperAdmin can show details of the trace (image) of traceDemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin'])
# def full_size_image_Super_Admin(request, traceDemandeRecharger_id):
#     trace_demande_recharger = get_object_or_404(LaTraceDemandeRecharger, pk=traceDemandeRecharger_id)
#     image = trace_demande_recharger.image
#     cliente = trace_demande_recharger.cliente.user.username
#     solde = trace_demande_recharger.solde
#     updated_by = trace_demande_recharger.demande_recharger.updated_by
#     status = trace_demande_recharger.demande_recharger.status
#     motif = trace_demande_recharger.demande_recharger.motifNonAcceptation

#     return render(request, 'websitebuilder/SuperAdmin/full_size_image_Super_Admin.html', {'image': image, 'cliente': cliente, 'solde': solde,'updated_by':updated_by,'status':status,'motif':motif})




# #List of LaTraceDemandeRecharger Demandes Recharge  [SuperAdmin]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def traceDemandeRecharger(request): 
#     traceDemandeRechargers = LaTraceDemandeRecharger.objects.order_by('-date_created')
#     context = {'traceDemandeRechargers': traceDemandeRechargers} 
#     return render(request, "websitebuilder/SuperAdmin/traceDemandeRecharger.html",context)




# #List of LaTraceDemandeRecharger Demandes Recharge  [Done]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def traceDemandeRechargerDone(request): 
#     traceDemandeRechargers = LaTraceDemandeRecharger.objects.filter(demande_recharger__status='Done').order_by('-date_created')
#     context = {'traceDemandeRechargers': traceDemandeRechargers} 
#     return render(request, "websitebuilder/SuperAdmin/traceDemandeRechargerDone.html",context)




# #List of LaTraceDemandeRecharger Demandes Recharge  [inacceptable]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def traceDemandeRechargerInacceptable(request): 
#     traceDemandeRechargers = LaTraceDemandeRecharger.objects.filter(demande_recharger__status='inacceptable').order_by('-date_created')
#     context = {'traceDemandeRechargers': traceDemandeRechargers} 
#     return render(request, "websitebuilder/SuperAdmin/traceDemandeRechargerInacceptable.html",context)





# #SuperAdmin can show details of the trace (image) of traceDemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin'])
# def full_size_image_NotDone_Super_Admin(request, DemandeRecharger_id):
#     Demande_Recharger = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id)
#     image = Demande_Recharger.image
#     cliente = Demande_Recharger.cliente.user.username
#     solde = Demande_Recharger.solde
#     updated_by = Demande_Recharger.updated_by
#     status = Demande_Recharger.status

#     return render(request, 'websitebuilder/SuperAdmin/full_size_image_Super_Admin.html', {'image': image, 'cliente': cliente, 'solde': solde,'updated_by':updated_by,'status':status})





# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def DemandeRechargerNotDone(request): 
#     DemandeRechargerNotDones = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#     context = {'DemandeRechargerNotDones': DemandeRechargerNotDones} 
#     return render(request, "websitebuilder/SuperAdmin/DemandeRechargerNotDone.html",context)





# #List of Demands Support all [SuperAdmin]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def DemandeSupportAll(request): 
#     DemandeSupports = DemandeSupport.objects.order_by('-date_created')
#     context = {'DemandeSupports': DemandeSupports} 
#     return render(request, "websitebuilder/SuperAdmin/DemandeSupportAll.html",context)



# #List of Demands Support Done [SuperAdmin]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def DemandeSupportDoneSA(request): 
#     DemandeSupportsDone = DemandeSupport.objects.filter(status='Done').order_by('-date_created')
#     # DemandeSupports = DemandeSupport.objects.order_by('-date_created')
#     context = {'DemandeSupportsDone': DemandeSupportsDone} 
#     return render(request, "websitebuilder/SuperAdmin/DemandeSupportDoneSA.html",context)



# #List of Demands Support Not Done yet [SuperAdmin]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SuperAdmin']) 
# def DemandeSupportNotDoneyetSA(request): 
#     DemandeSupportsNotDoneyet = DemandeSupport.objects.filter(status='Not Done yet').order_by('-date_created')
#     # DemandeSupports = DemandeSupport.objects.order_by('-date_created')
#     context = {'DemandeSupportsNotDoneyet': DemandeSupportsNotDoneyet} 
#     return render(request, "websitebuilder/SuperAdmin/DemandeSupportNotDoneyetSA.html",context)





# #SupportTechnique


#Home of SupportTechnique
@login_required(login_url='login')
@allowedUsers(allowedGroups=['SupportTechnique']) 
def homeSupportTechnique(request): 
    if request.user.is_authenticated:
        is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
    else: 
        is_SupportTechnique= False  
           
    context = {"is_SupportTechnique":is_SupportTechnique}
 
    return render(request, "websitebuilder/SupportTechnique/homeSupportTechnique.html",context)




# #DashbordHome of SupportTechnique
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique']) 
# def dashbordHomeSupportTechnique(request):  
#     return render(request, "websitebuilder/SupportTechnique/dashbordHomeSupportTechnique.html")




# #SupportTechnique can consume a demand support and update status to 'Consomé'
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique']) 
# def consome_support(request, demande_support_id):
#     demande_support = DemandeSupport.objects.get(pk=demande_support_id)
#     support_technique = request.user.supporttechnique
#     if demande_support and support_technique:
#         demande_support.status = 'Done'
#         demande_support.updated_by = support_technique
#         demande_support.save()
#         if demande_support.achat_support:
#             demande_support.achat_support.StatusConsomé = 'Consomé'
#             demande_support.achat_support.updated_by = support_technique
#             demande_support.achat_support.save()
#     return redirect('DemandeSupportNotDoneyet')



# #SupportTechnique can consume a demand support and update status to 'Consomé' with confirmation
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique'])
# def confirm_consome_support(request):
#     if request.method == 'POST':
#         demande_support_id = request.POST.get('demande_support_id')
#         if demande_support_id:
#             demande_support = get_object_or_404(DemandeSupport, pk=demande_support_id)
#             support_technique = request.user.supporttechnique
#             if demande_support and support_technique:
#                 demande_support.status = 'Done'
#                 demande_support.updated_by = support_technique
#                 demande_support.save()
#                 if demande_support.achat_support:
#                     demande_support.achat_support.StatusConsomé = 'Consomé'
#                     demande_support.achat_support.updated_by = support_technique
#                     demande_support.achat_support.save()
#                 return redirect('DemandeSupportNotDoneyet')
#             else:
#                 messages.error(request, "Invalid demande support or support technique.")
#         else:
#             messages.error(request, "Invalid demande support ID.")
#     return redirect('DemandeSupportNotDoneyet')





# #List of Demands Support Not Done yet [SupportTechnique]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique']) 
# def DemandeSupportNotDoneyet(request): 
#     DemandeSupports = DemandeSupport.objects.filter(status='Not Done yet').order_by('-date_created')
#     context = {'DemandeSupports': DemandeSupports} 
#     return render(request, "websitebuilder/SupportTechnique/DemandeSupportNotDoneyet.html",context)




# #List of Demands Support Done [SupportTechnique]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['SupportTechnique']) 
# def DemandeSupportDone(request): 
#     DemandeSupports = DemandeSupport.objects.filter(status='Done').order_by('-date_created')
#     context = {'DemandeSupports': DemandeSupports} 
#     return render(request, "websitebuilder/SupportTechnique/DemandeSupportDone.html",context)






#GestionnairesComptes



#Home of GestionnairesComptes
@login_required(login_url='login')
@allowedUsers(allowedGroups=['GestionnaireComptes']) 
def homeGestionnairesComptes(request): 
    if request.user.is_authenticated:
        is_GestionnaireComptes = request.user.groups.filter(name='GestionnaireComptes').exists()
    else: 
        is_GestionnaireComptes= False  
    
    # if request.user.is_authenticated:
    #     new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
    #     if new_demandes.exists():
    #         messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
           
    context = {"is_GestionnaireComptes":is_GestionnaireComptes}
 
    return render(request, "websitebuilder/GestionnaireComptes/homeGestionnaireComptes.html",context)





# #DashbordHome of GestionnaireComptes
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def dashbordHomeGestionnaireComptes(request):  
#     if request.user.is_authenticated:
#         new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#         if new_demandes.exists():
#             messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
            
#     return render(request, "websitebuilder/GestionnaireComptes/dashbordHomeGestionnaireComptes.html")




# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes'])
# def dashbordGestionnaireComptes(request):
#     if request.user.is_authenticated:
#         new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#         if new_demandes.exists():
#             messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')

#     return render(request, "websitebuilder/GestionnaireComptes/dashbordGestionnaireComptes.html")




# #GestionnaireComptes can show all details of DemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes'])
# def details_DemandeRecharger(request, demande_recharger_id):
#     demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
#     return render(request, 'websitebuilder/GestionnaireComptes/details_DemandeRecharger.html', {'demande_recharger': demande_recharger})




# #GestionnaireComptes can show details of the trace (image) of DemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes'])
# def view_full_size_image(request, DemandeRecharger_id):
#     image = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).image
#     cliente = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).cliente.user.username
#     solde = get_object_or_404(DemandeRecharger, pk=DemandeRecharger_id).solde

#     return render(request, 'websitebuilder/GestionnaireComptes/full_size_image.html', {'image': image,'cliente': cliente,'solde': solde})




# from django.shortcuts import redirect

# #GestionnaireComptes can confirm the DemandeRecharger and create LaTraceDemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def confirm_demande_recharger(request, demande_recharger_id):
#     demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
#     demande_recharger.updated_by = request.user.gestionnairecomptes
    
#     if request.method == 'POST':
#         solde = request.POST.get('solde')
#         image = request.FILES.get('image')
        
#         # Update solde of the client table
#         demande_recharger.cliente.solde += int(solde)
#         demande_recharger.cliente.save()
        
#         demande_recharger.status = 'Done'
#         demande_recharger.save()
        
#         # Create an LaTraceDemandeRecharger and save it
#         LaTraceDemandeRecharger.objects.create(
#             image=image,
#             solde=solde,
#             demande_recharger=demande_recharger,  
#             cliente=demande_recharger.cliente,
#             updated_by=request.user.gestionnairecomptes
#         )
        
#         messages.success(request, "Demande Recharger Confirm successfully")
#         return redirect('DemandeRechargerDone')

#     return render(request, 'websitebuilder/GestionnaireComptes/details_DemandeRecharger.html', {'demande_recharger': demande_recharger})




# #GestionnaireComptes can infirmer the DemandeRecharger and create LaTraceDemandeRecharger
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def infirmer_demande_recharger(request, demande_recharger_id):
#     demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
#     demande_recharger.updated_by = request.user.gestionnairecomptes
    
#     if request.method == 'POST':
#         solde = request.POST.get('solde')
#         image = request.FILES.get('image')
#         motifNonAcceptation = request.POST.get('motifNonAcceptation')
        
#         demande_recharger.status = 'inacceptable'
#         demande_recharger.motifNonAcceptation = motifNonAcceptation
#         demande_recharger.save()
        
#         # Create an LaTraceDemandeRecharger and save it
#         LaTraceDemandeRecharger.objects.create(
#             image=image,
#             solde=solde,
#             demande_recharger=demande_recharger, 
#             cliente=demande_recharger.cliente,
#             updated_by=request.user.gestionnairecomptes
#         )
        
#         messages.success(request, "Demande Recharger Confirm successfully")
#         return redirect('DemandeRechargerInacceptable')

#     return render(request, 'websitebuilder/GestionnaireComptes/details_DemandeRecharger.html', {'demande_recharger': demande_recharger})




# #List of Demandes Recharge Not Done yet [GestionnaireComptes]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def DemandeRechargerNotDoneyet(request):
#     if request.user.is_authenticated:
#         new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#         if new_demandes.exists():
#             messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
             
#     DemandeRechargers = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#     context = {'DemandeRechargers': DemandeRechargers} 
#     return render(request, "websitebuilder/GestionnaireComptes/DemandeRechargerNotDoneyet.html",context)




# #List of Demandes Recharge Done [GestionnaireComptes]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def DemandeRechargerDone(request):
#     if request.user.is_authenticated:
#         new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#         if new_demandes.exists():
#             messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
             
#     DemandeRechargers = DemandeRecharger.objects.filter(status='Done', updated_by__user=request.user).order_by('-date_created')
#     context = {'DemandeRechargers': DemandeRechargers} 
#     return render(request, "websitebuilder/GestionnaireComptes/DemandeRechargerDone.html",context)




# #List of Demandes Recharge inacceptable [GestionnaireComptes]
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['GestionnaireComptes']) 
# def DemandeRechargerInacceptable(request): 
#     if request.user.is_authenticated:
#         new_demandes = DemandeRecharger.objects.filter(status='Not Done yet').order_by('-date_created')
#         if new_demandes.exists():
#             messages.info(request, f'You have {new_demandes.count()} new demande(s) to review.')
            
#     DemandeRechargers = DemandeRecharger.objects.filter(status='inacceptable').order_by('-date_created')
#     context = {'DemandeRechargers': DemandeRechargers} 
#     return render(request, "websitebuilder/GestionnaireComptes/DemandeRechargerInacceptable.html",context)







#For ALL 

def detail(request):  
    return render(request, "websitebuilder/detail.html")







#The Some Def

# @login_required
# def Achat_website_list(request):
#     cliente = request.user.cliente
#     achats = AchatWebsites.objects.filter(cliente=cliente)
#     context = {'achats': achats}
#     return render(request, 'websitebuilder/WebSites.html', context)



# def done_demande_recharger(request, demande_recharger_id):
#     demande_recharger = get_object_or_404(DemandeRecharger, pk=demande_recharger_id)
#     demande_recharger.updated_by = request.user.gestionnairecomptes
    
#     demande_recharger.cliente.solde += demande_recharger.solde
#     demande_recharger.cliente.save()
    
#     demande_recharger.status = 'Done'
#     demande_recharger.save()
#     messages.success(request, f"Demand recharge {demande_recharger.code_DemandeRecharger} Confirmation as done successfully!")
#     return redirect('DemandeRechargerNotDoneyet')



# def confirm_demande_recharger(request):
#     if request.method == 'POST':
#         demande_recharger_id = request.POST.get('demande_recharger_id')
#         if demande_recharger_id:
#             return redirect('done_demande_recharger', demande_recharger_id=demande_recharger_id)
#         else:
#             messages.error(request, "Invalid demande recharger ID.")
#     return redirect('DemandeRechargerNotDoneyet')
