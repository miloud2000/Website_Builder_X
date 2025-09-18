def filter_demandes(request, cliente):
    from websitebuilder.models import DemandeRecharger
    status = request.GET.get('demande_status')
    date_min = request.GET.get('demande_date_min')
    date_max = request.GET.get('demande_date_max')
    export = request.GET.get('demande_export')

    qs = DemandeRecharger.objects.filter(cliente=cliente)
    if status:
        qs = qs.filter(status=status)
    if date_min:
        qs = qs.filter(date_created__gte=date_min)
    if date_max:
        qs = qs.filter(date_created__lte=date_max)
    return qs.order_by('-date_created'), export


def filter_achats(request, cliente):
    from websitebuilder.models import AchatWebsites
    status = request.GET.get('achat_status')
    date_min = request.GET.get('achat_date_min')
    date_max = request.GET.get('achat_date_max')
    export = request.GET.get('achat_export')

    qs = AchatWebsites.objects.filter(cliente=cliente)
    if status:
        qs = qs.filter(BuilderStatus=status)
    if date_min:
        qs = qs.filter(date_created__gte=date_min)
    if date_max:
        qs = qs.filter(date_created__lte=date_max)
    return qs.order_by('-date_created'), export


def filter_tickets(request, cliente):
    from websitebuilder.models import Ticket
    status = request.GET.get('ticket_status')
    date_min = request.GET.get('ticket_date_min')
    date_max = request.GET.get('ticket_date_max')
    export = request.GET.get('ticket_export')

    qs = Ticket.objects.filter(cliente=cliente)
    if status:
        qs = qs.filter(status=status)
    if date_min:
        qs = qs.filter(date_created__gte=date_min)
    if date_max:
        qs = qs.filter(date_created__lte=date_max)
    return qs.order_by('-date_created'), export




def filter_achat_supports(request, cliente):
    from websitebuilder.models import AchatSupport
    status = request.GET.get('support_status')
    conso = request.GET.get('support_conso')
    export = request.GET.get('support_export')

    qs = AchatSupport.objects.filter(cliente=cliente)
    if status:
        qs = qs.filter(Status=status)
    if conso:
        qs = qs.filter(StatusConsomé=conso)
    return qs.order_by('-date_created'), export
