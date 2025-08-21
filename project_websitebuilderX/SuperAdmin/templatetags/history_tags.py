from django import template

register = template.Library()

ACTION_LABELS = {
    'Website_need_suspendre': 'Suspendre',
    'Website_reprendre_suspendre': 'Reprendre Suspendre',
    'website_need_reset': 'Need Reset',
    'Websites_location_payment_delay': 'Payment Location Delay',
    'Websites_location_payment_reprendre': 'Payment Location Reprendre',
    'Websites_Need_Delete': 'Need Delete',
    'Website_need_resiliation': 'Need Resiliation',
    'Website_reprendre_resiliation': 'Reprendre Resiliation',
    'Websites_hebergement_payment_delay': 'Hebergement Payment Delay',
    'Websites_hebergement_payment_reprendre': 'Hebergement Reprendre Payment Delay',
}

@register.simple_tag
def get_action_label(model_name):
    return ACTION_LABELS.get(model_name, 'Action inconnue')

@register.simple_tag
def get_website_name(history):
    website = history.website_builder or history.location_website_builder or history.getfree_website_builder
    return website.nameWebsite if website else "Aucune donnée disponible"
