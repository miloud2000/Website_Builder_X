# utils/exports.py
from django.http import HttpResponse
import csv
from io import BytesIO
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def export_achats_excel(achats, cliente):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=achats_{cliente.user.username}.csv'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prix', 'Statut', 'Date'])
    for a in achats:
        writer.writerow([
            a.websites.name,
            a.prix_achat,
            a.BuilderStatus,
            a.date_created.strftime('%d/%m/%Y %H:%M')
        ])
    return response

def export_achats_pdf(achats, cliente):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Sites achetés – {cliente.user.username}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [['Nom', 'Prix', 'Statut', 'Date']]
    for a in achats:
        data.append([
            a.websites.name,
            f"{a.prix_achat} MAD",
            a.BuilderStatus,
            a.date_created.strftime('%d/%m/%Y %H:%M')
        ])

    table = Table(data, colWidths=[120, 80, 100, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=achats_{cliente.user.username}.pdf'
    return response



def export_tickets_excel(tickets, cliente):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=tickets_{cliente.user.username}.csv'
    writer = csv.writer(response)
    writer.writerow(['Sujet', 'Statut', 'Date'])
    for t in tickets:
        writer.writerow([
            t.description,
            t.status,
            t.date_created.strftime('%d/%m/%Y %H:%M')
        ])
    return response



def export_tickets_pdf(tickets, cliente):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Tickets – {cliente.user.username}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [['Sujet', 'Statut', 'Date']]
    for t in tickets:
        data.append([
            t.description,
            t.status,
            t.date_created.strftime('%d/%m/%Y %H:%M')
        ])

    table = Table(data, colWidths=[200, 100, 120])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=tickets_{cliente.user.username}.pdf'
    return response


def export_achat_supports_excel(achat_supports, cliente):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename=supports_{cliente.user.username}.csv'
    writer = csv.writer(response)
    writer.writerow(['Support', 'Prix', 'Statut', 'Consommation', 'Technicien', 'Date'])
    for s in achat_supports:
        writer.writerow([
            s.support.name,
            s.prix,
            s.Status,
            s.StatusConsomé,
            s.updated_by.user.username if s.updated_by else 'Non assigné',
            s.date_created.strftime('%d/%m/%Y %H:%M')
        ])
    return response

def export_achat_supports_pdf(achat_supports, cliente):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    elements.append(Paragraph(f"Supports achetés – {cliente.user.username}", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [['Support', 'Prix', 'Statut', 'Consommation', 'Technicien', 'Date']]
    for s in achat_supports:
        data.append([
            s.support.name,
            f"{s.prix} MAD",
            s.Status,
            s.StatusConsomé,
            s.updated_by.user.username if s.updated_by else 'Non assigné',
            s.date_created.strftime('%d/%m/%Y %H:%M')
        ])

    table = Table(data, colWidths=[100, 60, 80, 100, 100, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=supports_{cliente.user.username}.pdf'
    return response
