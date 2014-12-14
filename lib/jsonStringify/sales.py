__author__ = 'Yussuf'
from decimal import Decimal as D

from django.core.urlresolvers import reverse
from django.utils import timezone

from core.models import Product
from pos.models import Sale, Customer, SalesLine, SalesPayment, PaymentMethod, SaleInvoiceLine, SaleInvoice
from lib.jsonStringify.utility import decodeReceivedText
from brutils import shortcuts

def saleFromJson(salesData, terminal, staff):
    '''
        the json object passed to this method is already converted using json.dumps
        it is the 'salesData' object
    '''
    walkInCustomerID = 4
    now = timezone.now()
    store = terminal.store
    newSale = False
    # print salesData

    try:
        customer = Customer.objects.get(pk=salesData['customerID'])
    except Customer.DoesNotExist: # customer not attached to sale.
        customer = Customer.objects.get(pk=walkInCustomerID)
    try:
        sale = Sale.objects.get(pk=salesData['id'])
    except Sale.DoesNotExist:
        sale = Sale(
            customer=customer,
            purchaseDate=now,
            salesPerson=staff,
            code="1",
        )
        newSale = True
    sale.total = salesData['salesTotalInGST']
    sale.customer = customer
    sale.deliveryAddress = salesData['deliveryAddress']
    sale.status = salesData['status']
    sale.storeNote = decodeReceivedText(salesData['storeNote'])
    sale.note = decodeReceivedText(salesData['saleNote'])
    sale.terminal = terminal
    if sale.status == "COMPLETED":
        sale.fullPaymentDate = now
    sale.save()
    if newSale:
        sale.code = Sale.generateSaleNumber(terminal, store, sale.id)
        sale.save()
    #salesLines
    line = 0
    for salesLine in salesData['salesLines']:
        line += 1
        try:
            dbSalesLine = SalesLine.objects.get(sale=sale, line=line)
        except SalesLine.DoesNotExist:
            dbSalesLine = SalesLine(sale=sale, line=line)
        product = Product.objects.get(pk=salesLine['productID'])
        dbSalesLine.quantity = salesLine['quantity']
        dbSalesLine.released = salesLine['released'] + salesLine['toRelease']
        dbSalesLine.unitPrice = salesLine['unitPrice']
        dbSalesLine.price = salesLine['totalPrice']
        dbSalesLine.item = product
        dbSalesLine.description = salesLine['description']
        dbSalesLine.warrantyRef = salesLine['warrantyRef']
        dbSalesLine.modelNum = salesLine['modelNum']
        dbSalesLine.save()
        #stock count with serials
        #serials = salesLine['barcodes'].strip().split(',')
        product.deltaStockCounts(store, salesLine['toRelease'], reference=sale, referenceType="Sale")
        shortcuts.updateSalesHistorySales(salesLine, store, dbSalesLine.item)
    #delete lines that do not exist any more.
    extraLines = SalesLine.objects.filter(sale=sale, line__gt=line)
    extraLines.delete()
    #
    groupedBy = salesData["paymentsGrouping"]
    for payment in salesData['paymentLines']:
        amount = payment['amount']
        paymentMethod = PaymentMethod.objects.get(pk=payment['method_id'])
        try: #check if payment has already been entered.
            dbSalesPayment = SalesPayment.objects.get(sale=sale, paymentMethod=paymentMethod, amount=amount)
        except SalesPayment.DoesNotExist: #create payments for the new entries.
            newSalesPayment = SalesPayment(sale=sale, amount=amount, date=now, paymentMethod=paymentMethod, receivedBy=staff, groupedBy=groupedBy)
            newSalesPayment.save()
            groupedBy += 1
    if len(salesData['newInvoiceLines']) > 0:
        invoiceReference = SaleInvoice.generateInvoiceNumber(terminal, store, sale.id, sale.getMostRecentInvoice()+1)
        total = D('0.00')
        invoice = SaleInvoice(sale=sale, reference=invoiceReference, total=total, salesPerson=staff)
        invoice.note = decodeReceivedText(salesData['saleNote'])
        invoice.save()
        for invoiceLine in salesData['newInvoiceLines']:
            retrievedLine = SalesLine.objects.get(sale=sale, line=invoiceLine['line'])
            dbInvoiceLine = SaleInvoiceLine(
                invoice=invoice,
                salesLine=retrievedLine,
                quantity=invoiceLine['quantity'],
                unitPrice=invoiceLine['unitPrice'],
                price=invoiceLine['totalPrice']
            )
            dbInvoiceLine.save()
            total += D(invoiceLine['totalPrice'])
        invoice.total = total
        invoice.save()
    return sale

def jsonFromSale(sale):
    '''
        returns object to later be loaded using json.loads
    '''
    salesData = {}
    #customer
    customer = sale.customer
    customerInformation = {
        "id" : customer.id,
        "name" : customer.firstName + " " + customer.lastName,
        "htmlAddress" : sale.deliveryAddress if sale.id is not None else customer.htmlFormattedAddress(),
        "firstContact" : customer.firstContactPoint(),
        "creditLimit": "%.2f" % customer.account.remainingCreditLimit(),
    }
    #salesLines
    salesLines = []
    line = 0
    dbSalesLines = SalesLine.objects.filter(sale=sale)
    for dbSalesLine in dbSalesLines:
        line += 1
        salesLine = {
            "line" : line,
            "productID" : dbSalesLine.item.id,
            "modelNum": dbSalesLine.modelNum,
            "description" : dbSalesLine.description,
            "warrantyRef" : dbSalesLine.warrantyRef,
            "unitCostPrice": "%.2f" % dbSalesLine.item.costPrice,
            "lineCostPrice": "%.2f" % (dbSalesLine.item.costPrice*dbSalesLine.quantity),
            "quantity" : dbSalesLine.quantity,
            "released" : dbSalesLine.released,
            "unitPrice": "%.2f" % dbSalesLine.unitPrice,
            "totalPrice": "%.2f" % dbSalesLine.price,
        }
        salesLines.append(salesLine)
    #payments
    payments = []
    salesPayments = SalesPayment.objects.filter(sale=sale)
    for salesPayment in salesPayments:
        payment = {
            "method_name" : salesPayment.paymentMethod.name,
            "method_id" : salesPayment.paymentMethod.id,
            "amount" : "%.2f" % salesPayment.amount,
            "paymentDate" : salesPayment.date.isoformat(),
            "group" : salesPayment.groupedBy,
            "printURL" : reverse("pos:printPaymentReceipt", args=[sale.id, salesPayment.groupedBy])
        }
        payments.append(payment)
    paymentsGroupedBy = sale.getMostRecentGroupedBy() + 1
    invoices = []
    salesInvoices = SaleInvoice.objects.filter(sale=sale)
    for salesInvoice in salesInvoices:
        invoice = {
            "reference": salesInvoice.reference,
            "salesPerson": salesInvoice.salesPerson.name,
            "total": "%.2f" % salesInvoice.total,
            "created": salesInvoice.created.isoformat(),
            "printURL": reverse("pos:printTaxInvoice", args=[salesInvoice.id]),
        }
        invoices.append(invoice)
    #all together
    salesData = {
        'id': sale.id,
        "status": sale.status,
        "paymentsGrouping": paymentsGroupedBy,
        "storeNote": sale.storeNote,
        "saleNote": sale.note,
        "customer": customerInformation,
        "salesLines": salesLines,
        "paymentLines": payments,
        "invoiceLines": invoices,
    }
    return salesData









