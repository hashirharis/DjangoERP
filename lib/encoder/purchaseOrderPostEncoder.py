__author__ = 'Yussuf'
from datetime import datetime

from b2b.models import StockOrderLine
from lib.jsonStringify.utility import decodeDate, decodeReceivedText


def encodePostData(orderObject,orderDict,etDict,TorP="P"):
    '''
    required ET data as below:

    EncodedOrder = {
        "et_type" :,
        "tp_flag" :, //(optional)
        "quote-ref":,
        "bo-ref",
        "promo-ref",
        "dd-name",
        "dd-street-address-1",
        "dd-street-address-2",
        "dd-suburb",
        "dd-state",
        "dd-post-code",
        "dd-country",
        "dd-contact-name",
        "dd-email",
        "dd-phone",

        "datetime-expected" :,
        "cancel-not-after" :,
        "delivery-not-before":,
        "delivery-not-after":,
        "ETInstructions":,
    };
    '''


    HOGLN="9377779071717" #headofficeGLN
    if etDict.get('tp-flag') is not None:
        TPFlag = etDict['tp-flag']
    else:
        TPFlag = TorP

    encoderData = {}
    encoderData['record-identifier'] = "EAPO"
    encoderData['transaction-set'] = "ORDERS"
    encoderData['order-type'] = etDict['et_type']
    encoderData['order-number'] = orderObject.reference
    encoderData['message-function'] = 9
    encoderData['test-production-flag'] = TPFlag
    encoderData['receiver-identifier'] = orderObject.supplier.GLN
    encoderData['sender-identifier'] = HOGLN
    encoderData['order-datetime'] =  datetime.now().strftime("%Y%m%d%H%M")
    encoderData['shipment-request'] = ""
    encoderData['datetime-expected'] = decodeDate(etDict['datetime-expected']).strftime("%Y%m%d")
    encoderData['cancel-not-after'] = decodeDate(etDict['cancel-not-after']).strftime("%Y%m%d")
    encoderData['deliver-not-before'] = decodeDate(etDict['deliver-not-before']).strftime("%Y%m%d")
    encoderData['deliver-not-after'] = decodeDate(etDict['deliver-not-after']).strftime("%Y%m%d")
    encoderData['contract-number-reference'] =  decodeReceivedText(etDict['quote-ref'])
    encoderData['blanket-order-no-reference'] = decodeReceivedText(etDict['bo-ref'])
    encoderData['promotion-deal-no-reference'] = decodeReceivedText(etDict['promo-ref'])
    encoderData['sales-dept-no-reference'] = ""
    encoderData['purchaser'] = HOGLN
    encoderData['supplier'] = orderObject.supplier.GLN
    encoderData['suppliers-name'] = orderObject.supplier.distributor
    encoderData['purchaser-ship-to-code'] = orderObject.store.GLN
    encoderData['purchaser-ship-to-name'] = orderObject.store.name


    if etDict['radioDD']:
        encoderData['dd-name'] = decodeReceivedText(etDict['dd-name'])
        encoderData['dd-street-address-1'] = decodeReceivedText(etDict['dd-street-address-1'])
        encoderData['dd-street-address-2'] = decodeReceivedText(etDict['dd-street-address-2'])
        encoderData['dd-suburb'] = decodeReceivedText(etDict['dd-suburb'])
        encoderData['dd-state'] = decodeReceivedText(etDict['dd-state'])
        encoderData['dd-post-code'] = decodeReceivedText(etDict['dd-post-code'])
        encoderData['dd-country'] = ""
        encoderData['dd-contact-name'] = decodeReceivedText(etDict['dd-contact-name'])
        encoderData['dd-email'] = decodeReceivedText(etDict['dd-email'])
        encoderData['dd-phone'] = decodeReceivedText(etDict['dd-phone'])
    else:
        encoderData['dd-name'] = ""
        encoderData['dd-street-address-1'] = ""
        encoderData['dd-street-address-2'] = ""
        encoderData['dd-suburb'] = ""
        encoderData['dd-state'] = ""
        encoderData['dd-post-code'] = ""
        encoderData['dd-country'] = ""
        encoderData['dd-contact-name'] = ""
        encoderData['dd-email'] = ""
        encoderData['dd-phone'] = ""

    encoderData['lineItems'] = []
    dbOrderLines = StockOrderLine.objects.filter(order=orderObject)
    for orderLine in dbOrderLines:
        lineitem = {}
        lineitem['record-identifier'] = "LINEITEM"
        lineitem['line-item-number'] = orderLine.line
        lineitem['purchasers-product-code'] = orderLine.item.model
        lineitem['gtin-product-code'] = orderLine.item.EAN
        lineitem['suppliers-product-code'] = ""
        lineitem['item-description'] = orderLine.item.description
        lineitem['quantity'] = orderLine.quantity
        lineitem['unit-of-measure'] = ""
        lineitem['datetime-expected'] = decodeDate(etDict['datetime-expected']).strftime("%Y%m%d")
        lineitem['price-qualifier'] = "AAA"
        lineitem['unit-price'] = orderLine.invoiceActual
        lineitem['contract-number-reference'] = decodeReceivedText(etDict['quote-ref'])
        lineitem['number-of-packages'] = ""
        lineitem['packaging-level'] = ""
        lineitem['tax-details'] = "10"
        lineitem['line-item-free-text-1'] = ""
        lineitem['line-item-free-text-2'] = ""
        encoderData['lineItems'].append(lineitem)

    encoderData['headerFreeText'] = []
    for instruction in orderDict['etInstructions']:
        if instruction['type'] == "Delivery":
            qualifier = 'DEL'
        else:
            qualifier = 'PUR'
        freetextline = {
            'record-identifier' : 'FTXHEADER',
            'free-text-qualifier' : qualifier,
            'free-text-line-1' : decodeReceivedText(instruction["line1"]),
            'free-text-line-2' : decodeReceivedText(instruction["line2"]),
            'free-text-line-3' : decodeReceivedText(instruction["line3"]),
            'free-text-line-4' : decodeReceivedText(instruction["line4"]),
            'free-text-line-5' : decodeReceivedText(instruction["line5"]),
        }
        encoderData['headerFreeText'].append(freetextline)

    encoderData["endObject"] = {
        "record-identifier" : "END",
        "total-monetary-amount" : orderObject.orderTotalInvoiceExGST,
        "order-num" : orderObject.reference,
    }

    return encoderData
