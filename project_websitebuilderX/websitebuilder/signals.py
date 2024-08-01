from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Websites_location_payment_delay,
    Websites_location_payment_reprendre,
    Websites_Need_Delete,
    Website_need_resiliation,
    Website_reprendre_resiliation,
    Website_need_suspendre,
    Website_reprendre_suspendre,
    website_need_reset,
    Websites_hebergement_payment_delay,
    Websites_hebergement_payment_reprendre,
    History
)

def create_history_entry(instance, model_name):
    History.objects.create(
        model_name=model_name,
        instance_id=instance.id,
        cliente=instance.cliente,
        website=instance.website if hasattr(instance, 'website') else None,
        location_website_builder=instance.location_website_builder if hasattr(instance, 'location_website_builder') else None,
        getfree_website_builder=instance.getfree_website_builder if hasattr(instance, 'getfree_website_builder') else None,
        website_builder=instance.website_builder if hasattr(instance, 'website_builder') else None,
        statut=instance.statut
    )


@receiver(post_save, sender=Websites_location_payment_delay)
def save_websites_location_payment_delay_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Websites_location_payment_delay')

@receiver(post_save, sender=Websites_location_payment_reprendre)
def save_websites_location_payment_reprendre_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Websites_location_payment_reprendre')

@receiver(post_save, sender=Websites_Need_Delete)
def save_websites_need_delete_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Websites_Need_Delete')

@receiver(post_save, sender=Website_need_resiliation)
def save_website_need_resiliation_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Website_need_resiliation')

@receiver(post_save, sender=Website_reprendre_resiliation)
def save_website_reprendre_resiliation_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Website_reprendre_resiliation')

@receiver(post_save, sender=Website_need_suspendre)
def save_website_need_suspendre_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Website_need_suspendre')

@receiver(post_save, sender=Website_reprendre_suspendre)
def save_website_reprendre_suspendre_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Website_reprendre_suspendre')

@receiver(post_save, sender=website_need_reset)
def save_website_need_reset_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'website_need_reset')

@receiver(post_save, sender=Websites_hebergement_payment_delay)
def save_websites_hebergement_payment_delay_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Websites_hebergement_payment_delay')

@receiver(post_save, sender=Websites_hebergement_payment_reprendre)
def save_websites_hebergement_payment_reprendre_to_history(sender, instance, **kwargs):
    create_history_entry(instance, 'Websites_hebergement_payment_reprendre')
