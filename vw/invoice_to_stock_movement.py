__author__ = 'Adee'
from users.models import *
from b2b.models import HeadOfficeInvoice, HeadOfficeInvoiceLine
import datetime
from core.models import *
from lib.jsonStringify.utility import decodeReceivedText
from core.models import Product
from stock.models import ManualStockMovement
from vw.models import *
from stock.models import StoreInventory, StoreInventoryItemMovement, StoreInventoryItem, SalesHistory
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from b2b.views import *

"""
This function acts the same as b2b/openHOInvoice, but uses an if statement to render either
    "vw/new-invoice-stock-movement-in.html"
or
    "vw/new-invoice-stock-movement-out.html"
depending on what store is attributed to the invoice.  All VW stockIN invoices must have VW as the store attribute,
stockOUT can have any store assigned to the store attribute.
"""


# from brutils import shortcuts



@login_required()
def openVWInvoice(request, invoice_id):
    shortcuts.initialiseMerchandiserEditSession(request)
    distributors = Brand.getUniqueDistributors()
    stores = Store.objects.all()
    context = {
        'distributors': distributors,
        'stores': stores,
    }
    #existing Invoice Loading
    HoInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoice_id)
    HOInvoiceJson = jsonFromInvoice(HoInvoice)
    updatedContext = {
        'invoiceData': json.dumps(HOInvoiceJson),
        'invoice': HoInvoice,
    }
    context.update(updatedContext)
    if request.store.displayHOMenu() and request.GET.get('viewable', '') is '':
        #VW store editing an invoice
        if HoInvoice.chargedBy is None and HoInvoice.reconciledBy is None:
            if HoInvoice.store.code == "VW":
                return render(request, 'vw/new-invoice-stock-movement-in.html', context)
            else:
                return render(request, 'vw/new-invoice-stock-movement-out.html', context)
        else:
            return render(request, 'b2b/invoicing/view.html', context)
    elif request.store == HoInvoice.store:
        return render(request, 'b2b/invoicing/store-view.html', context)
    else:
        #store trying to access an invoice that isn't theirs
        return redirect('b2b:invoicesAll')

"""
This function acts the same as b2b/saveHOInvoice but points to a VW url.
It calls:
"VWinvoiceFromJson" which creates an invoice, and
"stockMovementFromJson" which initiates the stock movement
"""

@login_required()
def saveVWInvoice(request, type=0):
    movementType = type
    if ('invoiceData' in request.POST) and request.POST['invoiceData'].strip():
        HOInvoiceData = json.loads(request.POST['invoiceData'], encoding="utf-8")
        HOInvoice = VWinvoiceFromJson(HOInvoiceData, request.staff, movementType, request.session)
        stockMovementFromJson(HOInvoiceData, request.staff, HOInvoice)
        returnUrls = {
            "openInvoice" : reverse('vw:openHOInvoice', args=[HOInvoice.id]),
        }
        jsonResponse = json.dumps(returnUrls)

        return HttpResponse(jsonResponse)

"""
This function uses the HOInvoiceData from json.loads to create an Invoice obj in our db
"""

from brutils import shortcuts

def VWinvoiceFromJson(HOInvoiceData, staff, movementType, session):




    try:
        HoInvoice = HeadOfficeInvoice.objects.get(pk=HOInvoiceData['id'])
    except HeadOfficeInvoice.DoesNotExist:
        HoInvoice = HeadOfficeInvoice()
        HoInvoice.createdDate = datetime.datetime.now()
    createAndSaveInvoice(HoInvoice, HOInvoiceData, movementType, staff)
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




        store = Store.objects.get(code="VW")
        if movementType == "stockIN":
            shortcuts.updateSalesHistoryPurchase(dbLine, store, session)
        else:
            shortcuts.updateSalesHistorySalesFromVW(dbLine, store, dbLine.item, session)
    #delete lines that do not exist any more.
    extraLines = HeadOfficeInvoiceLine.objects.filter(invoice=HoInvoice, line__gt=lineNum)
    extraLines.delete()
    return HoInvoice


