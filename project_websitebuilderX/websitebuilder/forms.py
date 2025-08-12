from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm

from django import forms
from .models import *



from django import forms
from django.contrib.auth.models import User
from .models import Cliente

class ClienteForm(forms.ModelForm):
    username = forms.CharField()
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Cliente
        fields = ['prenom', 'nom', 'email', 'phone']

        
        
        
        

class AdministrateurForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name','email', 'phone']
      


from .models import Commercial

class CommercialForm(UserCreationForm):
    name = forms.CharField(max_length=100, required=True, label="Nom commercial")
    phone = forms.CharField(max_length=100, required=True, label="Téléphone")
    status = forms.ChoiceField(choices=Commercial.STATUS_CHOICES, label="Statut")

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'name', 'phone', 'status']



      

class SupportTechniqueForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name','email', 'phone']
        
        
        


class GestionnaireComptesForm(UserCreationForm):
    name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=100)
    phone = forms.CharField(max_length=100)
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'name','email', 'phone']
        
        
        
             
        
class DemandeRechargerForm(forms.ModelForm):
    class Meta:
        model = DemandeRecharger
        fields = ['solde', 'image'] 
   
      
      
      
        
class ClienteForm(UserCreationForm):
    prenom = forms.CharField(max_length=100, required=True)
    nom = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(max_length=200, required=True)
    phone = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'prenom', 'nom', 'phone']        
        
   
   
   
   
class AdditionalInfoForm(forms.ModelForm):
    address = forms.CharField(max_length=100, required=True)
    nom_entreprise = forms.CharField(max_length=100, required=True)
    numero_ice = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Cliente
        fields = ['address', 'nom_entreprise', 'numero_ice']     





class ClienteUpdateForm(forms.ModelForm):
    prenom = forms.CharField(max_length=100, required=True)
    nom = forms.CharField(max_length=100, required=True)
    email = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=100, required=True)

    class Meta:
        model = Cliente
        fields = ['prenom', 'nom', 'email', 'phone']
        
        
        

     
        
class ClientePasswordChangeForm(PasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        for fieldname in ['old_password', 'new_password1', 'new_password2']:
            self.fields[fieldname].widget.attrs.update({'class': 'form-control', 'placeholder': fieldname.capitalize()})
            
   


class InputForm(forms.Form):
    input_text = forms.CharField(label='Enter a Text for Générateur Description', max_length=1000)
    
    
    


# class TicketFilterForm(forms.Form):
#     code_ticket = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'placeholder': 'Code Ticket'})
#     )
#     date_created = forms.DateField(
#         required=False,
#         widget=forms.DateInput(attrs={'type': 'date'})
#     )
#     username_client = forms.CharField(
#         max_length=100,
#         required=False,
#         widget=forms.TextInput(attrs={'placeholder': 'Username Client'})
#     )
