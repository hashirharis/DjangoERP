__author__ = 'Yussuf'
from b2b.models import *

def reconFromJson(data, staff):
    recon = Recon()
    recon.startDate = data['endDate']
    recon.endDate = data['endDate']
    recon.statementTotal = data['statementTotal']
    recon.status = data['status']
    recon.distributor = Brand.objects.filter(distributor=data['distributor'])[0]
    recon.createdBy = staff
    recon.save()
    for line in data['reconLines']:
        invoiceToUpdate = HeadOfficeInvoice.objects.get(pk=line['id'])
        reconLine = ReconLines()
        reconLine.recon = recon
        reconLine.invoice = invoiceToUpdate
        reconLine.selected = line['selected']
        reconLine.comment = line['comment']
        reconLine.save()
        invoiceToUpdate.reconciledBy = staff
        invoiceToUpdate.reconciledDate = datetime.datetime.now()
        invoiceToUpdate.save()