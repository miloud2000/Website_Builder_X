from django.contrib import admin

from .models import *

admin.site.register(Cliente),
admin.site.register(Administrateur),
admin.site.register(Websites),
admin.site.register(AchatWebsites),
admin.site.register(Supports),
admin.site.register(AchatSupport),
admin.site.register(DemandeSupport),
admin.site.register(SupportTechnique),
admin.site.register(Commercial),
admin.site.register(GestionnaireComptes),
admin.site.register(DemandeRecharger),
admin.site.register(LaTraceDemandeRecharger),
admin.site.register(WebsiteBuilder),
admin.site.register(LocationWebsites),
admin.site.register(LocationWebsiteBuilder),
admin.site.register(MergedWebsiteBuilder),
admin.site.register(Websites_client_statu),
admin.site.register(Websites_location_payment_delay),
admin.site.register(Websites_location_payment_reprendre),
admin.site.register(Websites_Need_Delete),
admin.site.register(Website_need_resiliation),
admin.site.register(Website_reprendre_resiliation),
admin.site.register(Website_need_suspendre),
admin.site.register(Website_reprendre_suspendre),
admin.site.register(website_need_reset),
admin.site.register(Websites_hebergement_payment_delay),
admin.site.register(Websites_hebergement_payment_reprendre),
admin.site.register(GetFreeWebsites),
admin.site.register(GetFreeWebsiteBuilder),
admin.site.register(Facturations),
admin.site.register(Ticket),
admin.site.register(Conversation),


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'instance_id', 'cliente', 'website', 'date_created', 'statut')
    list_filter = ('model_name', 'date_created')
    search_fields = ('model_name', 'cliente__user__username')




















