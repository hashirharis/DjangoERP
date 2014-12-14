__author__ = 'Adee'
from b2b.models import B2BInvoice, B2BInvoiceLine

def jsonFromB2BInvoice(invoice):
    invoiceLines = []
    #orderLine should have id,quantity,description,invoicePrice,netPrice
    #invoice should have distributor, store, invoiceNumber, invoiceDate, orderNumber
    dbinvoiceLines = B2BInvoiceLine.objects.filter(invoice=invoice)

    for InvoiceLine in dbinvoiceLines:
        invoiceLineJson = {
            'brandName': InvoiceLine.item.brand.brand,
            'description': "%s %s" % (InvoiceLine.item.model, InvoiceLine.item.description),
            'id': InvoiceLine.item.id,
            'invActual': '%.2f' % InvoiceLine.unitPrice,
            'quantity': InvoiceLine.quantity,
            'modelNum': InvoiceLine.item.model,#TODO:get the most accurate spannet price.
            'spanNet': '%.2f' % InvoiceLine.item.spanNet
        }
        invoiceLines.append(invoiceLineJson)

    HOInvoiceJson = {
        'distributor': invoice.distributor.distributor,
        'store': invoice.store.id,
        'invoiceNumber': invoice.invoiceNumber,
        'invoiceDate': invoice.invoiceDate.isoformat(),
        'orderReference': invoice.orderNumber,
        'invoiceLines': invoiceLines,
    }

    # print HOInvoiceJson
    return HOInvoiceJson