__author__ = 'Yussuf'
import datetime

from users.models import Store
from core.models import Product, Brand
from b2b.models import StockOrder,StockOrderLine,ElectronicStockOrder
from lib.encoder import purchaseOrderPostEncoder, purchaseOrderEncoder
from lib.jsonStringify.utility import decodeDate,decodeReceivedText


def orderFromJson(orderData,staff):
    # print orderData
    store = orderData.get('currentStore') if orderData.get('orderingStore') is None else orderData.get('orderingStore') #the store this order is being placed for.
    store = Store.objects.get(pk=store)
    now = datetime.datetime.now()

    supplier = Brand.objects.get(pk=orderData['supplierID'])

    try:
        stockOrder = StockOrder.objects.get(pk=orderData['id'])
    except StockOrder.DoesNotExist:
        stockOrder = StockOrder()
        stockOrder.orderedBy = staff

    stockOrder.store = store
    stockOrder.supplier = supplier
    stockOrder.comment = decodeReceivedText(orderData['comment'])
    stockOrder.packingSlipNumber = decodeReceivedText(orderData['packingSlipNumber'])
    stockOrder.reference = decodeReceivedText(orderData['orderReference'])
    stockOrder.status = orderData['status'] #SAVED,PENDING[''],COMPLETE different pending status'
    stockOrder.type = orderData['type']
    stockOrder.is_et = orderData['is_et']
    stockOrder.orderTotalInvoiceExGST = orderData['totalInvoiceExGST']
    stockOrder.orderTotalInvoiceInGST = orderData['totalInvoiceInGST']
    stockOrder.orderTotalStoreNetInGST = orderData['storeNetInGST']
    stockOrder.save()

    line = 0
    for orderLine in orderData['orderLines']:
        line += 1
        try:
            dbOrderLine = StockOrderLine.objects.get(order=stockOrder,line=line)
        except:
            dbOrderLine = StockOrderLine(order=stockOrder,line=line)
        product = Product.objects.get(id=orderLine['productID'])
        dbOrderLine.item = product
        dbOrderLine.description = orderLine['description']
        dbOrderLine.quantity = orderLine['quantity']
        dbOrderLine.invoiceList = orderLine['originalInvoiceExGST']
        dbOrderLine.invoiceActual = orderLine['invoiceExGST']
        dbOrderLine.unitNet = orderLine['unitNetIncGST']
        dbOrderLine.lineNet = orderLine['lineNetIncGST']
        dbOrderLine.save()
        product.getStockCounts(store) #this updates the stock count as well.

    if 'et' in orderData and orderData['et'] is not None:
        electronicOrderData = orderData['et']
        encoderData = purchaseOrderPostEncoder.encodePostData(stockOrder,orderData,electronicOrderData,"T") #for testing
        RAWSendString = purchaseOrderEncoder.encodePurchaseOrder(encoderData)
        electronicStockOrder = ElectronicStockOrder(
            stockOrder = stockOrder,
            et_type = encoderData['order-type'],
            ddAddress1 = encoderData['dd-street-address-1'],
            ddAddress2 = encoderData['dd-street-address-2'],
            ddSuburb = encoderData['dd-suburb'],
            ddState = encoderData['dd-state'],
            ddPostcode = encoderData['dd-post-code'],
            ddName = encoderData['dd-name'],
            ddPhone = encoderData['dd-phone'],
            ddEmail = encoderData['dd-email'],
            promotionalReference = encoderData['promotion-deal-no-reference'],
            quotationReference = encoderData['contract-number-reference'],
            blanketOrderReference = encoderData['blanket-order-no-reference'],
            dateRequired = decodeDate(electronicOrderData['datetime-expected']),
            deliveryWindowStart = decodeDate(electronicOrderData['deliver-not-after']),
            deliveryWindowEnd =  decodeDate(electronicOrderData['deliver-not-before']),
            cancelOrderDate = decodeDate(electronicOrderData['cancel-not-after']),
            status = "PENDING",
            sentDate = now,
            sentRAW = RAWSendString,
        )
        electronicStockOrder.save()

    return stockOrder

def jsonFromOrder(order):
    orderLines = []

    #orderLine should have id,quantity,description,invoicePrice,netPrice
    #order should have id,type,orderreference,packing slip number,note,status,supplier,id

    dbOrderLines = StockOrderLine.objects.filter(order=order)
    for dbOrderLine in dbOrderLines:
        orderLine = {
            "id" : dbOrderLine.item.id,
            "quantity" :dbOrderLine.quantity,
            "description" : dbOrderLine.description,
            "invoicePrice": "%.2f" % dbOrderLine.invoiceActual,
            "invoiceOriginal": "%.2f" % dbOrderLine.invoiceList,
            "netPrice": "%.2f" % dbOrderLine.unitNet,
            "lineNet": "%.2f" % dbOrderLine.lineNet,
            }
        orderLines.append(orderLine)

    orderData = {
        "orderLines" : orderLines,
        "id" : order.id,
        "supplier" : order.supplier.id,
        "supplierHasET": order.supplier.hasElectronicTrading,
        "orderReference": order.reference,
        "status": order.status,
        "store": order.store.id,
        "note": order.comment,
        "packingSlipNumber": order.packingSlipNumber,
        "type": order.type,
        "et": order.is_et,
        "purchaser": order.purchaser(),
    }

    # print orderData
    return orderData