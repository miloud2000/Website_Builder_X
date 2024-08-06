import time
import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils import timezone
from websitebuilder.models import WebsiteBuilder, GetFreeWebsiteBuilder,Websites_hebergement_payment_delay,Websites_hebergement_payment_reprendre

class Command(BaseCommand): 
    help = 'Check hebergement dates and update statuses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update_count_4 = 0
        self.update_count_5 = 0

    def handle(self, *args, **options):
        while True:
            self.check_hebergement_dates()
            time.sleep(30)  # Sleep for 30 seconds (for testing purposes)


    def check_hebergement_dates(self):
        current_date = timezone.now().date()

        self.check_date_hebergement_day_after(current_date)
        self.check_date_hebergement_1_day_after(current_date)
        
        self.check_date_hebergement_free_day_after(current_date)
        self.check_date_hebergement_1_free_day_after(current_date)


        self.stdout.write(self.style.NOTICE(f'Count of Status "4" updates: {self.update_count_4}'))
        self.stdout.write(self.style.NOTICE(f'Count of Status "5" updates: {self.update_count_5}'))


    def check_date_hebergement_day_after(self, current_date):
        all_websiteBuilder = WebsiteBuilder.objects.all()

        for websiteBuilder in all_websiteBuilder:
            if websiteBuilder.date_fin_hebergement:
                date_fin_hebergement_date = websiteBuilder.date_fin_hebergement.date()
                date_difference = (current_date - date_fin_hebergement_date).days

                if date_difference < 0:
                    self.update_merged_website_status_0(websiteBuilder)




    def check_date_hebergement_1_day_after(self, current_date):
        all_websiteBuilder = WebsiteBuilder.objects.all()

        for websiteBuilder in all_websiteBuilder:
            if websiteBuilder.date_fin_hebergement:
                date_fin_hebergement_date = websiteBuilder.date_fin_hebergement.date()
                date_difference = (current_date - date_fin_hebergement_date).days

                if date_difference >= 1:
                    self.update_merged_website_status(websiteBuilder)
                    
#######################################################################################################  
                    
    #Free
    def check_date_hebergement_free_day_after(self, current_date):
        all_getfree_website_builder = GetFreeWebsiteBuilder.objects.all()

        for getfree_website_builder in all_getfree_website_builder:
            if getfree_website_builder.date_fin_hebergement:
                date_fin_hebergement_date = getfree_website_builder.date_fin_hebergement.date()
                date_difference = (current_date - date_fin_hebergement_date).days

                if date_difference < 0:
                    self.update_merged_website_free_status_0(getfree_website_builder)
                    
                    
                    
    def check_date_hebergement_1_free_day_after(self, current_date):
        all_getfree_website_builder = GetFreeWebsiteBuilder.objects.all()

        for getfree_website_builder in all_getfree_website_builder:
            if getfree_website_builder.date_fin_hebergement:
                date_fin_hebergement_date = getfree_website_builder.date_fin_hebergement.date()
                date_difference = (current_date - date_fin_hebergement_date).days

                if date_difference >= 1:
                    self.update_merged_website_free_status(getfree_website_builder)

