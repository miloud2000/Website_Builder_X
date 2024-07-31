from datetime import timezone
import time
from django.core.management.base import BaseCommand
from websitebuilder.models import Website_need_suspendre,Website_reprendre_suspendre,website_need_reset

class Command(BaseCommand):
    help = 'Check actions on the websites'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def handle(self, *args, **options):
        while True:
            # Check and delete records every 30 seconds
            self.delete_records()
            # Sleep for 30 seconds
            time.sleep(30)


    def delete_records(self):
        # Query to find records where statut == '1'
        records_to_delete = Website_need_suspendre.objects.filter(statut='1')
        records_to_delete_Re = Website_reprendre_suspendre.objects.filter(statut='1')
        records_to_delete_reset = website_need_reset.objects.filter(statut='1')


        # Delete the records and get the count
        count_website_need_suspendre, _ = records_to_delete.delete()
        count_website_reprendre_suspendre, _ = records_to_delete_Re.delete()
        count_website_need_reset, _ = records_to_delete_reset.delete()

        # Log how many records were deleted
        self.stdout.write(f"Deleted {count_website_need_suspendre} records from Website_need_suspendre with statut = '1'.")
        self.stdout.write(f"Deleted {count_website_reprendre_suspendre} records from Website_reprendre_suspendre with statut = '1'.")
        self.stdout.write(f"Deleted {count_website_need_reset} records from website_need_reset with statut = '1'.")
        self.stdout.write(f"--------------------------------------------------------")