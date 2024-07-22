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




# @anonymous_required
# def home2(request):
#     return render(request, "websitebuilder/home2.html")


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




#Cliente


#DashbordHome of Cliente
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



# def dashboard(request):  
#     latest_website_builders = []

#     if request.user.is_authenticated:
#         for achat in request.user.cliente.achatwebsites_set.filter(BuilderStatus='Builder'):
#             latest_website_builders.extend(achat.websitebuilder_set.all())

#     # Slice the list to get only the latest 5 instances
#     latest_website_builders = latest_website_builders[-2:]

#     context = {
#         'latest_website_builders': latest_website_builders,
#     }
#     return render(request, "clients/dashboard2.html",context)



def dashboard(request):  
    return render(request, "clients/dashboard.html")



# def dashboard2(request): 
#     cliente = request.user.cliente
#     WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:5]
#     context = {
#         'WebsiteBuilders': WebsiteBuilders,
#     } 
#     return render(request, "clients/dashboard2.html",context)


def editUser(request):  
    return render(request, "clients/editUser.html")


#Edit and display client information
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def detailUser(request):  
    cliente = request.user.cliente 
    AchatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')[:2]
    AchatWebsitess = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')[:2]
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

    context = {
        'cliente': cliente,
        'AchatSupports': AchatSupports,
        'AchatWebsitess': AchatWebsitess,
        'WebsiteBuilders': WebsiteBuilders,
    }
    return render(request, "clients/detailUser.html", context)



#Edit client more information [address,nom_entreprise,...]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_additional_info(request):
    if request.method == 'POST':
        address = request.POST.get('address')
        nom_entreprise = request.POST.get('nom_entreprise')
        numero_ice = request.POST.get('numero_ice')

        cliente = request.user.cliente
        cliente.address = address
        cliente.nom_entreprise = nom_entreprise
        cliente.numero_ice = numero_ice
        cliente.save()

        messages.success(request, "Additional information added successfully!")
        return redirect('detailUser')
    else:
        form = AdditionalInfoForm()

    return render(request, 'clients/detailUser.html', {'form': form})




#Edit client more information [nom,prenom,...]
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def update_cliente(request):
    cliente = request.user.cliente  
    if request.method == 'POST':
        prenom = request.POST.get('prenom')
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        phone = request.POST.get('phone')

        cliente = request.user.cliente
        cliente.prenom = prenom
        cliente.nom = nom
        cliente.email = email
        cliente.phone = phone
        cliente.save()
        
        messages.success(request, "Client updated successfully!")
        return redirect('detailUser')
    else:
        cliente_form = ClienteUpdateForm()

    return render(request, 'clients/detailUser.html', {'cliente_form': cliente_form})



from django.contrib.auth import update_session_auth_hash


#Edit password for client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def change_password(request):
    cliente = request.user.cliente 

    if request.method == 'POST':
        form = ClientePasswordChangeForm(request.user, request.POST)  
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, request.user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('detailUser')  
        else:
            messages.error(request, 'Please rewrite old password is not correct.')
            return redirect('detailUser')  
    else:
        form = ClientePasswordChangeForm(request.user)  
    
    return render(request, 'clients/detailUser.html', {'form': form})




#List of websites that are displayed to the client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_websites(request): 
    cliente = request.user.cliente  
    websites = Websites.objects.all()
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'websites': websites,
        'WebsiteBuilders': WebsiteBuilders,
        }  
    return render(request, "clients/list_websites.html",context)




#More detail of website
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def detail_website(request, slugWebsites):
    if request.user.is_authenticated:
        is_Cliente = request.user.groups.filter(name='Cliente').exists()
        is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
        is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
    else: 
        is_Cliente= False  
        is_SupportTechnique= False 
        is_Administrateur= False  
        
    website_info = get_object_or_404(Websites, slugWebsites=slugWebsites)
    
    context = {
        'website_info': website_info,
        "is_Cliente": is_Cliente,
        "is_SupportTechnique":is_SupportTechnique,
        "is_Administrateur":is_Administrateur
    }
    return render(request, "clients/detail_website.html", context)




#List of All websites that are displayed to the client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def all_list_websites(request):
    if request.user.is_authenticated:
        is_Cliente = request.user.groups.filter(name='Cliente').exists()
        is_SupportTechnique = request.user.groups.filter(name='SupportTechnique').exists()
        is_Administrateur = request.user.groups.filter(name='Administrateur').exists()
    else:
        is_Cliente = False  
        is_SupportTechnique = False 
        is_Administrateur = False  

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
        "selected_category": category,
        "cms_filter": cms_filter,
        "langues_filter": langues_filter,
        "plan_filter": plan_filter,
    }

    return render(request, 'clients/all_list_websites.html', context)



#List of Supports that are displayed to the client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_services(request):
    cliente = request.user.cliente  
    supports = Supports.objects.all()
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'supports': supports,
        'WebsiteBuilders': WebsiteBuilders,
        } 
    return render(request, "clients/list_services.html",context)


from itertools import chain


#List of all services owned by the registered client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def MesServices(request):  
    cliente = request.user.cliente
    achat_supports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')
    achat_websites = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    location_websites = LocationWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    getfree_website = GetFreeWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

    combined_websites = sorted(
        chain(
            achat_websites,
            location_websites,
            getfree_website
        ),
        key=lambda instance: instance.date_created,
        reverse=True
    )

    context = {
        'achat_supports': achat_supports,
        'achat_websites': achat_websites,
        'location_websites': location_websites,
        'getfree_website': getfree_website,
        'combined_websites': combined_websites,
        'WebsiteBuilders': WebsiteBuilders,
    }
    return render(request, "clients/MesServices.html", context)




