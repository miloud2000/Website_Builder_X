from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
import random
import string





class GestionnaireComptes(models.Model):
    Status= [
        ('Active', 'Active'),
        ('No Active	', 'No Active'),
    ]
    user = models.OneToOneField(User, null=True, blank=False, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    Status = models.CharField(max_length=50, default='Active', null=True)  # choices=Status,
    slugGestionnaireComptes= models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slugGestionnaireComptes:
            self.slugGestionnaireComptes = slugify(self.user.username) #slugify(self.user.username) 
        super().save(*args, **kwargs)
  
        
    def __str__(self):
        return self.name
    





def generate_cliente_code(nom, prenom):
    first_letter_nom = nom[0].upper() if nom else ''
    first_letter_prenom = prenom[0].upper() if prenom else ''
    random_digits = ''.join(random.choices(string.digits, k=4))
    code = f'ALT-{first_letter_nom}{first_letter_prenom}{random_digits}'
    return code





class Cliente(models.Model):
    user = models.OneToOneField(User, null=True, blank=False, on_delete=models.SET_NULL)
    prenom = models.CharField(max_length=100, null=True)
    nom = models.CharField(max_length=100, null=True)
    email = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    slugCliente = models.SlugField(blank=True, null=True)
    code_client = models.CharField(max_length=100, null=True)
    updated_by = models.ForeignKey(GestionnaireComptes, on_delete=models.SET_NULL, null=True, blank=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='added_clients')
    address = models.CharField(max_length=255, null=True, blank=True)
    nom_entreprise = models.CharField(max_length=255, null=True, blank=True)
    numero_ice = models.CharField(max_length=100, null=True, blank=True)
    photo = models.ImageField(null=True, blank=True)


    def save(self, *args, **kwargs):
        if not self.slugCliente:
            self.slugCliente = slugify(self.user.username) #slugify(self.user.username) 
        if not self.code_client:
            self.code_client = generate_cliente_code(self.nom, self.prenom)
        super().save(*args, **kwargs)

    
    def __str__(self):
        return f"{self.nom} {self.prenom}"






def generate_DemandeRecharger_code(nom, prenom):
    first_letter_prenom = prenom[0].upper() if prenom else ''
    first_letter_nom = nom[0].upper() if nom else ''
    random_digits = ''.join(random.choices(string.digits, k=4))
    code = f'D-{first_letter_prenom}{first_letter_nom}-{random_digits}'
    return code






class DemandeRecharger(models.Model):
    Status = [
        ('Done', 'Done'),
        ('Not Done yet', 'Not Done yet'),
        ('inacceptable', 'inacceptable'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(GestionnaireComptes, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status, default='Not Done yet', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(null=True)
    motifNonAcceptation = models.CharField(max_length=100, null=True)
    code_DemandeRecharger = models.CharField(max_length=100, null=True)
    
    def save(self, *args, **kwargs):
        if not self.code_DemandeRecharger:
            self.code_DemandeRecharger = generate_DemandeRecharger_code(self.cliente.nom, self.cliente.prenom)
        super().save(*args, **kwargs)
  
    def __str__(self):
        return f"Demande {self.cliente.user.username} Recharger Solde {self.solde} MAD"






class LaTraceDemandeRecharger(models.Model):
    demande_recharger = models.ForeignKey(DemandeRecharger, on_delete=models.CASCADE)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(GestionnaireComptes, on_delete=models.SET_NULL, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(null=True)

  
    def __str__(self):
         return f"Gestionnaire des Comptes {self.updated_by.user.username} Update Solde of {self.cliente.user.username} with Solde {self.solde} MAD of code Demande {self.demande_recharger.code_DemandeRecharger} "









class Administrateur(models.Model):
    Status= [
        ('Active', 'Active'),
        ('No Active	', 'No Active'),
    ]
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    Status = models.CharField(max_length=50, default='Active', null=True)  # choices=Status,
    slugAdministrateur = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slugAdministrateur:
            self.slugAdministrateur = slugify(self.user.username) #slugify(self.user.username) 
        super().save(*args, **kwargs)
  
        
    def __str__(self):
        return self.name
    
    


class AdminActionLog(models.Model):
    admin = models.ForeignKey(User, on_delete=models.CASCADE) 
    action_type = models.CharField(max_length=100)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.admin.username} - {self.action_type} - {self.timestamp.strftime('%d/%m/%Y %H:%M')}"

    
    

    
    
class SupportTechnique(models.Model):
    Status= [
        ('Active', 'Active'),
        ('No Active	', 'No Active'),
    ]
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    Status = models.CharField(max_length=50, default='Active', null=True)  # choices=Status,
    slugSupportTechnique = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slugSupportTechnique:
            self.slugSupportTechnique = slugify(self.user.username) #slugify(self.user.username) 
        super().save(*args, **kwargs)
  
        
    def __str__(self):
        return self.name
    
    
    
    
    

class Commercial(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    user = models.OneToOneField(User, null=True, blank=False, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100, null=True)  
    email = models.EmailField(max_length=100, null=True)
    phone = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Active', null=True)
    slugCommercial = models.SlugField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slugCommercial and self.name:
            self.slugCommercial = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



    
    
    
# def generate_Website_code(name, date_created):
#     first_letters = name[:4].upper() if name else ''
#     short_date_created = date_created.strftime('%y%m') if date_created else ''
#     random_digits = ''.join(random.choices(string.digits, k=4))
#     code = f'WEB-{first_letters}{short_date_created}{random_digits}'
#     return code

    
    
class Websites(models.Model):
    Status = [
        ('Active', 'Active'),
        ('No Active', 'No Active'),
    ]
    Catégories = [
        ('Ecommerce', 'Ecommerce'),
        ('Blogs', 'Blogs'),
        ('Business', 'Business'),
        ('portfolio', 'portfolio'),
        ('Educational', 'Educational'),
        ('News', 'News'),
    ]
    cms = [
        ('WordPress', 'WordPress'),
        ('Drupal', 'Drupal'),
    ]
    langues = [
        ('Français', 'Français'),
        ('Anglais', 'Anglais'),
    ]
    plans = [
        ('Free', 'Free'),
        ('Payant', 'Payant'),
    ]
    name = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, choices=Status, default='Active', null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    prix_loyer = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    prix_hebergement = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    slugWebsites = models.SlugField(blank=True, null=True)
    image = models.ImageField(null=True)
    description = models.CharField(max_length=1000, null=True, blank=True)  
    video = models.URLField(null=True, blank=True)  # New field for video
    CMS = models.CharField(max_length=50, choices=cms, default='WordPress', null=True)
    langues = models.CharField(max_length=50, choices=langues, default='Français', null=True)
    catégorie = models.CharField(max_length=50, choices=Catégories, default='Ecommerce', null=True)
    plan = models.CharField(max_length=50, choices=plans, default='Free', null=True)
    is_visible = models.BooleanField(default=True)
    # code_Website = models.CharField(max_length=100, null=True)


    def save(self, *args, **kwargs):
        if not self.slugWebsites:
            self.slugWebsites = slugify(self.name)
        # if not self.code_Website:
        #     self.code_Website = generate_Website_code(self.name, self.date_created)
        super().save(*args, **kwargs)
  
        
    def __str__(self):
        return self.name



from django.core.exceptions import ValidationError

class GetFreeWebsites(models.Model):
    BuilderStatus = [
        ('Builder', 'Builder'),
        ('in progress', 'in progress'),
        ('Not yet', 'Not yet'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    websites = models.ForeignKey(Websites, on_delete=models.CASCADE)
    prix_free = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    BuilderStatus = models.CharField(max_length=50, choices=BuilderStatus, default='Not yet', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # Check the client has a 1 free website
            if GetFreeWebsites.objects.filter(cliente=self.cliente).exists():
                # raise ValidationError(f"The client {self.cliente} already has a free website.")
                raise ValidationError("You have one free website, and this is the most you can take for free.")
            self.cliente.solde -= self.websites.prix
            self.cliente.save()
        super().save(*args, **kwargs)
        
    @property
    def transaction_type(self):
        return 'GetFreeWebsite'

    def __str__(self):
        return f"Get Free {self.cliente.user.username} le site Web {self.websites.name} pour {self.websites.prix} MAD"




class AchatWebsites(models.Model):
    BuilderStatus= [
        ('Builder', 'Builder'),
        ('in progress', 'in progress'),
        ('Not yet', 'Not yet'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    websites = models.ForeignKey(Websites, on_delete=models.CASCADE)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    BuilderStatus = models.CharField(max_length=50, choices=BuilderStatus, default='Not yet', null=True)  # choices=Status,
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    # date_debut = models.DateTimeField(null=True, blank=True)
    # date_fin = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Initialize is_new before using it
        if is_new:
            self.cliente.solde -= self.websites.prix
            self.cliente.save()
        super().save(*args, **kwargs)
        if is_new:
            Facturations.objects.create(
                location_website=None,
                achat_website=self,
                getfree_website=None,
                achat_support=None,
                cliente=self.cliente,
                website=self.websites,
                support=None,
                code_facturation=generate_facturation_code(self.cliente.user.username),
                date_created=timezone.now()
            )

    def website_builder(self):
        return WebsiteBuilder.objects.filter(achat_website=self).first()

    @property
    def transaction_type(self):
        return 'AchatWebsites'

    def __str__(self):
        return f"Acheté {self.cliente.user.username} le site Web {self.websites.name} pour {self.websites.prix} MAD"



from django.utils import timezone
from datetime import timedelta

class LocationWebsites(models.Model):
    BuilderStatus= [
        ('Builder', 'Builder'),
        ('in progress', 'in progress'),
        ('Not yet', 'Not yet'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    websites = models.ForeignKey(Websites, on_delete=models.CASCADE)
    prix_loyer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    BuilderStatus = models.CharField(max_length=50, choices=BuilderStatus, default='Not yet', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    date_debut = models.DateTimeField(null=True, blank=True)
    date_fin = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Initialize is_new before using it
        if is_new:
            # Set date_debut to now
            self.date_debut = timezone.now()
            # You mentioned this line needs to be deleted from this code because you add it in view.py
            # self.date_fin = self.date_debut + timedelta(days=30)
            
            # Update the solde of Cliente only when creating
            # self.cliente.solde -= self.websites.prix
            # self.cliente.save()

        super().save(*args, **kwargs)

        if is_new:
            Facturations.objects.create(
                location_website=self,
                achat_website=None,
                getfree_website=None,
                achat_support=None,
                cliente=self.cliente,
                website=self.websites,
                support=None,
                code_facturation=generate_facturation_code(self.cliente.user.username),
                date_created=timezone.now()
            )

    @property
    def transaction_type(self):
        return 'LocationWebsites'

    def __str__(self):
        return f"Location {self.cliente.user.username} le site Web {self.websites.name}"


# return f"Achat for {self.cliente.nom} on {self.websites.name} on {self.websites.prix} MAD"



class Supports(models.Model):
    StatusDisponible = [
        ('Disponible', 'Disponible'),
        ('No Disponible', 'No Disponible'),
    ]
    name = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=1000, null=True, blank=True) 
    status = models.CharField(max_length=50, choices=StatusDisponible, default='Disponible', null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0) 
    slugSupport = models.SlugField(blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    # code_Website = models.CharField(max_length=100, null=True)


    def save(self, *args, **kwargs):
        if not self.slugSupport:
            self.slugSupport = slugify(self.name)
        super().save(*args, **kwargs)
  
        
    def __str__(self):
        return self.name





class AchatSupport(models.Model):
    Status = [
        ('Active', 'Active'),
        ('No Active', 'No Active'),
    ]
    StatusConsomé = [
        ('Consomé', 'Consomé'),
        ('Not Consomé', 'Not Consomé'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    support = models.ForeignKey(Supports, on_delete=models.CASCADE)
    updated_by = models.ForeignKey(SupportTechnique, on_delete=models.SET_NULL, null=True, blank=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Status = models.CharField(max_length=50, choices=Status, default='No Active', null=True)
    StatusConsomé = models.CharField(max_length=50, choices=StatusConsomé, default='Not Consomé', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Initialize is_new before using it

        if is_new:
            # Deduct support prix from cliente solde
            self.cliente.solde -= self.support.prix
            self.cliente.save()

        super().save(*args, **kwargs)

        if is_new:
            # Create Websites_client_statu only if this is a new instance
            Websites_client_statu.objects.create(
                cliente=self.cliente,
                achat_support=self,
                support=self.support,
                date_created=self.date_created,
            )
            
            Facturations.objects.create(
                location_website=None,
                achat_website=None,
                getfree_website=None,
                achat_support=self,
                cliente=self.cliente,
                website=None,
                support=self.support,
                code_facturation=generate_facturation_code(self.cliente.user.username),
                date_created=timezone.now()
            )

    def __str__(self):
        return f"Acheté {self.cliente.user.username} le support {self.support.name} pour {self.support.prix} MAD"






def generate_DemandeSupport_code(nom, prenom,name):
    first_letter_prenom = prenom[0].upper() if prenom else ''
    first_letter_nom = nom[0].upper() if nom else ''
    nom_support = name.replace(' ', '')
    random_digits = ''.join(random.choices(string.digits, k=4))
    code = f'D-{nom_support}-{first_letter_nom}{first_letter_prenom}-{random_digits}'
    return code




class DemandeSupport(models.Model):
    Status = [
        ('Done', 'Done'),
        ('Not Done yet', 'Not Done yet'),
    ]
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    achat_support = models.ForeignKey(AchatSupport, on_delete=models.CASCADE) 
    updated_by = models.ForeignKey(SupportTechnique, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=Status, default='Not Done yet', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    code_DemandeSupport = models.CharField(max_length=100, null=True)
    
    def save(self, *args, **kwargs):
        if not self.code_DemandeSupport:
            self.code_DemandeSupport = generate_DemandeSupport_code(self.cliente.nom, self.cliente.prenom, self.achat_support.support.name)
        super().save(*args, **kwargs)
  
    def __str__(self):
        return self.achat_support.support.name
 

  
    
class GetFreeWebsiteBuilder(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
    ]
    STATUS_CHOICES_1 = [
        ('1', '1'),  #service actif
        ('2', '2'),  #suspendu
        ('3', '3'),  #demande de résiliation
        ('4', '4'),  #paiement en retard 
        ('5', '5'),  #en attente de suppression 
        ('6', '6'),  #Supprimé
    ]  

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    getfree_website = models.ForeignKey(GetFreeWebsites, on_delete=models.CASCADE)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    db_port = models.CharField(max_length=30, null=True, blank=True)
    app_port = models.CharField(max_length=30, null=True, blank=True)
    nameWebsite = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    Statu_du_website = models.CharField(max_length=50, choices=STATUS_CHOICES_1, default='1', null=True)
    date_build = models.DateTimeField(null=True, blank=True)
    date_hebergement = models.DateTimeField(null=True, blank=True)
    date_fin_hebergement = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.getfree_website.websites.name}-{self.cliente.user.username}-{self.nameWebsite}"

    def save(self, *args, **kwargs):
        if self.getfree_website:
            self.website = self.getfree_website.websites
             
        # Set date_build if not already set
        if not self.date_build:
            self.date_build = timezone.now()
        
        # Set date_hebergement and date_fin_hebergement if not already set
        if not self.date_hebergement:
            self.date_hebergement = timezone.now()
            self.date_fin_hebergement = self.date_hebergement + timedelta(days=360)
            
        # Check if the status is being set to '1' during modification
        if self.status == '1' and self.pk:
            # Update only when status is set to '1'
            if self.getfree_website:
                self.getfree_website.BuilderStatus = 'Builder'
                self.getfree_website.save()

        super().save(*args, **kwargs)
        
        existing_entry = Websites_client_statu.objects.filter(getfree_website_builder=self).first()
        if existing_entry:
            existing_entry.cliente = self.cliente
            existing_entry.website = self.website
            existing_entry.date_created = self.date_created
            existing_entry.save()
        else:
            Websites_client_statu.objects.create(
                cliente=self.cliente,
                getfree_website_builder=self,
                website=self.website,
                date_created=self.date_created,
            )
 

  
    
    
    
class WebsiteBuilder(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
    ]
    STATUS_CHOICES_1 = [
        ('1', '1'),  #service actif
        ('2', '2'),  #suspendu
        ('3', '3'),  #demande de résiliation
        ('4', '4'),  #paiement en retard 
        ('5', '5'),  #en attente de suppression 
        ('6', '6'),  #Supprimé

        
    ]
    # STATUS_CHOICES_2 = [ 
    #     ('0', '0'),  #non actif
    #     ('1', '1'),  #service actif
    #     ('2', '2'),  #suspendu
    #     ('3', '3'),  #résilier
    #     ('4', '4'),  #deleted 
    # ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    achat_website = models.ForeignKey(AchatWebsites, on_delete=models.CASCADE)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    db_port = models.CharField(max_length=30, null=True, blank=True)
    app_port = models.CharField(max_length=30, null=True, blank=True)
    nameWebsite = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    Statu_du_website = models.CharField(max_length=50, choices=STATUS_CHOICES_1, default='1', null=True)
    # Statu_du_website_action = models.CharField(max_length=50, choices=STATUS_CHOICES_2, default='1', null=True)
    date_build = models.DateTimeField(null=True, blank=True)
    date_hebergement = models.DateTimeField(null=True, blank=True)
    date_fin_hebergement = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
  
    def __str__(self):
        return f"{self.achat_website.websites.name}-{self.cliente.user.username}-{self.nameWebsite}"

    def save(self, *args, **kwargs):
        # Ensure the website field is set correctly from achat_website
        if self.achat_website:
            self.website = self.achat_website.websites
             
        # Set date_build if not already set
        if not self.date_build:
            self.date_build = timezone.now()
        
         # Set date_hebergement and date_fin_hebergement if not already set
        if not self.date_hebergement:
            self.date_hebergement = timezone.now()
            self.date_fin_hebergement = self.date_hebergement + timedelta(days=360)

        
        # Check if the status is being set to '1' during modification
        if self.status == '1' and self.pk:
            # Update only when status is set to '1'
            if self.achat_website:
                self.achat_website.BuilderStatus = 'Builder'
                self.achat_website.save()

        super().save(*args, **kwargs)
        
        existing_entry = Websites_client_statu.objects.filter(website_builder=self).first()
        if existing_entry:
            # Update the existing entry
            existing_entry.cliente = self.cliente
            existing_entry.website = self.website
            existing_entry.date_created = self.date_created
            existing_entry.save()
        else:
            # Create a new instance of Websites_client_statu
            Websites_client_statu.objects.create(
                cliente=self.cliente,
                website_builder=self,
                website=self.website,
                date_created=self.date_created,
            )
        
        
        
        
        
        

class LocationWebsiteBuilder(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),
        ('1', '1'),
    ]
    STATUS_CHOICES_1 = [
        ('1', '1'),  #service actif
        ('2', '2'),  #suspendu
        ('3', '3'),  #demande de résiliation
        ('4', '4'),  #paiement en retard 
        ('5', '5'),  #en attente de suppression 
        ('6', '6'),  #Il sera supprimé après un jour 
        ('7', '7'),  #Supprimé
    ]
    # STATUS_CHOICES_2 = [ 
    #     ('0', '0'),  #non actif
    #     ('1', '1'),  #service actif
    #     ('2', '2'),  #suspendu
    #     ('3', '3'),  #résilier
    #     ('4', '4'),  #deleted 
    # ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website = models.ForeignKey(LocationWebsites, on_delete=models.CASCADE)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    db_port = models.CharField(max_length=30, null=True, blank=True)
    app_port = models.CharField(max_length=30, null=True, blank=True)
    nameWebsite = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    Statu_du_website = models.CharField(max_length=50, choices=STATUS_CHOICES_1, default='1', null=True)
    # Statu_du_website_action = models.CharField(max_length=50, choices=STATUS_CHOICES_2, default='1', null=True)
    # date_debut = models.DateTimeField(null=True, blank=True)
    # date_fin = models.DateTimeField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
  
    def __str__(self):
        return f"{self.location_website.websites.name}-{self.cliente.user.username}-{self.nameWebsite}"

    def save(self, *args, **kwargs):
        #the website field is set correctly from location_website
        if self.location_website:
            self.website = self.location_website.websites
            
        # if not self.pk:
        #     # Set date_debut to now
        #     self.date_debut = timezone.now()
        
        # Check if the status is being set to '1' during modification
        if self.status == '1' and self.pk:
            # Update only when status is set to '1'
            if self.location_website:
                self.location_website.BuilderStatus = 'Builder'
                self.location_website.save()

        super().save(*args, **kwargs)
        
         # Check if a corresponding entry already exists in Websites_client_statu
        existing_entry = Websites_client_statu.objects.filter(location_website_builder=self).first()
        if existing_entry:
            # Update the existing entry
            existing_entry.cliente = self.cliente
            existing_entry.website = self.website
            existing_entry.date_created = self.date_created
            existing_entry.save()
        else:
            # Create a new instance of Websites_client_statu
            Websites_client_statu.objects.create(
                cliente=self.cliente,
                location_website_builder=self,
                website=self.website,
                date_created=self.date_created,
            )

        
 
 
 
 
class MergedWebsiteBuilder(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website.name}-{self.cliente.user.username}"

    def save(self, *args, **kwargs):
        if self.website_builder:
            self.website = self.website_builder.website
        elif self.location_website_builder:
            self.website = self.location_website_builder.website
        elif self.getfree_website_builder:
            self.website = self.getfree_website_builder.website
        
        super().save(*args, **kwargs)

 
 
 
 
class Websites_client_statu(models.Model):
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    achat_support = models.OneToOneField(AchatSupport, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE, null=True, blank=True)
    support = models.ForeignKey(Supports, on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)


    def __str__(self):
        return f"Status for {self.cliente.user.username}"
    
    
     


def generate_facturation_code(username):
    username = username.upper() 
    random_digits = ''.join(random.choices(string.digits, k=6))
    code = f'ALT-{username}-{random_digits}'
    return code



class Facturations(models.Model):
    location_website = models.ForeignKey(LocationWebsites, on_delete=models.CASCADE, null=True, blank=True)
    achat_website = models.ForeignKey(AchatWebsites, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website = models.ForeignKey(GetFreeWebsites, on_delete=models.CASCADE, null=True, blank=True)
    achat_support = models.ForeignKey(AchatSupport, on_delete=models.CASCADE, null=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE, null=True, blank=True)
    support = models.ForeignKey(Supports, on_delete=models.CASCADE, null=True, blank=True)
    code_facturation = models.CharField(max_length=100, null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.code_facturation:
            self.code_facturation = generate_facturation_code(self.cliente.user.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code_facturation} for {self.cliente.user.username}"
    







#64
class Websites_location_payment_delay(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  # Status 0
        ('1', '1'),  # Status 1
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        username = self.cliente.user.username if self.cliente.user else 'No username'
        return f"{self.website.name}-{username}"



class Websites_location_payment_reprendre(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website.name}-{self.cliente.user.username}"
    
 
 
 
 
class Websites_Need_Delete(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.statut}-{self.cliente.user.username}"
 




class Website_need_resiliation(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website.name}-{self.cliente.user.username}"
 
 
 
 
 
 

class Website_reprendre_resiliation(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website.name}-{self.cliente.user.username}"
 
 
 
 
 
class Website_need_suspendre(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.statut}-{self.cliente.user.username}"
    
    
   
   

 
class Website_reprendre_suspendre(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.statut}-{self.cliente.user.username}"
  





class website_need_reset(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    location_website_builder = models.OneToOneField(LocationWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.statut}-{self.cliente.user.username}"
    
    



#date_hebergement
class Websites_hebergement_payment_delay(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website}-{self.cliente.user.username}"
    
    
    

class Websites_hebergement_payment_reprendre(models.Model):
    STATUS_CHOICES = [
        ('0', '0'),  #
        ('1', '1'),  #
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    website_builder = models.OneToOneField(WebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.OneToOneField(GetFreeWebsiteBuilder, on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, choices=STATUS_CHOICES, default='0', null=True)
    website = models.ForeignKey(Websites, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.website_builder.nameWebsite}-{self.cliente.user.username}"
    
    
    
    

from django.utils.crypto import get_random_string


class testing(models.Model):
    description = models.TextField(max_length=2000, null=False, blank=False)
    
    def __str__(self):
        return f"dfdfd"





from django.utils.crypto import get_random_string


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('Ouvert', 'Ouvert'),
        ('En Cours de traitement', 'En Cours de traitement'),
        ('Fermée', 'Fermée'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    description = models.TextField(max_length=2000, null=False, blank=False)
    status = models.CharField(max_length=40, choices=STATUS_CHOICES, default='Ouvert')
    typeTicket = models.CharField(max_length=40, null=False, blank=False)
    Branche = models.CharField(max_length=40, null=False, blank=False)
    code_Ticket = models.CharField(max_length=100, null=True, blank=True, unique=True)
    supportName = models.ForeignKey(Supports, on_delete=models.CASCADE, null=True, blank=True)
    websiteName = models.ForeignKey(Websites, on_delete=models.CASCADE, null=True, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    code_Demande = models.CharField(max_length=100, null=True, blank=True) 
    updated_by_ts = models.ForeignKey(SupportTechnique, on_delete=models.SET_NULL, null=True, blank=True)
    updated_by_gc = models.ForeignKey(GestionnaireComptes, on_delete=models.SET_NULL, null=True, blank=True)
    description_updated_by = models.TextField(max_length=2000, null=True, blank=True) 
    pièce_joint_updated_by  = models.ImageField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)
    pièce_joint = models.ImageField(null=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.cliente.user.username} - {self.typeTicket}"


    def save(self, *args, **kwargs):
        if not self.code_Ticket:
            self.code_Ticket = self.generate_unique_code()
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        nom_initial = self.cliente.nom[0].upper() if self.cliente.nom else ''
        prenom_initial = self.cliente.prenom[0].upper() if self.cliente.prenom else ''
        code = f'TK{nom_initial}{prenom_initial}{get_random_string(length=5)}'
        
        while Ticket.objects.filter(code_Ticket=code).exists():
            code = f'TK{nom_initial}{prenom_initial}{get_random_string(length=5)}'
        
        return code




class Conversation(models.Model):
    TICKET_TYPE_CHOICES = [
        ('Cliente', 'Cliente'),
        ('SupportTechnique', 'SupportTechnique'),
        ('GestionnaireComptes', 'GestionnaireComptes'),
    ]

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='conversations')
    sender_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    sender_id = models.PositiveIntegerField()
    message = models.TextField(max_length=2000, blank=True)
    image = models.ImageField(upload_to='conversation_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        sender = self.get_sender()
        return f"Conversation {self.id} - {self.ticket.code_Ticket} - {sender}"

    def get_sender(self):
        if self.sender_type == 'Cliente':
            return Cliente.objects.get(id=self.sender_id).user.username
        elif self.sender_type == 'SupportTechnique':
            return SupportTechnique.objects.get(id=self.sender_id).name
        elif self.sender_type == 'GestionnaireComptes':
            return GestionnaireComptes.objects.get(id=self.sender_id).name
        return None

    @property
    def sender(self):
        return self.get_sender()






class History(models.Model):
    MODEL_CHOICES = [
        ('Websites_location_payment_delay', 'Websites Location Payment Delay'),
        ('Websites_location_payment_reprendre', 'Websites Location Payment Reprendre'),
        ('Websites_Need_Delete', 'Websites Need Delete'),
        ('Website_need_resiliation', 'Website Need Resiliation'),
        ('Website_reprendre_resiliation', 'Website Reprendre Resiliation'),
        ('Website_need_suspendre', 'Website Need Suspendre'),
        ('Website_reprendre_suspendre', 'Website Reprendre Suspendre'),
        ('website_need_reset', 'Website Need Reset'),
        ('Websites_hebergement_payment_delay', 'Websites Hebergement Payment Delay'),
        ('Websites_hebergement_payment_reprendre', 'Websites Hebergement Payment Reprendre'),
    ]
    
    model_name = models.CharField(max_length=50, choices=MODEL_CHOICES)
    instance_id = models.PositiveIntegerField()
    cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE)
    website = models.ForeignKey('Websites', on_delete=models.CASCADE, null=True, blank=True)
    location_website_builder = models.ForeignKey('LocationWebsiteBuilder', on_delete=models.CASCADE, null=True, blank=True)
    getfree_website_builder = models.ForeignKey('GetFreeWebsiteBuilder', on_delete=models.CASCADE, null=True, blank=True)
    website_builder = models.ForeignKey('WebsiteBuilder', on_delete=models.CASCADE, null=True, blank=True)
    statut = models.CharField(max_length=50, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.model_name} - {self.instance_id} - {self.cliente.user.username}"
