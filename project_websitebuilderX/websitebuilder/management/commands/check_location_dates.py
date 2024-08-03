import time
import pickle
import os
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.utils import timezone
from websitebuilder.models import LocationWebsiteBuilder, LocationWebsites,Websites_location_payment_delay,Websites_Need_Delete,Websites_location_payment_reprendre

class Command(BaseCommand): 
    help = 'Check location dates and update statuses'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.sent_first_reminders_file = 'sent_first_reminders.pkl'  # File to store the last email sent dates for first reminders
        # self.sent_second_reminders_file = 'sent_second_reminders.pkl'  # File to store the last email sent dates for second reminders
        # self.sent_first_reminders = self.load_sent_emails(self.sent_first_reminders_file)
        # self.sent_second_reminders = self.load_sent_emails(self.sent_second_reminders_file)
        self.update_count_4 = self.load_update_count('update_count_4')  # Load update count for status '4'
        self.update_count_5 = self.load_update_count('update_count_5')  # Load update count for status '5')

    # def load_sent_emails(self, file):
    #     if os.path.exists(file):
    #         with open(file, 'rb') as f:
    #             return pickle.load(f)
    #     else:
    #         return {}


    def load_update_count(self, count_type):
        count_file = f'{count_type}.pkl'
        if os.path.exists(count_file):
            try:
                with open(count_file, 'rb') as f:
                    return pickle.load(f)
            except (pickle.UnpicklingError, EOFError, IOError) as e:
                self.stdout.write(self.style.ERROR(f'Error loading pickle file: {e}'))
                return 0
        else:
            return 0


    # def save_sent_emails(self, data, file):
    #     with open(file, 'wb') as f:
    #         pickle.dump(data, f)


    def save_update_count(self, count, count_type):
        count_file = f'{count_type}.pkl'
        with open(count_file, 'wb') as f:
            pickle.dump(count, f)


    def handle(self, *args, **options):
        while True:
            self.check_location_dates()
            # self.save_sent_emails(self.sent_first_reminders, self.sent_first_reminders_file)  
            # self.save_sent_emails(self.sent_second_reminders, self.sent_second_reminders_file) 
            self.save_update_count(self.update_count_4, 'update_count_4')  
            self.save_update_count(self.update_count_5, 'update_count_5') 
            time.sleep(30) 


    def check_location_dates(self):
        current_date = timezone.now().date()

        self.check_location_dates_day_after(current_date)
        self.check_location_dates_1_day_after(current_date)
        self.check_location_dates_15_days_after(current_date)
        self.check_location_dates_29_day_after(current_date)
        self.check_location_dates_30_day_after(current_date)



        self.stdout.write(self.style.NOTICE(f'Count of Status "4" updates: {self.update_count_4}'))
        self.stdout.write(self.style.NOTICE(f'Count of Status "5" updates: {self.update_count_5}'))


    def check_location_dates_day_after(self, current_date):
        all_locations = LocationWebsites.objects.all()

        for location in all_locations:
            if location.date_fin:
                date_fin_date = location.date_fin.date()
                date_difference = (current_date - date_fin_date).days

                if date_difference < 0:
                    self.update_merged_website_status_0(location)



    def check_location_dates_1_day_after(self, current_date):
        all_locations = LocationWebsites.objects.all()

        for location in all_locations:
            if location.date_fin:
                date_fin_date = location.date_fin.date()
                date_difference = (current_date - date_fin_date).days

                if date_difference == 1:
                    self.update_merged_website_status(location)




    def check_location_dates_15_days_after(self, current_date):
        all_locations = LocationWebsites.objects.all()

        for location in all_locations:
            if location.date_fin:
                date_fin_date = location.date_fin.date()
                date_difference = (current_date - date_fin_date).days

                if date_difference == 15:
                    self.update_merged_website_status_15(location)
                    
                    
                    
    
    def check_location_dates_29_day_after(self, current_date):
        all_locations = LocationWebsites.objects.all()

        for location in all_locations:
            if location.date_fin:
                date_fin_date = location.date_fin.date()
                date_difference = (current_date - date_fin_date).days

                if date_difference == 29:
                    self.update_merged_website_status_29(location)
                # if date_difference <= 29:
                #     self.update_merged_website_status_29(location)




    def check_location_dates_30_day_after(self, current_date):
        all_locations = LocationWebsites.objects.all()

        for location in all_locations:
            if location.date_fin:
                date_fin_date = location.date_fin.date()
                date_difference = (current_date - date_fin_date).days

                if date_difference >= 30:
                    self.update_merged_website_status_30(location)



    def update_merged_website_status_0(self, location):
        location_website_builder = LocationWebsiteBuilder.objects.filter(location_website=location).first()
        if location_website_builder:
            if location_website_builder.Statu_du_website not in ['1', '2', '3', '7']: #7 DELETE 
                location_website_builder.Statu_du_website = '1'
                location_website_builder.save()
                self.stdout.write(self.style.SUCCESS(f'Status of {location_website_builder} updated successfully to 1'))
                
                # Delete Websites_Need_Delete
                websites_need_delete_entry = Websites_Need_Delete.objects.filter(location_website_builder=location_website_builder).first()
                if websites_need_delete_entry:
                    websites_need_delete_entry.delete()
                    self.stdout.write(self.style.SUCCESS(f'Corresponding entry from Websites_Need_Delete deleted successfully'))
                else:
                    self.stdout.write(self.style.NOTICE(f'No corresponding entry in Websites_Need_Delete found for location: {location}'))
                    
                # Delete Websites_location_payment_delay
                websites_location_payment_delay_entry = Websites_location_payment_delay.objects.filter(location_website_builder=location_website_builder).first()
                if websites_location_payment_delay_entry:
                    # Add an entry to Websites_location_payment_reprendre
                    Websites_location_payment_reprendre.objects.create(
                        cliente=websites_location_payment_delay_entry.cliente,
                        location_website_builder=location_website_builder,
                        statut='0',  # Adjust the status as needed
                        website=websites_location_payment_delay_entry.website
                    )
                    websites_location_payment_delay_entry.delete()
                    self.stdout.write(self.style.SUCCESS(f'Corresponding entry from Websites_location_payment_delay deleted and moved to Websites_location_payment_reprendre successfully'))
                else:
                    self.stdout.write(self.style.NOTICE(f'No corresponding entry in Websites_location_payment_delay found for location: {location}'))
                    
            else:
                self.stdout.write(self.style.NOTICE(f'Status of {location_website_builder} is already "1"'))
        else:
            self.stdout.write(self.style.ERROR(f'No LocationWebsiteBuilder found for location: {location}'))




    def update_merged_website_status(self, location):
        location_website_builder = LocationWebsiteBuilder.objects.filter(location_website=location).first()
        if location_website_builder:
            if location_website_builder.Statu_du_website != '4':
                location_website_builder.Statu_du_website = '4'
                location_website_builder.save()
                cliente = location_website_builder.cliente

                # Create an instance of Websites_location_payment_delay
                payment_delay_instance, created = Websites_location_payment_delay.objects.get_or_create(
                    cliente=cliente,
                    location_website_builder=location_website_builder,
                    statut='0',
                    website=location_website_builder.website  
                )

                self.send_first_payment_reminder_email(location)
                self.stdout.write(self.style.SUCCESS(f'Status of {location_website_builder} updated successfully to 4'))
                self.update_count_4 += 1  
            else:
                self.stdout.write(self.style.NOTICE(f'Status of {location_website_builder} is already "4"'))
        else:
            self.stdout.write(self.style.ERROR(f'No LocationWebsiteBuilder found for location: {location}'))
 
    
    
    
    

    def update_merged_website_status_15(self, location):
        location_website_builder = LocationWebsiteBuilder.objects.filter(location_website=location).first()
        if location_website_builder:
            if location_website_builder.Statu_du_website != '5':
                location_website_builder.Statu_du_website = '5'
                location_website_builder.save()
                
                self.send_second_payment_reminder_email(location)
                self.stdout.write(self.style.SUCCESS(f'Status of {location_website_builder} updated successfully to 5'))
                self.update_count_5 += 1  
            else:
                self.stdout.write(self.style.NOTICE(f'Status of {location_website_builder} is already "5"'))
        else:
            self.stdout.write(self.style.ERROR(f'No LocationWebsiteBuilder found for location: {location}'))



        
    def update_merged_website_status_29(self, location):
        location_website_builder = LocationWebsiteBuilder.objects.filter(location_website=location).first()
        if location_website_builder:
            if location_website_builder.Statu_du_website != '6':
                location_website_builder.Statu_du_website = '6'
                location_website_builder.save()
                
                cliente = location_website_builder.cliente

                # Create an instance of Websites_location_payment_delay
                payment_delay_instance, created = Websites_location_payment_delay.objects.get_or_create(
                    cliente=cliente,
                    location_website_builder=location_website_builder,
                    statut='0',
                    website=location_website_builder.website  
                )

                self.send_payment_reminder_email_29(location)
                self.stdout.write(self.style.SUCCESS(f'Status of {location_website_builder} updated successfully to 6 '))
                self.update_count_5 += 1  
            else:
                self.stdout.write(self.style.NOTICE(f'Status of {location_website_builder} is already "5"'))
        else:
            self.stdout.write(self.style.ERROR(f'No LocationWebsiteBuilder found for location: {location}'))

    


    def update_merged_website_status_30(self, location):
        location_website_builder = LocationWebsiteBuilder.objects.filter(location_website=location).first()
        if location_website_builder:
            if location_website_builder.Statu_du_website != '7':
                location_website_builder.Statu_du_website = '7'
                location_website_builder.save()

                cliente = location_website_builder.cliente

                # Create an instance of Websites_Need_Delete
                need_delete_instance, created = Websites_Need_Delete.objects.get_or_create(
                    cliente=location_website_builder.cliente,
                    location_website_builder=location_website_builder,
                    statut='0',
                )

                self.send_payment_reminder_email_30(location)
                self.stdout.write(self.style.SUCCESS(f'Status of {location_website_builder} updated successfully to 7'))
                self.update_count_5 += 1  
            else:
                self.stdout.write(self.style.NOTICE(f'Status of {location_website_builder} is already "7"'))
        else:
            self.stdout.write(self.style.ERROR(f'No LocationWebsiteBuilder found for location: {location}'))




    def send_first_payment_reminder_email(self, location):
        cliente = location.cliente
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
        '''.format(username=cliente.user.username, website_name=location.websites.name)

        # Send the email
        send_mail(subject, strip_tags(message), 'mohamedguessoum120@gmail.com', [email_address], html_message=message)
        self.stdout.write(self.style.SUCCESS(f'Email sent to {email_address}'))




    def send_second_payment_reminder_email(self, location):
        cliente = location.cliente
        email_address = cliente.email
        subject = 'Notification : Suppression Définitive de Votre Service dans 15 Jours'
        message = '''
            <html>
                <body>
                    <p>Dear {username},</p>
                    <p>J'espère que ce message vous trouve bien.</p>
                    <p>It is with regret that we must inform you of the suspension of your service due to an unpaid location fee.</p>
                    <p>As a result, your site {website_name} has been temporarily suspended. This means that access to your website, including all associated services, will be unavailable until the outstanding balance is settled.</p>
                    <p>We understand that unforeseen circumstances may have led to this situation, and we are committed to helping you resolve it as soon as possible. To restore your service, please make the necessary payment as soon as possible.</p>
                    <p>For further assistance or to discuss payment options, please contact our billing department immediately at [Contact Details].</p>
                    <p>We sincerely apologize for any inconvenience this may cause and appreciate your immediate attention to this matter.</p>
                    <p>Thank you for your cooperation.</p>
                    <p>Regards,</p>
                </body>
            </html>
        '''.format(username=cliente.user.username, website_name=location.websites.name)

        # Send the email
        send_mail(subject, strip_tags(message), 'mohamedguessoum120@gmail.com', [email_address], html_message=message)
        self.stdout.write(self.style.SUCCESS(f'Email sent to {email_address}'))




    def send_payment_reminder_email_29(self, location):
        cliente = location.cliente
        email_address = cliente.email
        subject = 'Notification : Suppression Définitive de Votre Service dans 1 Jours'
        message = '''
            <html>
                <body>
                    <p>Dear {username},</p>
                    <p>J'espère que ce message vous trouve bien.</p>
                    <p>It is with regret that we must inform you of the suspension of your service due to an unpaid location fee.</p>
                    <p>As a result, your site {website_name} has been temporarily suspended. This means that access to your website, including all associated services, will be unavailable until the outstanding balance is settled.</p>
                    <p>We understand that unforeseen circumstances may have led to this situation, and we are committed to helping you resolve it as soon as possible. To restore your service, please make the necessary payment as soon as possible.</p>
                    <p>For further assistance or to discuss payment options, please contact our billing department immediately at [Contact Details].</p>
                    <p>We sincerely apologize for any inconvenience this may cause and appreciate your immediate attention to this matter.</p>
                    <p>Thank you for your cooperation.</p>
                    <p>Regards,</p>
                </body>
            </html>
        '''.format(username=cliente.user.username, website_name=location.websites.name)

        # Send the email
        send_mail(subject, strip_tags(message), 'mohamedguessoum120@gmail.com', [email_address], html_message=message)
        self.stdout.write(self.style.SUCCESS(f'Email sent to {email_address}'))



    def send_payment_reminder_email_30(self, location):
            cliente = location.cliente
            email_address = cliente.email
            subject = 'Notification : suppression du contenaire définitivement '
            message = '''
                <html>
                    <body>
                        <p>Dear {username},</p>
                        <p>J'espère que ce message vous trouve bien.</p>
                        <p>It is with regret that we must inform you of the suspension of your service due to an unpaid location fee.</p>
                        <p>As a result, your site {website_name} has been temporarily suspended. This means that access to your website, including all associated services, will be unavailable until the outstanding balance is settled.</p>
                        <p>We understand that unforeseen circumstances may have led to this situation, and we are committed to helping you resolve it as soon as possible. To restore your service, please make the necessary payment as soon as possible.</p>
                        <p>For further assistance or to discuss payment options, please contact our billing department immediately at [Contact Details].</p>
                        <p>We sincerely apologize for any inconvenience this may cause and appreciate your immediate attention to this matter.</p>
                        <p>Thank you for your cooperation.</p>
                        <p>Regards,</p>
                    </body>
                </html>
            '''.format(username=cliente.user.username, website_name=location.websites.name)

            # Send the email
            send_mail(subject, strip_tags(message), 'mohamedguessoum120@gmail.com', [email_address], html_message=message)
            self.stdout.write(self.style.SUCCESS(f'Email sent to {email_address}'))