#List of all webSites owned by the registered client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def WebSites(request): 
    cliente = request.user.cliente
    achats = AchatWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    locations = LocationWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    frees = GetFreeWebsites.objects.filter(cliente=cliente).order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]

    website_builders = WebsiteBuilder.objects.filter(cliente=cliente)
    location_website_builders = LocationWebsiteBuilder.objects.filter(cliente=cliente)
    free_website_builders = GetFreeWebsiteBuilder.objects.filter(cliente=cliente)


    context = {
        'achats': achats,
        'locations': locations,
        'website_builders': website_builders,
        'location_website_builders':location_website_builders,
        'WebsiteBuilders': WebsiteBuilders,
        'free_website_builders' :free_website_builders,
        'frees': frees,
    } 
    return render(request, "clients/WebSites.html", context)






#List of all supports owned by the registered client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def Services(request):
    cliente = request.user.cliente
    achatSupports = AchatSupport.objects.filter(cliente=cliente).order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'achatSupports': achatSupports,
        'WebsiteBuilders': WebsiteBuilders,
    }   
    return render(request, "clients/Services.html",context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def solde_et_facturation(request): 
    cliente = request.user.cliente   
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    facturations = Facturations.objects.filter(cliente=cliente).order_by('-date_created')
    context = {
        'WebsiteBuilders': WebsiteBuilders,
        'facturations': facturations,
    } 
    return render(request, "clients/solde_et_facturation.html",context)



from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from io import BytesIO
from xml.sax.saxutils import escape
from reportlab.platypus import Spacer
from datetime import datetime
from reportlab.lib.enums import TA_CENTER




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def generate_facturation_pdf(request, facturation_id):
    facturation = get_object_or_404(Facturations, id=facturation_id)
    template_path = 'clients/facturation_pdf_template.html'
    context = {'facturation': facturation}

    # Create a bytes buffer for the PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Create styles
    styles = getSampleStyleSheet()
    normal_style = styles['Normal']
    header_style = styles['Heading2']
    subheader_style = ParagraphStyle(name='SubHeader', fontSize=10, leading=12)
    
    # Start with the header
    elements = []
    elements.append(Paragraph('FACTURE', header_style))
    
    # Client Information
    client_info = f"""
    <b>Société:</b> {facturation.cliente.nom_entreprise}<br/>
    <b>Réf. Client:</b> {facturation.cliente.code_client}<br/>
    <b>Client:</b> {facturation.cliente.prenom} {facturation.cliente.nom}<br/>
    <b>Adresse:</b> {facturation.cliente.address}<br/>
    <b>ICE:</b> {facturation.cliente.numero_ice}<br/>
    <br/>
    """
    elements.append(Paragraph(client_info, normal_style))

    Référence_facture = f"""<b>Référence facture:</b> {facturation.code_facturation}"""
    elements.append(Paragraph(Référence_facture, subheader_style))
    
    formatted_date = facturation.date_created.strftime("%d %b %Y")
    Frais_services = f"""<b>Frais de services Altivax du:</b> {formatted_date}<br/>"""
    elements.append(Paragraph(Frais_services, subheader_style))
    
    
    # Determine description and price
    if facturation.location_website:
        description = f"Site Web loué est {facturation.location_website.websites}"
        total_ttc = facturation.location_website.prix_loyer
        
        # Format the end_date
        formatted_end_date = facturation.location_website.date_fin.strftime("%d %b %Y")
        end_date = f"La date fin de Location est {formatted_end_date}"
    elif facturation.achat_website:
        description = f"Le site a été acheté est {facturation.achat_website.websites}"
        total_ttc = facturation.achat_website.prix_achat
        end_date = ""
    elif facturation.achat_support:
        description = f"Support acheté est {facturation.achat_support.support}"
        total_ttc = facturation.achat_support.prix
        end_date = ""
    else:
        description = "N/A"
        total_ttc = 0
        end_date = ""


    # Create table data
    table_data = [['Description', 'Total TTC']]
    row_data = [description, f"{total_ttc} MAD"]

    if facturation.location_website:
        table_data[0].insert(1, 'Date Fin Location')
        row_data.insert(1, end_date)

    table_data.append(row_data)

    # Determine the number of columns in the table
    num_cols = len(table_data[0])

    # Create a table with automatic column widths
    table = Table(table_data)

    # Calculate 80% of the page width and adjust the table width
    page_width = letter[0]
    table_width = page_width * 0.8

    # Calculate column widths based on content and total table width
    column_widths = []
    for col_index in range(num_cols):
        max_width = max([len(str(row[col_index])) for row in table_data]) * 6  # Estimate width based on content length
        column_widths.append(max_width)

    # Adjust column widths to fit within the table width
    total_content_width = sum(column_widths)
    scale_factor = table_width / total_content_width
    adjusted_column_widths = [width * scale_factor for width in column_widths]

    # Apply adjusted column widths to the table
    table._argW = adjusted_column_widths

    # Style the table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), '#f2f2f2'),
        ('GRID', (0, 0), (-1, -1), 1, 'black'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONT', (0, 1), (-1, -1), 'Helvetica'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 1), (-1, -1), '#ffffff'),
    ]))

    # Add space before the table
    elements.append(Spacer(1, 12))  # (width, height) in points. 12 points = 1/6 inch

    elements.append(table)

    # Add space after the table
    elements.append(Spacer(1, 12))

  
    # Add space before the Total TTC paragraph
    elements.append(Spacer(1, 12))

    # Define a center-aligned paragraph style
    centered_style = ParagraphStyle(name='Centered', parent=subheader_style, alignment=TA_CENTER)

    # Add the Total TTC paragraph with center alignment
    elements.append(Paragraph(f"Total TTC: {total_ttc} MAD", centered_style))

    # Add space after the Total TTC paragraph
    elements.append(Spacer(1, 12))
    
    
    # Payment Conditions
    conditions = """
    En votre aimable règlement<br/>
    Et avec nos remerciements.<br/><br/>
    Conditions de paiement : paiement à réception de facture.<br/>
    Aucun escompte consenti pour règlement anticipé.<br/>
    Règlement par virement bancaire ou carte bancaire.<br/><br/>
    En cas de retard de paiement, indemnité forfaitaire pour frais de recouvrement : 40 euros (art. L.4413 et L.4416 code du commerce).
    """
    elements.append(Paragraph(conditions, subheader_style))
    
    # Build the PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer and write it to the response
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facturation_{facturation.cliente.user.username}_{facturation.code_facturation}.pdf"'
    return response







