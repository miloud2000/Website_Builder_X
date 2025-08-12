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




@login_required(login_url='login')
@allowedUsers(allowedGroups=['Commercial']) 
def addCliente_c(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1']
            )

            Cliente.objects.create(
                user=user,
                prenom=form.cleaned_data['prenom'],
                nom=form.cleaned_data['nom'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                added_by=request.user  # ✅ فقط من أضافه
            )

            group = Group.objects.get(name="Cliente")
            user.groups.add(group)

            messages.success(request, f"{user.username} ajouté avec succès !")
            return redirect('ClienteCommercial')
        else:
            messages.error(request, "Formulaire invalide.")
    else:
        form = ClienteForm()

    return render(request, 'Commercial/addCliente.html', {'form': form})
