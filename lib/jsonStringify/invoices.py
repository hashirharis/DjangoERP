__author__ = 'Yussuf'
import datetime

from users.models import *
from core.models import *
from b2b.models import HeadOfficeInvoice, HeadOfficeInvoiceLine
from lib.jsonStringify.utility import decodeReceivedText
from ranges import stockranges
from brutils import shortcuts


def invoiceFromJson(HOInvoiceData, staff, merchandiserSessiom):
    #TODO: if b2b order exists under this name and isn't linked then link it up !
    try:
        HoInvoice = HeadOfficeInvoice.objects.get(pk=HOInvoiceData['id'])
    except HeadOfficeInvoice.DoesNotExist:
        HoInvoice = HeadOfficeInvoice()
        HoInvoice.createdDate = datetime.datetime.now()
    HoInvoice.distributor = Brand.objects.filter(distributor=HOInvoiceData['distributor'])[0]
    HoInvoice.type = HOInvoiceData['type']
    HoInvoice.store = Store.objects.get(pk=HOInvoiceData['store'])
    HoInvoice.invoiceNumber = decodeReceivedText(HOInvoiceData['invoiceNumber'])
    HoInvoice.invoiceDate = HOInvoiceData['invoiceDate']
    HoInvoice.dueDate = HOInvoiceData.get('dueDate', None)
    HoInvoice.orderReference = decodeReceivedText(HOInvoiceData['orderReference'])
    HoInvoice.otherInvoiceReference = decodeReceivedText(HOInvoiceData['otherInvoiceReference'])
    HoInvoice.hoComments = decodeReceivedText(HOInvoiceData['hoComments'])
    HoInvoice.storeInformation = decodeReceivedText(HOInvoiceData['storeInformation'])
    HoInvoice.extendedCredit = HOInvoiceData['extendedCredit']
    HoInvoice.freight = HOInvoiceData['freight']
    HoInvoice.invTotal = HOInvoiceData['invTotal']
    HoInvoice.invTotalExGST = HOInvoiceData['invTotalExGST']
    HoInvoice.netTotal = HOInvoiceData['netTotal']
    HoInvoice.createdBy = staff
    HoInvoice.save()
    lineNum = 0
    for line in HOInvoiceData['invoiceLines']:
        lineNum += 1
        try:
            dbLine = HeadOfficeInvoiceLine.objects.get(invoice=HoInvoice, line=lineNum)
        except HeadOfficeInvoiceLine.DoesNotExist:
            dbLine = HeadOfficeInvoiceLine()
            dbLine.invoice = HoInvoice
        dbLine.line = lineNum
        dbLine.item = Product.objects.get(pk=line['productID'])
        dbLine.invoicePrice = line['linePriceInGST']
        dbLine.quantity = line['quantity']
        dbLine.storeNet = line['unitSpanNet']
        dbLine.unitPrice = line['unitPriceExGST']
        dbLine.save()
        #update merchandiser history
        shortcuts.updateSalesHistoryPurchase(dbLine, HoInvoice.store, merchandiserSessiom)

    #delete lines that do not exist any more.
    extraLines = HeadOfficeInvoiceLine.objects.filter(invoice=HoInvoice, line__gt=lineNum)
    extraLines.delete()
    #function used by the stock ranges module to check ranged items
    stockranges.checkRangedItem(HoInvoice)
    return HoInvoice

def jsonFromInvoice(HoInvoice):
    HOInvoiceJson = {
        'id' : HoInvoice.id,
        'distributor' : HoInvoice.distributor.distributor,
        'type' : HoInvoice.type,
        'store' : HoInvoice.store.id,
        'invoiceNumber' : HoInvoice.invoiceNumber,
        'invoiceDate' : HoInvoice.invoiceDate.isoformat(),
        'orderReference' : HoInvoice.orderReference,
        'otherInvoiceReference' : HoInvoice.otherInvoiceReference,
        'hoComments' : HoInvoice.hoComments,
        'storeInformation' : HoInvoice.storeInformation,
        'extendedCredit' : HoInvoice.extendedCredit,
        'freight' : '%.2f' % HoInvoice.freight,
        'invTotal' : '%.2f' % HoInvoice.invTotal,
        'invTotalExGST' : '%.2f' % HoInvoice.invTotalExGST,
        'netTotal' : '%.2f' % HoInvoice.netTotal,
        'createdDate' : HoInvoice.createdDate.isoformat(),
        'invoiceLines' : [],
    }
    InvoiceLines = HeadOfficeInvoiceLine.objects.filter(invoice=HoInvoice)
    for InvoiceLine in InvoiceLines:
        invoiceLineJson = {
            'brandName' : InvoiceLine.item.brand.brand,
            'description' : "%s %s" %(InvoiceLine.item.model, InvoiceLine.item.description),
            'id' : InvoiceLine.item.id,
            'invActual' : '%.2f' % InvoiceLine.unitPrice,
            'quantity' : InvoiceLine.quantity,
            'modelNum' : InvoiceLine.item.model,
            'spanNet' : '%.2f' % InvoiceLine.storeNet,
        }
        HOInvoiceJson['invoiceLines'].append(invoiceLineJson)
    return HOInvoiceJson

def jsonRevertFromInvoice(HoInvoice):
    hojson = jsonFromInvoice(HoInvoice)
    hojson['id'] = 0
    if hojson['type'] == "Return of stock":
        hojson['type'] = "Purchase of stock"
    elif hojson['type'] == "Purchase of stock":
        hojson['type'] = "Return of stock"
    return hojson