"""
This function is called by the above "VWinvoiceFromJson" to create an Invoice obj in our db
"""

def createAndSaveInvoice(HoInvoice, HOInvoiceData, movementType, staff):
    HoInvoice.distributor = Brand.objects.filter(distributor=HOInvoiceData['distributor'])[0]
    HoInvoice.type = HOInvoiceData['type']
    if movementType == "stockIN":
        HoInvoice.store = Store.objects.get(code='VW')
    else:
        HoInvoice.store = Store.objects.get(pk=HOInvoiceData['store'])
    invoiceNumber = decodeReceivedText(HOInvoiceData['invoiceNumber'])
    if invoiceNumber[0] == "V" and invoiceNumber[1] == "W":  #  add VW initials to start of invoice number
        HoInvoice.invoiceNumber = decodeReceivedText(HOInvoiceData['invoiceNumber'])
    else:
        HoInvoice.invoiceNumber = "VW" + decodeReceivedText(HOInvoiceData['invoiceNumber'])
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

"""
This function is called by the above "VWinvoiceFromJson" to create InvoiceLine objects in our db
"""
#
# def createAndSaveInvoiceLine(HoInvoice, lineNum, line):
#     lineNum += 1
#     try:
#         dbLine = HeadOfficeInvoiceLine.objects.get(invoice=HoInvoice, line=lineNum)
#     except HeadOfficeInvoiceLine.DoesNotExist:
#         print "DoesNotExist"
#         dbLine = HeadOfficeInvoiceLine()
#         dbLine.invoice = HoInvoice
#         print "bismila1", dbLine.invoice
#
#     finally:
#         dbLine.line = lineNum
#         dbLine.item = Product.objects.get(pk=line['productID'])
#         dbLine.invoicePrice = line['linePriceInGST']
#         dbLine.quantity = line['quantity']
#         dbLine.storeNet = line['unitSpanNet']
#         dbLine.unitPrice = line['unitPriceExGST']
#         print dbLine.line
#         print dbLine.item
#         a= dbLine.save()
#         print a,'_______ moayad'
#         item, created = HeadOfficeInvoiceLine.objects.get_or_create(line=lineNum, item= Product.objects.get(pk=line['productID']),
#                                                     invoicePrice=line['linePriceInGST'],quantity = line['quantity'], storeNet = line['unitSpanNet'],
#                                                     unitPrice = line['unitPriceExGST'], invoice=HoInvoice )
#         print 'created new item', created
#         print 'item is ', item
#         item.save()

"""
This function is called by "saveVWInvoice" to initiate a stock movement
It calls the following functions;
rollbackStoreInventoryLevels()
updateOldMovementTraces_stockOut()
updateOldMovementTraces_stockIn()
updateVWStockCounts()
"""

