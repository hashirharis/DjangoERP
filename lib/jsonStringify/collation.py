__author__ = 'Yussuf'
from django.core.urlresolvers import reverse

from bulletins.models import Collation, CollationItem, CollationOrder, CollationOrderLine, Store, Group, DeliveryMonth
from lib.jsonStringify.utility import decodeReceivedText, decodeBulletinBoardDate

from django.utils import timezone
from decimal import Decimal as D
import json

def collationFromJson(collationData, type, user):
    '''
        the json object passed to this method is already converted using json.dumps
        it is the 'salesData' object
    '''
    try:
        collation = Collation.objects.get(pk=collationData['id'])
        created = False
    except Collation.DoesNotExist:
        collation = Collation()
        created = True
    #bulletin fields
    collation.type = type
    collation.origin = user
    collation.tag = 'Collations'
    collation.subject = decodeReceivedText(collationData['subject'])
    collation.content = decodeReceivedText(collationData['content'])
    collation.sendSMS = collationData['sendSMS']
    collation.sendEmail = collationData['sendEmail']
    collation.sendSMSReminder = collationData['sendSMSReminder']
    collation.sendEmailReminder = collationData['sendEmailReminder']
    collation.archiveDate = timezone.make_aware(decodeBulletinBoardDate(collationData['archiveDate']), timezone.get_current_timezone())
    collation.startDate = timezone.make_aware(decodeBulletinBoardDate(collationData['startDate']), timezone.get_current_timezone())
    collation.endDate = timezone.make_aware(decodeBulletinBoardDate(collationData['endDate']), timezone.get_current_timezone())
    #collation specific
    collation.orderMethod = collationData['orderMethod']
    collation.save()
    collation.setArchivedAndStarted()
    collation.save(skip_modified=True)

    collation.toStores.clear()
    for storepk in collationData['toStores']:
        collation.toStores.add(Store.objects.get(pk=storepk))
    collation.toGroups.clear()
    for grouppk in collationData['toGroups']:
        collation.toGroups.add(Group.objects.get(pk=grouppk))

    if created:
        collation.notifyStores()

    line = 0
    for collationLine in collationData['collationItems']:
        line += 1
        try:
            dbCollationItem = CollationItem.objects.get(collation=collation, line=line)
        except CollationItem.DoesNotExist:
            dbCollationItem = CollationItem(collation=collation, line=line)
        dbCollationItem.model = collationLine['model']
        dbCollationItem.hidden = collationLine['hidden']
        dbCollationItem.deleted = collationLine['deleted']
        dbCollationItem.prices = json.dumps(collationLine['prices'])
        dbCollationItem.save()

    #deliveryMonths
    line = 0
    for month in collationData['deliveryMonths']:
        line += 1
        try:
            dbDeliveryMonth = DeliveryMonth.objects.get(collation=collation, line=line)
        except DeliveryMonth.DoesNotExist:
            dbDeliveryMonth = DeliveryMonth(collation=collation, line=line)
        dbDeliveryMonth.month = month['month']
        dbDeliveryMonth.hidden = month['hidden']
        dbDeliveryMonth.deleted = month['deleted']
        dbDeliveryMonth.save()
    return collation

def jsonFromCollation(collation):
    '''
        returns object to later be loaded using json.loads
    '''
    collationItems = []
    line = 0
    dbCollationItems = CollationItem.objects.filter(collation=collation)
    for dbCollationItem in dbCollationItems:
        line += 1
        collationLine = {
            "line": dbCollationItem.line,
            "model": dbCollationItem.model,
            "prices": dbCollationItem.prices_dict,
            "hidden": dbCollationItem.hidden,
            "deleted": dbCollationItem.deleted
        }
        collationItems.append(collationLine)
    #all together
    collationData = {
        'id': collation.id,
        "subject": collation.subject,
        "startDate": timezone.localtime(collation.startDate).strftime('%m/%d/%Y'),
        "endDate": timezone.localtime(collation.endDate).strftime('%m/%d/%Y'),
        "archiveDate": timezone.localtime(collation.archiveDate).strftime('%m/%d/%Y'),
        "tag": collation.tag,
        "toStores": [x.id for x in collation.toStores.all()],
        "toGroups": [x.id for x in collation.toGroups.all()],
        "content": collation.content,
        "sendSMS": collation.sendSMS,
        "sendEmail": collation.sendEmail,
        "sendSMSReminder": collation.sendSMSReminder,
        "sendEmailReminder": collation.sendEmailReminder,
        "collationItems": collationItems,
        "orderMethod": collation.orderMethod,
        "deliveryMonths": collation.deliveryMonths_arr(),
    }
    return collationData

def updateOrders(orders=None, admin=False):
    if admin:
        for jsonOrder in orders:
            order = CollationOrder.objects.get(pk=jsonOrder['id'])
            order.status = jsonOrder['status']
            #order.orderNumber = jsonOrder['orderNum']
            order.hoHidden = jsonOrder['hoHidden']
            order.hoOrderNumber = jsonOrder.get('hoOrderNumber', '')
            order.save()
    else:
        for jsonOrder in orders:
            if jsonOrder.get('totalQuantity', None) is None:
                return
            order = CollationOrder.objects.get(pk=jsonOrder['id'])
            order.totalQuantity = jsonOrder['totalQuantity']
            order.orderNumber = jsonOrder['orderNum']
            order.storeComment = jsonOrder['orderComment']
            order.save()
            for jsonOrderLine in jsonOrder['orderLines']:
                orderline = CollationOrderLine.objects.get(pk=jsonOrderLine['lineid'])
                orderline.quantity = jsonOrderLine['quantity']
                orderline.save()