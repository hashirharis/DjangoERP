__author__ = 'Yussuf'
import csv
import StringIO

def encodePurchaseOrder(dictObject):

    stringIO = StringIO.StringIO()
    purchaseOrderCsv = csv.writer(stringIO, delimiter='|', quoting=csv.QUOTE_NONE, lineterminator='~')

    purchaseOrderCsv.writerow(encodeHeader(dictObject))
    for freeText in dictObject['headerFreeText']:
        purchaseOrderCsv.writerow(encodeFreeText(freeText))
    for lineItem in dictObject['lineItems']:
        purchaseOrderCsv.writerow(encodeLineItem(lineItem))
    purchaseOrderCsv.writerow(encodeEndRecordItem(dictObject['endObject']))

    return stringIO.getvalue()

def encodeHeader(dictObject):
    '''headerStructure = [
        u'record-identifier',           #EAPO
        u'transaction-set',             #ORDERS
        u'order-type',                  #PurchaseOrder/blanketorder etc.
        u'order-number',                #number
        u'message-function',            #9 - original
        u'test-production-flag',        #Test or Production
        u'receiver-identifier',         #supplier
        u'sender-identifier',           #HO GLN
        u'order-datetime',              #YYYYMMDDhhss
        u'datetime-expected',           #YYYMMDD
        u'shipment-request',            #ussually day after
        u'cancel-not-after',            #ussually day after + 3 months
        u'deliver-not-after',           #above
        u'deliver-not-before',          #day after
        u'contract-number-reference',
        u'blanket-order-no-reference',
        u'promotion-deal-no-reference',
        u'sales-dept-no-reference',
    ]
    otherDetailsStructure = {
        u'purchaser',               #HO             #
        u'supplier',                #supplier GLN
        u'suppliers-name',          #supplier name
        u'purchaser-ship-to-code',  #store GLN
        u'purchaser-ship-to-name',  #store name
        u'dd-name',
        u'dd-address-1',
        u'dd-address-2',
        u'dd-city-suburb',
        u'dd-state',
        u'dd-post-code',
        u'dd-country',
        u'dd-contact-name',
        u'dd-email',
        u'dd-phone',
    }
    '''
    #main details
    headerArray = [
        dictObject['record-identifier'],           #EAPO
        dictObject['transaction-set'],             #ORDERS
        dictObject['order-type'],                  #PurchaseOrder/blanketorder etc.
        dictObject['order-number'],                #number
        dictObject['message-function'],            #9 - original    #5
        dictObject['test-production-flag'],        #Test or Production
        dictObject['receiver-identifier'],         #supplier GLN
        dictObject['sender-identifier'],           #HO GLN
        dictObject['order-datetime'],              #YYYYMMDDhhss
        dictObject['datetime-expected'],           #YYYMMDD #10
        dictObject['shipment-request'],            #ussually day after
        dictObject['cancel-not-after'],            #ussually day after + 3 months
        dictObject['deliver-not-after'],           #above
        dictObject['deliver-not-before'],          #day after
        dictObject['contract-number-reference'],    #15
        dictObject['blanket-order-no-reference'],
        dictObject['promotion-deal-no-reference'],
        dictObject['sales-dept-no-reference'],
        dictObject['purchaser'],                    #HO GLN
    ]
    for i in range(20,30): headerArray.append("")
    #supplier details
    headerArray.append(dictObject['supplier'])
    headerArray.append(dictObject['suppliers-name'])
    for i in range(32,38): headerArray.append("")
    headerArray.append(dictObject['purchaser-ship-to-code'])
    headerArray.append(dictObject['purchaser-ship-to-name'])  #Store Name
    for i in range(40,58): headerArray.append("")
    headerArray += [
        dictObject['dd-name'],
        dictObject['dd-street-address-1'],
        dictObject['dd-street-address-2'], #60
        dictObject['dd-suburb'],
        dictObject['dd-state'],
        dictObject['dd-post-code'],
        dictObject['dd-country'],
        dictObject['dd-contact-name'],
        dictObject['dd-email'],
        dictObject['dd-phone'],
    ]
    for i in range(68,70): headerArray.append("")
    return headerArray

def encodeLineItem(lineitem):
    lineArray = [
        lineitem['record-identifier'],
        lineitem['line-item-number'],
        lineitem['purchasers-product-code'],
        lineitem['gtin-product-code'],
        lineitem['suppliers-product-code'], #5
        lineitem['item-description'],
        lineitem['quantity'],
        lineitem['unit-of-measure'],
        lineitem['datetime-expected'],
        lineitem['price-qualifier'],    #10
        lineitem['unit-price'],
        lineitem['contract-number-reference'],
        lineitem['number-of-packages'],
        lineitem['packaging-level'],
        lineitem['tax-details'],    #15
        lineitem['line-item-free-text-1'],
        lineitem['line-item-free-text-2'],
    ]
    for i in range(18,25): lineArray.append("")
    return lineArray

def encodeFreeText(freetext):
    lineArray = [
        freetext['record-identifier'],
        freetext['free-text-qualifier'],
        freetext['free-text-line-1'],
        freetext['free-text-line-2'],
        freetext['free-text-line-3'],
        freetext['free-text-line-4'],
        freetext['free-text-line-5'],
    ]
    return lineArray

def encodeEndRecordItem(endObject):
    lineArray = [
        endObject['record-identifier'],
        endObject['total-monetary-amount'],
        endObject['order-num'],
    ]
    return lineArray