def stockMovementFromJson(HOInvoiceData, staff, HOInvoice):
    stockMovements = False
    invoiceNumber = HOInvoiceData['invoiceNumber']
    if not invoiceNumber[0] == "V" and not invoiceNumber[1] == "W":  #  add VW initials to start of invoice number
        invoiceNumber = "VW" + invoiceNumber
    try:
        stockMovements = LinkInvoiceToStockMovement.objects.filter(invoiceNumber=invoiceNumber)
    except LinkInvoiceToStockMovement.DoesNotExist:
        pass
    for stockMovement in stockMovements:  # rollback Store Inventory Levels
        if stockMovements:
            if not HOInvoice.store.code == "VW":
                manualStockMovementId = stockMovement.manualStockMovementId
                storeInventoryItemMovementObjects = StoreInventoryItemMovement.objects.filter(docReference=manualStockMovementId)
                if HOInvoice.store.code == "VW":
                    inventoryItems = StoreInventoryItem.objects.filter(movementIn__in=storeInventoryItemMovementObjects)
                else:
                    inventoryItems = StoreInventoryItem.objects.filter(movementOut__in=storeInventoryItemMovementObjects)
                rollbackStoreInventoryLevels(inventoryItems, HOInvoice)
            else:
                manualStockMovementId = stockMovement.manualStockMovementId
                storeInventoryItemMovementObjects = StoreInventoryItemMovement.objects.filter(docReference=manualStockMovementId)
                inventoryItems = StoreInventoryItem.objects.filter(movementIn__in=storeInventoryItemMovementObjects)
                rollbackStoreInventoryLevels(inventoryItems, HOInvoice)
    for stockMovement in stockMovements:  # update Old Movement Traces
        if stockMovement:
            manualStockMovementId = stockMovement.manualStockMovementId
            if not HOInvoice.store.code == "VW":
                updateOldMovementTraces_stockOut(manualStockMovementId, HOInvoice)
            else:
                updateOldMovementTraces_stockIn(manualStockMovementId, HOInvoice)
    updateVWStockCounts(HOInvoiceData, staff, invoiceNumber, HOInvoice)

"""
This function is called by the above "stockMovementFromJson" to adjust StoreInventory levels
"""

def rollbackStoreInventoryLevels(inventoryItems, HOInvoice):
    for inventoryItem in inventoryItems:
        storeInventoryObject = StoreInventory.objects.get(id=inventoryItem.inventory.id)
        if HOInvoice.store.code == "VW":
            storeInventoryObject.level -= 1
        else:
            storeInventoryObject.level += 1
            storeInventoryObject.available += 1
        storeInventoryObject.save()

"""
This function is called by the above "stockMovementFromJson" when a STOCKIN invoice is edited, thus the stock levels
need readjustments.  The following functions are called:
Delete the ManualStockMovement
Delete the LinkInvoiceToStockMovement
Delete the StoreInventoryItemMovement
"""

def updateOldMovementTraces_stockIn(manualStockMovementId, HOInvoice):
    movement = ManualStockMovement.objects.get(id=manualStockMovementId)
    movement.delete()
    link = LinkInvoiceToStockMovement.objects.get(manualStockMovementId=manualStockMovementId)
    link.delete()
    StoreInventoryItemMovementObjects = StoreInventoryItemMovement.objects.filter(docReference=manualStockMovementId)
    for storeInventoryItemMovementObject in StoreInventoryItemMovementObjects:
        if HOInvoice.store.code == "VW":
            storeInventoryItemMovementObject.delete()

"""
This function is called by the above "stockMovementFromJson" when a STOCKOUT invoice is edited, thus the stock levels
need readjustments.  The following functions are called:
Delete the ManualStockMovement
Delete the LinkInvoiceToStockMovement
Delete the StoreInventoryItemMovement
"""

def updateOldMovementTraces_stockOut(manualStockMovementId, HOInvoice):
    storeInventoryItemMovements = StoreInventoryItemMovement.objects.filter(docReference=manualStockMovementId)
    storeInventoryItems = StoreInventoryItem.objects.filter(movementOut__in=storeInventoryItemMovements)
    for item in storeInventoryItems:  # remove trace of movement
        item.movementOut = None
        item.save()
    movement = ManualStockMovement.objects.get(id=manualStockMovementId)
    movement.delete()
    link = LinkInvoiceToStockMovement.objects.get(manualStockMovementId=manualStockMovementId)
    link.delete()
    StoreInventoryItemMovementObjects = StoreInventoryItemMovement.objects.filter(docReference=manualStockMovementId)
    for storeInventoryItemMovementObject in StoreInventoryItemMovementObjects:
        if HOInvoice.store.code == "VW":
            storeInventoryItemMovementObject.delete()

"""
This function is called by the above "stockMovementFromJson"
It calls "product.deltaStockCounts()" from core\models.py to update stock counts

"""

