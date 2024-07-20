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