@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def paiement(request):  
    cliente = request.user.cliente   
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'WebsiteBuilders': WebsiteBuilders,
    } 
    return render(request, "clients/paiement.html",context)




#Can the client create request Reload "Demande Recharger"
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def create_demande_recharger(request):
    cliente = request.user.cliente  
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    if request.method == 'POST':
        form = DemandeRechargerForm(request.POST, request.FILES)
        if form.is_valid():
            demande_recharger = form.save(commit=False)
            demande_recharger.cliente = request.user.cliente
            demande_recharger.save()
            messages.success(request, "Demande Recharger in progress, please wait ...")
            return redirect('clients/list_demande_recharger')
        else:
            messages.error(request, "There was an error with your form. Please check the details and try again.")
    else:
        form = DemandeRechargerForm()
    
    return render(request, 'clients/create_demande_recharger.html', {'form': form,'WebsiteBuilders':WebsiteBuilders})



#List of all request Reload "Demande Recharger" owned by the registered client
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_demande_recharger(request):
    cliente = request.user.cliente
    list_demande_rechargers = DemandeRecharger.objects.filter(cliente=cliente).order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'list_demande_rechargers': list_demande_rechargers,
        'WebsiteBuilders': WebsiteBuilders,
    }
   
    return render(request, 'clients/list_demande_recharger.html',context)





#List of all Demande Recharger owned by the registered client and status is "not done yet"
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_Demande_Recharger_En_attente(request): 
    cliente = request.user.cliente
    DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='Not Done yet').order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'DemandeRechargers': DemandeRechargers,
        'WebsiteBuilders': WebsiteBuilders,
        } 
    return render(request, "clients/list_Demande_Recharger_En_attente.html",context)




#List of all Demande Recharger owned by the registered client and status is "done"
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_Demande_Recharger_Complete(request): 
    cliente = request.user.cliente
    DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='Done').order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'DemandeRechargers': DemandeRechargers,
        'WebsiteBuilders': WebsiteBuilders,
        } 
    return render(request, "clients/list_Demande_Recharger_Complete.html",context)




#List of all Demande Recharger owned by the registered client and status is "inacceptable"
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def list_Demande_Recharger_Annule(request): 
    cliente = request.user.cliente
    DemandeRechargers = DemandeRecharger.objects.filter(cliente=cliente,status='inacceptable').order_by('-date_created')
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    context = {
        'DemandeRechargers': DemandeRechargers,
        'WebsiteBuilders': WebsiteBuilders,
        } 
    return render(request, "clients/list_Demande_Recharger_Annule.html",context)




from django.db.models import F

#The client can buy a website ,Maybe i need deleted this becuase i use just confirm_Achat_website
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def Achat_website(request, website_id):
    try:
        website = Websites.objects.get(pk=website_id)
        cliente = request.user.cliente  
        if cliente.solde >= website.prix:
            # Create a table in the Achat model
            AchatWebsites.objects.create(cliente=cliente, websites=website, solde=website.prix)
            messages.success(request, f"Website {website.name} Achat successfully!")
            
            #Need deleted from this code because I add it in models.py
            # cliente.solde -= website.prix  
            # cliente.save()  
            return redirect('clients/WebSites')
        else:
            messages.error(request, "Insufficient balance to purchase this website.")
            return redirect('clients/list_websites')
    except Websites.DoesNotExist:
        messages.error(request, "Website does not exist.")
    except Cliente.DoesNotExist:
        messages.error(request, "Client does not exist.")
    return redirect('WebSites')



from django.utils import formats