def updateVWStockCounts(HOInvoiceData, staff, invoiceNumber, HOInvoice):
    for line in HOInvoiceData['invoiceLines']:
        movement = ManualStockMovement(createdBy=staff, comments="")
        movement.save()
        link = LinkInvoiceToStockMovement(manualStockMovementId=movement.id, invoiceNumber=invoiceNumber)
        link.save()
        quantity = line['quantity']
        unitPriceExGST = line['unitPriceExGST']
        product = Product.objects.get(pk=line['productID'])
        if HOInvoice.store.code == "VW":
            quantity = quantity * -1
        product.deltaStockCounts(staff.store, quantity, reference=movement,
                                 referenceType='Manual', purchaseNet=unitPriceExGST)

"""
This function deletes an invoice and its corresponding links and movements
"""

@login_required()
def deleteVWInvoice(request, pk):
    invoiceId = pk
    HoInvoice = get_object_or_404(HeadOfficeInvoice, pk=invoiceId)
    deleteInvoiceAndLines(HoInvoice, invoiceId)
    deleteLinkAndMovement(HoInvoice)
    return render(request, 'vw/dashboard.html')

"""
This function is called by the above "deleteVWInvoice" to delete the invoice and its lines
"""

def deleteInvoiceAndLines(HoInvoice, invoiceId):
    headOfficeInvoiceLines = HeadOfficeInvoiceLine.objects.filter(invoice=invoiceId)
    for headOfficeInvoiceLine in headOfficeInvoiceLines:
        itemId = headOfficeInvoiceLine.item
        quantity = headOfficeInvoiceLine.quantity
        storeInventory = StoreInventory.objects.get(product=itemId)
        if HoInvoice.store.code == "VW":  # update stock levels
            storeInventory.level -= quantity
            storeInventory.available -= quantity
        else:
            storeInventory.level += quantity
            storeInventory.available += quantity
        storeInventory.save()
    for headOfficeInvoiceLine in headOfficeInvoiceLines:  # remove invoice lines
        try:
            headOfficeInvoiceLine.delete()
        except AssertionError:
            pass
    headOfficeInvoice = HeadOfficeInvoice.objects.get(id=invoiceId)
    headOfficeInvoice.delete()

"""
This function is called by the above "deleteVWInvoice" to delete the
following models that are attached to the invoice:
ManualStockMovement
LinkInvoiceToStockMovement
StoreInventoryItem
"""

def deleteLinkAndMovement(HoInvoice):
    linkInvoiceToStockMovements = LinkInvoiceToStockMovement.objects.filter(invoiceNumber=HoInvoice.invoiceNumber)
    for linkInvoiceToStockMovementObject in linkInvoiceToStockMovements:
        temp = linkInvoiceToStockMovementObject.manualStockMovementId
        manualStockMovement = ManualStockMovement.objects.get(id=temp)
        linkInvoiceObj = linkInvoiceToStockMovementObject.manualStockMovementId
        storeInventoryItemMovements = StoreInventoryItemMovement.objects.filter(docReference=linkInvoiceObj)
        storeInventoryItems = StoreInventoryItem.objects.filter(movementOut__in=storeInventoryItemMovements)
        storeInventoryItems = storeInventoryItems.filter(movementIn__in=storeInventoryItemMovements)
        for storeInventoryItem in storeInventoryItems:  # Update movement data
            if HoInvoice.store.code == "VW":
                storeInventoryItem.delete()
            else:
                storeInventoryItem.movementOut = None
                storeInventoryItem.save()
        rollbackStoreInventoryLevels(storeInventoryItems, HoInvoice)
        if HoInvoice.store.code == "VW":
            updateOldMovementTraces_stockIn(linkInvoiceObj, HoInvoice)
        else:
            updateOldMovementTraces_stockOut(linkInvoiceObj, HoInvoice)
        linkInvoiceToStockMovementObject.delete()
        manualStockMovement.delete()