#################################################################################################################




    def update_merged_website_status_0(self, websiteBuilder):
        if websiteBuilder.Statu_du_website not in ['1', '2', '3', '7']:  # 7 DELETE
            websiteBuilder.Statu_du_website = '1'
            websiteBuilder.save()
            self.stdout.write(self.style.SUCCESS(f'Status of {websiteBuilder} updated successfully to 1'))
            
            # Delete related Websites_hebergement_payment_delay entries
            Websites_hebergement_payment_delay.objects.filter(website_builder=websiteBuilder).delete()
            Websites_hebergement_payment_reprendre.objects.get_or_create(
                cliente=websiteBuilder.cliente,
                website_builder=websiteBuilder,
                statut='0',
                website=websiteBuilder.website
            )

        else:
            self.stdout.write(self.style.NOTICE(f'Status of {websiteBuilder} is already "1"'))



    def update_merged_website_status(self, websiteBuilder):
        if websiteBuilder.Statu_du_website != '4':
            websiteBuilder.Statu_du_website = '4'
            websiteBuilder.save()

            Websites_hebergement_payment_delay.objects.get_or_create(
                cliente=websiteBuilder.cliente,
                website_builder=websiteBuilder,
                statut='0',
                website=websiteBuilder.website
            )

            self.send_first_payment_reminder_email(websiteBuilder)
            self.stdout.write(self.style.SUCCESS(f'Status of {websiteBuilder} updated successfully to 4'))
            self.update_count_4 += 1  # Increment update count for status '4'
        else:
            self.stdout.write(self.style.NOTICE(f'Status of {websiteBuilder} is already "4"'))
            
  
##############################################################################################################          
        
    #free
    def update_merged_website_free_status_0(self, getfree_website_builder):
        if getfree_website_builder.Statu_du_website not in ['1', '2', '3', '7']:  # 7 DELETE
            getfree_website_builder.Statu_du_website = '1'
            getfree_website_builder.save()
            self.stdout.write(self.style.SUCCESS(f'Status of {getfree_website_builder} updated successfully to 1'))
            
            # Delete related Websites_hebergement_payment_delay entries
            Websites_hebergement_payment_delay.objects.filter(getfree_website_builder=getfree_website_builder).delete()

        else:
            self.stdout.write(self.style.NOTICE(f'Status of {getfree_website_builder} is already "1"'))
    
    
    
    def update_merged_website_free_status(self, getfree_website_builder):
        if getfree_website_builder.Statu_du_website != '4':
            getfree_website_builder.Statu_du_website = '4'
            getfree_website_builder.save()

            Websites_hebergement_payment_delay.objects.get_or_create(
                cliente=getfree_website_builder.cliente,
                getfree_website_builder=getfree_website_builder,
                statut='0',
                website=getfree_website_builder.website
            )

            # self.send_first_payment_reminder_email(getfree_website_builder)
            self.stdout.write(self.style.SUCCESS(f'Status of {getfree_website_builder} updated successfully to 4'))
            self.update_count_4 += 1  # Increment update count for status '4'
        else:
            self.stdout.write(self.style.NOTICE(f'Status of {getfree_website_builder} is already "4"'))
        
#################################################################################################################             





    def send_first_payment_reminder_email(self, websiteBuilder):
        cliente = websiteBuilder.cliente
        email_address = cliente.email
        subject = "Suspension de votre site web en raison d'un impayé de location"
        message = '''
        <html>
            <body>
                <p>Dear {username},</p>
                <p>J'espère que ce message vous trouve en bonne santé.</p>
                <p>C'est avec regret que nous devons vous informer de la suspension de votre service en raison d'un impayé de location.</p>
                <p>En conséquence, votre site {website_name} a été temporairement suspendu. Cela signifie que l'accès à votre site web, y compris à tous les services associés, sera indisponible tant que le solde impayé ne sera pas réglé.</p>
                <p>Nous comprenons que des circonstances imprévues ont pu conduire à cette situation, et nous sommes déterminés à vous aider à la résoudre le plus rapidement possible. Pour rétablir votre service, veuillez effectuer le paiement nécessaire dès que possible.</p>
                <p>Nous nous excusons sincèrement pour tout inconvénient que cela pourrait causer et apprécions votre attention immédiate à cette question.</p>
                <p>Nous vous remercions de votre coopération.</p>
                <p>Cordialement.</p>
            </body>
        </html>
        '''.format(username=cliente.user.username, website_name=websiteBuilder.website.name)

        # Send the email
        send_mail(subject, strip_tags(message), 'mohamedguessoum120@gmail.com', [email_address], html_message=message)
        self.stdout.write(self.style.SUCCESS(f'Email sent to {email_address}'))