# Email sending function send_email_Achat_website
def send_email_Achat_website(request, cliente, websiteName,websiteDate,websitePrix):
    mail_subject = "Achat Website successfully"
    formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
    formatted_price = formats.number_format(websitePrix)
    
    message = render_to_string("websitebuilder/send_email_Achat_website.html", {
        'user': cliente.user.username,
        'name_website': websiteName,
        'date_website': formatted_date,
        'prix_website': formatted_price,
        'domain': get_current_site(request).domain,
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[cliente.user.email])
    email.content_subtype = "html"  
    
    if email.send():
        success_message = mark_safe(
            f'Dear <b>{cliente.user.username}</b>, Website Achat<b>{websiteName}</b> has been successfully . '
            f'Please check your email <b>{cliente.user.email}</b> for more details.'
        )
        messages.success(request, success_message)
    else:
        messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




#The client can buy a website, but after confirming
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def confirm_Achat_website(request):
    if request.method == 'POST':
        website_id = request.POST.get('website_id')
        try:
            website = Websites.objects.get(pk=website_id)
            cliente = Cliente.objects.get(user=request.user)
            if cliente.solde >= website.prix:
                # Create a table in the AchatWebsites model
                achat_website = AchatWebsites.objects.create(cliente=cliente, websites=website, prix_achat=website.prix)
                # Send email
                send_email_Achat_website(request, cliente, website.name, achat_website.date_created, achat_website.prix_achat)

                # messages.success(request, f"Website {website.name} purchased successfully!")
            else:
                messages.error(request, "Insufficient balance to purchase this website.")
                return redirect('list_websites')
        except Cliente.DoesNotExist:
            messages.error(request, "Client does not exist.")
        except Websites.DoesNotExist:
            messages.error(request, "Website does not exist.")
    return redirect('WebSites')






# Email sending function send_email_GetFree_website
def send_email_GetFree_website(request, cliente, websiteName,websiteDate,websitePrix):
    mail_subject = "Get Free Website successfully"
    formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
    formatted_price = formats.number_format(websitePrix)
    
    message = render_to_string("websitebuilder/send_email_GetFree_website.html", {
        'user': cliente.user.username,
        'name_website': websiteName,
        'date_website': formatted_date,
        'prix_website': formatted_price,
        'domain': get_current_site(request).domain,
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[cliente.user.email])
    email.content_subtype = "html"  
    
    if email.send():
        success_message = mark_safe(
            f'Dear <b>{cliente.user.username}</b>, Website Achat<b>{websiteName}</b> has been successfully . '
            f'Please check your email <b>{cliente.user.email}</b> for more details.'
        )
        messages.success(request, success_message)
    else:
        messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')



# The client can Get it Free a website
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def GetFree_website(request):
    if request.method == 'POST':
        website_id = request.POST.get('website_id')
        try:
            website = Websites.objects.get(pk=website_id)
            cliente = Cliente.objects.get(user=request.user)
            if cliente.solde >= website.prix:
                try:
                    getfree_website = GetFreeWebsites.objects.create(cliente=cliente, websites=website, prix_free=website.prix)
                    messages.success(request, f"Website {website.name} purchased successfully!")
                    # Send email
                    send_email_GetFree_website(request, cliente, website.name, getfree_website.date_created, getfree_website.prix_free)
                except ValidationError as e:
                    #Error for get more than 1 website Free
                    error_message = e.messages[0]
                    messages.error(request, error_message)
            else:
                messages.error(request, "Insufficient balance to purchase this website.")
                return redirect('list_websites')
        except Cliente.DoesNotExist:
            messages.error(request, "Client does not exist.")
        except Websites.DoesNotExist:
            messages.error(request, "Website does not exist.")
    return redirect('WebSites')





# Email sending function send_email_loyer_website
def send_email_loyer_website(request, cliente, websiteName,websiteDate,websiteDateFine,websitePrix):
    mail_subject = "Location Website successfully"
    formatted_date = formats.date_format(websiteDate, "DATETIME_FORMAT")
    formatted_dateFin = formats.date_format(websiteDateFine, "DATETIME_FORMAT")
    formatted_price = formats.number_format(websitePrix)
    
    message = render_to_string("websitebuilder/send_email_loyer_website.html", {
        'user': cliente.user.username,
        'name_website': websiteName,
        'date_website': formatted_date,
        'DateFine_website': formatted_dateFin,
        'prix_website': formatted_price,
        'domain': get_current_site(request).domain,
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[cliente.user.email])
    email.content_subtype = "html"  
    
    if email.send():
        success_message = mark_safe(
            f'Dear <b>{cliente.user.username}</b>, Website Location <b>{websiteName}</b> has been successfully . '
            f'Please check your email <b>{cliente.user.email}</b> for more details.'
        )
        messages.success(request, success_message)
    else:
        messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




#confirm_loyer_website loyer website with chose period of loyer with prix 
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def confirm_loyer_website(request):
    if request.method == 'POST':
        website_id = request.POST.get('website_id')
        rental_period = int(request.POST.get('rental_period', 1))  # Default to 1 month if not provided
        website = get_object_or_404(Websites, pk=website_id)
        cliente = request.user.cliente
        
        total_price = website.prix_loyer * rental_period

        # Check if the cliente has enough solde
        if cliente.solde < total_price:
            messages.error(request, "You do not have enough solde to rent this website.")
            return redirect('list_websites')  
        
        # Create the LocationWebsites
        date_debut = timezone.now()
        date_fin = date_debut + timedelta(days=30 * rental_period)
        Location_website = LocationWebsites.objects.create(
            cliente=cliente,
            websites=website,
            prix_loyer=total_price,
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        cliente.solde -= total_price
        cliente.save()
        
        # Send email
        send_email_loyer_website(request, cliente, website.name, date_debut, date_fin, total_price)
        messages.success(request, "Website rented successfully.")
        return redirect('WebSites')  
    else:
        messages.error(request, "Invalid request.")
        return redirect('list_websites')




#The client can buy a support, Maybe i need deleted this because i use just confirm_Achat_support
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def Achat_support(request, support_id):
    if request.user.is_authenticated:
        try:
            support = Supports.objects.get(pk=support_id)
            cliente = Cliente.objects.get(user=request.user)
            if cliente.solde >= support.prix:
                # Create a table in the AchatSupport model
                AchatSupport.objects.create(cliente=cliente, support=support, solde=support.prix)
                messages.success(request, f"Support {support.name} purchased successfully!")
                return redirect('clients/Services')
            else:
                messages.error(request, "Insufficient balance to purchase this support.")
                return redirect('clients/list_services')
        except Supports.DoesNotExist:
            messages.error(request, "Support does not exist.")
            return redirect('clients/list_services')
        except Cliente.DoesNotExist:
            messages.error(request, "Client does not exist.")
            return redirect('clients/list_services')
    else:
        messages.error(request, "You need to be logged in to purchase a Support.")
        return redirect('clients/Services')




#The client can buy a support, but after confirming
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def confirm_Achat_support(request):
    if request.method == 'POST':
        support_id = request.POST.get('support_id')
        try:
            support = Supports.objects.get(pk=support_id)
            cliente = Cliente.objects.get(user=request.user)
            if cliente.solde >= support.prix:
                # Create a table in the AchatSupport model
                AchatSupport.objects.create(cliente=cliente, support=support, prix=support.prix)
                messages.success(request, f"Support {support.name} purchased successfully!")
                return redirect('Services')
            else:
                messages.error(request, "Insufficient balance to purchase this support.")
        except Cliente.DoesNotExist:
            messages.error(request, "Client does not exist.")
        except Supports.DoesNotExist:
            messages.error(request, "Support does not exist.")
    return redirect('Services')




# # The client can activate a support
# @login_required(login_url='login')
# @allowedUsers(allowedGroups=['Cliente'])
# def consome_demande_support(request, support_id):
#     if request.method == 'POST':
#         try:
#             cliente = Cliente.objects.get(user=request.user)
#             achat_support = AchatSupport.objects.get(pk=support_id)
            
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

#                 # Send email to the client
#                 # Uncomment and customize the send_email_support_active function as needed
#                 # send_email_support_active(request, cliente, demande_support.code_DemandeSupport)

#                 messages.success(request, "Support consumed successfully and email sent to the client.")
#                 return redirect('/Services') 
#             else:
#                 messages.error(request, "Support is already consumed.")
#         except AchatSupport.DoesNotExist:
#             messages.error(request, "AchatSupport with the specified ID does not exist.")
#         except Cliente.DoesNotExist:
#             messages.error(request, "Cliente with the specified ID does not exist.")

#     return redirect('/Services')




# Email sending send_email_support_active function
def send_email_support_active(request, cliente, code_DemandeSupport):
    mail_subject = "Support Active Confirmation"
    message = render_to_string("websitebuilder/send_email_support_active.html", {
        'user': cliente.user.username,
        'support_code': code_DemandeSupport,
        'domain': get_current_site(request).domain,
        "protocol": 'https' if request.is_secure() else 'http'
    })

    email = EmailMessage(mail_subject, message, to=[cliente.user.email])
    email.content_subtype = "html"  
    
    if email.send():
        success_message = mark_safe(
            f'Dear <b>{cliente.user.username}</b>, the support with code <b>{code_DemandeSupport}</b> has been successfully activated. '
            f'Please check your email <b>{cliente.user.email}</b> for more details.'
        )
        messages.success(request, success_message)
    else:
        messages.error(request, f'Problem sending email to {cliente.user.email}, check if you typed it correctly.')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def confirm_consome_demande_support(request):
    if request.method == 'POST':
        support_id = request.POST.get('support_id')
        try:
            achat_support = AchatSupport.objects.get(pk=support_id)
            cliente = Cliente.objects.get(user=request.user)

            if achat_support.Status == 'No Active':
                achat_support.Status = 'Active'
                achat_support.save()

                # Create DemandeSupport
                code_DemandeSupport = generate_DemandeSupport_code(cliente.nom, cliente.prenom, achat_support.support.name)
                demande_support = DemandeSupport.objects.create(
                    cliente=cliente,
                    achat_support=achat_support,
                    status='Not Done yet',
                    code_DemandeSupport=code_DemandeSupport
                )

                # Send confirmation email
                send_email_support_active(request, cliente, demande_support.code_DemandeSupport)
                messages.success(request, "Support activated successfully and email sent with the Demande Support code.")
            else:
                messages.error(request, "Support is already active.")
        except AchatSupport.DoesNotExist:
            messages.error(request, "AchatSupport with the specified ID does not exist.")
        except Cliente.DoesNotExist:
            messages.error(request, "Cliente with the specified ID does not exist.")

    return redirect('Services')



@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def add_websiteBuilder(request):
    if request.method == 'POST':
        name_website = request.POST.get('nameWebsite')
        cliente_id = request.POST.get('cliente_id')
        achat_website_id = request.POST.get('website_id')
        
        # Check if the nameWebsite already exists
        if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
            messages.error(request, 'A Name of a website with this name already exists choose another name of your website.')
            return redirect('clients/WebSites') 
        
        achat_website = get_object_or_404(AchatWebsites, pk=achat_website_id)
        
        # Create a new WebsiteBuilder
        website_builder = WebsiteBuilder.objects.create(
            nameWebsite=name_website,
            cliente_id=cliente_id,
            achat_website=achat_website
        )
        
        
        # Create a new MergedWebsiteBuilder
        MergedWebsiteBuilder.objects.create(
            cliente_id=cliente_id,
            website_builder=website_builder,
            website=achat_website.websites
        )
        
        achat_website.BuilderStatus = 'in progress'
        achat_website.save()
        
        
        messages.success(request, 'Website in the progress of builder please wait 1 minute and your website will be built.')
        return redirect('WebSites') 
    else:
        return render(request, 'WebSites.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def add_GetFreeWebsiteBuilder(request):
    if request.method == 'POST':
        name_website = request.POST.get('nameWebsite')
        cliente_id = request.POST.get('cliente_id')
        getfree_website_id = request.POST.get('website_id')
        
        if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
            messages.error(request, 'A Name of a website with this name already exists choose another name of your website.')
            return redirect('WebSites') 
        
        getfree_website = get_object_or_404(GetFreeWebsites, pk=getfree_website_id)
        
        # Create a new GetFreeWebsiteBuilder
        getfree_website_builder = GetFreeWebsiteBuilder.objects.create(
            nameWebsite=name_website,
            cliente_id=cliente_id,
            getfree_website=getfree_website
        )
        
        # Create a new MergedWebsiteBuilder
        MergedWebsiteBuilder.objects.create(
            cliente_id=cliente_id,
            getfree_website_builder=getfree_website_builder,
            website=getfree_website_builder.website
        )
        
        getfree_website.BuilderStatus = 'in progress'
        getfree_website.save()

        messages.success(request, 'Website in the progress of builder please wait 1 minute and your website will be built.')
        return redirect('WebSites') 
    else:
        return render(request, 'WebSites.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def add_locationWebsiteBuilder(request):
    if request.method == 'POST':
        name_website = request.POST.get('nameWebsite')
        cliente_id = request.POST.get('cliente_id')
        location_website_id = request.POST.get('website_id')
        
        # Check if the nameWebsite already exists
        if LocationWebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or WebsiteBuilder.objects.filter(nameWebsite=name_website).exists() or GetFreeWebsiteBuilder.objects.filter(nameWebsite=name_website).exists():
            messages.error(request, 'A website with this name already exists, please choose another name.')
            return redirect('WebSites')
        
        location_website = get_object_or_404(LocationWebsites, pk=location_website_id)
        
        # Create a new LocationWebsiteBuilder
        location_website_builder = LocationWebsiteBuilder.objects.create(
            nameWebsite=name_website,
            cliente_id=cliente_id,
            location_website=location_website
        )
        
        # Create a new MergedWebsiteBuilder
        MergedWebsiteBuilder.objects.create(
                cliente_id=cliente_id,
                location_website_builder=location_website_builder,
                website=location_website.websites
            )
            
        location_website.BuilderStatus = 'in progress'
        location_website.save()
    
        messages.success(request, 'Website building is in progress, please wait a minute for your website to be built.')
        return redirect('WebSites')
    else:
        return render(request, 'WebSites.html')





def edite_website(request, website_name):
    cliente = request.user.cliente  
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
    website_builder = get_object_or_404(WebsiteBuilder, nameWebsite=website_name)
    merged_website_builder = MergedWebsiteBuilder.objects.filter(website_builder=website_builder).first()

    suspendre_exists = Website_need_suspendre.objects.filter(website_builder=website_builder).exists()
    reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(website_builder=website_builder).exists()
    
    
    suspendre_request = Website_need_suspendre.objects.filter(website_builder=website_builder).first()
    suspendre_request_status = suspendre_request.statut if suspendre_request else None
    
    
    
    
    reset_request = website_need_reset.objects.filter(website_builder=website_builder).first()
    reset_status = reset_request.statut if reset_request else None
    
    delete_exists = Websites_Need_Delete.objects.filter(website_builder=website_builder).first()
    delete_status = delete_exists.statut if delete_exists else None
    
    
    context = {
        'website_builder': website_builder,
        'merged_website_builder': merged_website_builder,
        'suspendre_exists':suspendre_exists,
        'reprendre_suspendre_exists':reprendre_suspendre_exists,  
        'reset_request' : reset_request,
        'reset_status': reset_status,
        'delete_exists':delete_exists,
        'delete_status':delete_status,
        'WebsiteBuilders':WebsiteBuilders,  
        'suspendre_request_status':suspendre_request_status,   
    }
    return render(request, "clients/EditeWebsite.html", context)





@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente']) 
def edite_free_website(request, website_name):
    cliente = request.user.cliente  
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
    getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, nameWebsite=website_name)
    merged_website_builder = MergedWebsiteBuilder.objects.filter(getfree_website_builder=getfree_website_builder).first()

    suspendre_exists = Website_need_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).exists()
    reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).exists()
    
    reset_request = website_need_reset.objects.filter(getfree_website_builder=getfree_website_builder).first()
    reset_status = reset_request.statut if reset_request else None
    
    delete_exists = Websites_Need_Delete.objects.filter(getfree_website_builder=getfree_website_builder).first()
    delete_status = delete_exists.statut if delete_exists else None
    
    context = {
        'getfree_website_builder': getfree_website_builder,
        'merged_website_builder': merged_website_builder,
        'suspendre_exists': suspendre_exists,
        'reprendre_suspendre_exists': reprendre_suspendre_exists,  
        'reset_request': reset_request,
        'reset_status': reset_status,
        'delete_exists': delete_exists,
        'delete_status': delete_status,
        'WebsiteBuilders': WebsiteBuilders,     
    }
    return render(request, "clients/EditeWebsiteGetFree.html", context)





def edite_website_Location(request, nameWebsite):
    cliente = request.user.cliente  
    WebsiteBuilders = MergedWebsiteBuilder.objects.filter(cliente=cliente).order_by('-date_created')[:6]
    
    website_builder_location = get_object_or_404(LocationWebsiteBuilder, nameWebsite=nameWebsite)
    merged_website_builder = MergedWebsiteBuilder.objects.filter(location_website_builder=website_builder_location).first()
    
    current_datetime = timezone.now()
    
    date_fin_date = website_builder_location.location_website.date_fin.date()

    current_date = current_datetime.date()
    
    expiration_delta = current_date - date_fin_date
    
    # Compare if the expiration date has passed
    expiration_passed = expiration_delta.days < 0

    # Check if a resiliation exists
    resiliation_exists = Website_need_resiliation.objects.filter(location_website_builder=website_builder_location).exists()
    reprendre_exists = Website_reprendre_resiliation.objects.filter(location_website_builder=website_builder_location).exists()

    suspendre_exists = Website_need_suspendre.objects.filter(location_website_builder=website_builder_location).exists()
    reprendre_suspendre_exists = Website_reprendre_suspendre.objects.filter(location_website_builder=website_builder_location).exists()
    
    
    suspendre_request = Website_need_suspendre.objects.filter(location_website_builder=website_builder_location).first()
    suspendre_request_status = suspendre_request.statut if suspendre_request else None
    
    reset_request = website_need_reset.objects.filter(location_website_builder=website_builder_location).first()
    reset_status = reset_request.statut if reset_request else None

    delete_exists = Websites_Need_Delete.objects.filter(location_website_builder=website_builder_location).first()
    delete_status = delete_exists.statut if delete_exists else None
    
    context = {
        'website_builder_location': website_builder_location,
        'merged_website_builder': merged_website_builder,
        'expiration_passed': expiration_passed,
        'resiliation_exists': resiliation_exists,
        'reprendre_exists': reprendre_exists,
        'suspendre_exists':suspendre_exists,
        'reprendre_suspendre_exists':reprendre_suspendre_exists,
        'reset_request' : reset_request,
        'reset_status': reset_status,
        'delete_exists':delete_exists,
        'delete_status':delete_status,
        'WebsiteBuilders':WebsiteBuilders, 
        'suspendre_request':suspendre_request,  
        'suspendre_request_status':suspendre_request_status,  
    }
    return render(request, "clients/EditeWebsiteLocation.html", context)




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_website_resiliation(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        location_website_builder_id = request.POST.get('location_website_builder_id')
        website_id = request.POST.get('website_id')

        cliente = get_object_or_404(Cliente, pk=cliente_id)
        location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
        website = get_object_or_404(Websites, pk=website_id)
        
        # Check if a Website_need_resiliation is exists for this location_website_builder
        if Website_reprendre_resiliation.objects.filter(location_website_builder=location_website_builder).exists():
            Website_reprendre_resiliation.objects.filter(location_website_builder=location_website_builder).delete()

        Website_need_resiliation.objects.create(
            cliente=cliente,
            location_website_builder=location_website_builder,
            statut='0', 
            website=website
        )
        
        location_website_builder.Statu_du_website = '3'
        location_website_builder.save()

        messages.success(request, 'La demande de Résiliation a été envoyée.')
        
        if location_website_builder_id:
            return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
          
        # return redirect('WebSites')  
    else:
        return render(request, 'EditeWebsiteLocation.html')



@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_website_reprendre(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        location_website_builder_id = request.POST.get('location_website_builder_id')
        website_id = request.POST.get('website_id')

        cliente = get_object_or_404(Cliente, pk=cliente_id)
        location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
        website = get_object_or_404(Websites, pk=website_id)

        # Check if a Website_need_resiliation is exists for this location_website_builder
        if Website_need_resiliation.objects.filter(location_website_builder=location_website_builder).exists():
            Website_need_resiliation.objects.filter(location_website_builder=location_website_builder).delete()

        Website_reprendre_resiliation.objects.create(
            cliente=cliente,
            location_website_builder=location_website_builder,
            statut='0',  
            website=website
        )
        
        location_website_builder.Statu_du_website = '1' 
        location_website_builder.save()

        messages.success(request, 'La demande de Reprendre a été envoyée.')
        
        if location_website_builder_id:
            return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
          
        # return redirect('WebSites')  
    else:
        return render(request, 'EditeWebsiteLocation.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_website_suspendre(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        location_website_builder_id = request.POST.get('location_website_builder_id')
        getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
        website_builder_id = request.POST.get('website_builder_id')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        location_website_builder = None
        website_builder = None
        getfree_website_builder = None  

        if location_website_builder_id:
            location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)

        if website_builder_id:
            website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)
            
        if getfree_website_builder_id:
            getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)  # Corrected here


        # Delete existing Website_reprendre_suspendre records if they exist
        if location_website_builder:
            Website_reprendre_suspendre.objects.filter(location_website_builder=location_website_builder).delete()
        if website_builder:
            Website_reprendre_suspendre.objects.filter(website_builder=website_builder).delete()
        if getfree_website_builder:
            Website_reprendre_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).delete()


        Website_need_suspendre.objects.create(
            cliente=cliente,
            location_website_builder=location_website_builder,
            website_builder=website_builder,
            getfree_website_builder=getfree_website_builder, 
            statut='0', 
        )

        if location_website_builder:
            location_website_builder.Statu_du_website = '2'  
            location_website_builder.save()
            
        if website_builder:
            website_builder.Statu_du_website = '2' 
            website_builder.save()
            
        if getfree_website_builder:
            getfree_website_builder.Statu_du_website = '2' 
            getfree_website_builder.save()

        messages.success(request, 'La demande de suspendre a été envoyée.')
        
        if location_website_builder_id:
            return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
        if website_builder_id:
            return redirect('edite_website', website_name=website_builder.nameWebsite)
        
        if getfree_website_builder_id:
            return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
    # return redirect('WebSites')  # Redirect to WebSites if none of the conditions are met
    # else:
    #     return render(request, 'clients/EditeWebsiteLocation.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_website_suspendre_reprendre(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        location_website_builder_id = request.POST.get('location_website_builder_id')
        getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
        website_builder_id = request.POST.get('website_builder_id')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        location_website_builder = None
        website_builder = None
        getfree_website_builder = None 

        if location_website_builder_id:
            try:
                location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)
            except LocationWebsiteBuilder.DoesNotExist:
                pass  

        if website_builder_id:
            try:
                website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)
            except WebsiteBuilder.DoesNotExist:
                pass  
        
        if getfree_website_builder_id:
            try:
                getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)
            except WebsiteBuilder.DoesNotExist:
                pass


        if location_website_builder:
            Website_need_suspendre.objects.filter(location_website_builder=location_website_builder).delete()
        if website_builder:
            Website_need_suspendre.objects.filter(website_builder=website_builder).delete()
        if getfree_website_builder:
            Website_need_suspendre.objects.filter(getfree_website_builder=getfree_website_builder).delete()


        if location_website_builder or website_builder or getfree_website_builder :
            Website_reprendre_suspendre.objects.create(
                cliente=cliente,
                location_website_builder=location_website_builder,
                getfree_website_builder=getfree_website_builder, 
                website_builder=website_builder,
                statut='0', 
            )


            if location_website_builder:
                location_website_builder.Statu_du_website = '1' 
                location_website_builder.save()

            if website_builder:
                website_builder.Statu_du_website = '1' 
                website_builder.save()
                
            if getfree_website_builder:
                getfree_website_builder.Statu_du_website = '1' 
                getfree_website_builder.save()

            messages.success(request, 'La demande de Reprendre de suspendre a été envoyée.')
        else:
            messages.error(request, 'Required fields are missing.')
            
        if location_website_builder_id:
            return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
        if website_builder_id:
            return redirect('edite_website', website_name=website_builder.nameWebsite)

        if getfree_website_builder_id:
            return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)

        # return redirect('WebSites')
    else:
        return render(request, 'EditeWebsiteLocation.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_website_reset(request):
    if request.method == 'POST':
        cliente_id = request.POST.get('cliente_id')
        location_website_builder_id = request.POST.get('location_website_builder_id')
        getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
        website_builder_id = request.POST.get('website_builder_id')

        cliente = get_object_or_404(Cliente, pk=cliente_id)

        location_website_builder = None
        website_builder = None
        getfree_website_builder = None 


        if location_website_builder_id:
            location_website_builder = get_object_or_404(LocationWebsiteBuilder, pk=location_website_builder_id)

        if website_builder_id:
            website_builder = get_object_or_404(WebsiteBuilder, pk=website_builder_id)

        if getfree_website_builder_id:
            getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)


        website_need_reset.objects.create(
            cliente=cliente,
            location_website_builder=location_website_builder,
            getfree_website_builder=getfree_website_builder, 
            website_builder=website_builder,
            statut='0', 
        )

        # if location_website_builder:
        #     location_website_builder.Statu_du_website = '2'  
        #     location_website_builder.save()
            
            
        # if website_builder:
        #     website_builder.Statu_du_website = '2' 
        #     website_builder.save()


        messages.success(request, 'La demande de Reset a été envoyée.')
        if location_website_builder_id:
            return redirect('edite_website_Location', nameWebsite=location_website_builder.nameWebsite)
            
        if website_builder_id:
            return redirect('edite_website', website_name=website_builder.nameWebsite) 
        
        if getfree_website_builder_id:
            return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
    else:
        return render(request, 'EditeWebsiteLocation.html')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_period_location(request, location_id):
    if request.method == 'POST':
        location = get_object_or_404(LocationWebsites, pk=location_id)
        website_builder_location = request.POST.get('website_builder_location_id')
        rental_period = request.POST.get('rental_period')
        
        try:
            rental_period = int(rental_period)
        except ValueError:
            messages.error(request, "Invalid rental period.")
            return redirect('list_websites')
        
        cliente = request.user.cliente
        total_price = location.websites.prix_loyer * rental_period

        if cliente.solde < total_price:
            messages.error(request, "You do not have enough solde to extend this rental period.")
            return redirect('edite_website_Location', nameWebsite=website_builder_location)
        
        # new_end_date = timezone.now() + timedelta(days=30 * rental_period)
        new_end_date = location.date_fin + timedelta(days=30 * rental_period)

        location.date_fin = new_end_date
        location.save()
        
        cliente.solde -= total_price
        cliente.save()

        messages.success(request, f"Rental period extended by {rental_period} months.")
        return redirect('edite_website_Location', nameWebsite=website_builder_location)
    else:
        messages.error(request, "Invalid request.")
        return redirect('WebSites')




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_period_hebergement(request, achat_id):
    if request.method == 'POST':
        achat = get_object_or_404(AchatWebsites, pk=achat_id)
        website_builder_id = request.POST.get('website_builder_id')
        hebergement_period = request.POST.get('hebergement_period')
        
        try:
            hebergement_period = int(hebergement_period)
        except ValueError:
            messages.error(request, "Invalid hebergement_period period.")
            return redirect('list_websites')
        
        website_builder = get_object_or_404(WebsiteBuilder, nameWebsite=website_builder_id)

        cliente = request.user.cliente
        total_price = achat.websites.prix_hebergement * hebergement_period

        if cliente.solde < total_price:
            messages.error(request, "You do not have enough solde to extend this hebergement_period period.")
            return redirect('edit_website_location', nameWebsite=website_builder_id)
        
        new_end_date = website_builder.date_fin_hebergement + timedelta(days=30 * hebergement_period)

        website_builder.date_fin_hebergement = new_end_date
        website_builder.save()
        
        cliente.solde -= total_price
        cliente.save()

        messages.success(request, f"Hebergement period extended by {hebergement_period} months.")
        return redirect('edite_website', website_name=website_builder.nameWebsite) 
        
    else:
        messages.error(request, "Invalid request.")
        return redirect('WebSites')
 
 
 
 
 
@login_required(login_url='login')
@allowedUsers(allowedGroups=['Cliente'])
def add_period_free_hebergement(request, free_id):
    if request.method == 'POST':
        free = get_object_or_404(GetFreeWebsites, pk=free_id)
        getfree_website_builder_id = request.POST.get('getfree_website_builder_id')
        hebergement_period = request.POST.get('hebergement_period')
        
        try:
            hebergement_period = int(hebergement_period)
        except ValueError:
            messages.error(request, "Invalid hebergement_period period.")
            return redirect('list_websites')
        
        getfree_website_builder = get_object_or_404(GetFreeWebsiteBuilder, pk=getfree_website_builder_id)

        cliente = request.user.cliente
        total_price = free.websites.prix_hebergement * hebergement_period

        if cliente.solde < total_price:
            messages.error(request, "You do not have enough solde to extend this hebergement period.")
            return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
        new_end_date = getfree_website_builder.date_fin_hebergement + timedelta(days=30 * hebergement_period)

        getfree_website_builder.date_fin_hebergement = new_end_date
        getfree_website_builder.save()
        
        cliente.solde -= total_price
        cliente.save()

        messages.success(request, f"Hebergement period extended by {hebergement_period} months.")
        return redirect('edite_free_website', website_name=getfree_website_builder.nameWebsite)
        
    else:
        messages.error(request, "Invalid request.")
        return redirect('WebSites')

    
