from users.models import Store, Staff

from django.db import models
from django.db.models import Q, Sum
from django.utils import timezone

import json
from datetime import datetime, timedelta

class Group(models.Model):
    name = models.CharField(max_length=100)
    stores = models.ManyToManyField(Store, related_name="bb_group")

    def __unicode__(self):
        return self.name

class Bulletin(models.Model):
    type_choices = (
        ('short', 'short'),
        ('long', 'long'),
        ('personal', 'personal'),
        ('message', 'message')
    )
    type = models.CharField(max_length=200, choices=type_choices)
    origin = models.ForeignKey(Staff)
    tag_choices = (
        ('Important', 'Important'),
        ('Price List', 'Price List'),
        ('Collations', 'Collations'),
        ('Promotions', 'Promotions'),
        ('Sell Through', 'Sell Through'),
        ('Price Drops', 'Price Drops'),
        ('Miscellaneous', 'Miscellaneous'),
        ('Catalogue', 'Catalogue')
    )
    tag = models.CharField(choices=tag_choices, max_length=100)
    toStores = models.ManyToManyField(Store, blank=True, verbose_name="")
    toStores.help_text = ""
    toGroups = models.ManyToManyField(Group, blank=True, verbose_name="")
    toGroups.help_text = ""
    subject = models.CharField(max_length=200)
    content = models.TextField()
    sendSMS = models.BooleanField("SMS Notification", default=False)
    sendEmail = models.BooleanField("Email Notification", default=False)
    sendSMSReminder = models.BooleanField("SMS Reminder", default=False)
    sendEmailReminder = models.BooleanField("Email Reminder", default=False)
    startDate = models.DateTimeField("Start", null=True, default=timezone.localtime(timezone.now()))
    endDate = models.DateTimeField("End", null=True)
    archiveDate = models.DateTimeField("Archive", null=True)
    started = models.BooleanField(default=False)
    archived = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(default=timezone.localtime(timezone.now()), blank=True, null=True)

    class Meta:
        ordering = ('-modified', '-created')

    def save(self, *args, **kwargs):
        if not kwargs.pop('skip_modified', False):
            self.modified = timezone.localtime(timezone.now())
        super(Bulletin, self).save(*args, **kwargs)

    @property
    def emailNotificationTemplate(self):
        return '%ss/reminder/email_notification.html' % self.getChild()[0]

    @property
    def smsNotificationTemplate(self):
        return '%ss/reminder/sms_notification.txt' % self.getChild()[0]

    def setArchivedAndStarted(self):
        '''
        we need this for form method and cronLocaleTime for other.
        '''
        if self.archiveDate:
            today = timezone.localtime(timezone.now()).date()
            start = timezone.localtime(self.startDate).date()
            archive = timezone.localtime(self.archiveDate).date()
            if today >= start: #started
                self.archived = False
                self.started = True
            if today >= archive: #archived
                self.archived = True
                self.started = False
            if today < start and today < archive: #pending
                self.archived = False
                self.started = False

    def notifyStores(self):
        today = timezone.localtime(timezone.now()).date()
        start = timezone.localtime(self.startDate).date()
        if start == today and self.sendEmail: #send email notification
            [x.send_notification_email(self) for x in self.readLog()]
        if start == today and self.sendSMS: #send sms notification
            [x.send_notification_sms(self) for x in self.readLog()]

    def endingSoon(self, days):
        today = timezone.localtime(timezone.now())
        x = timedelta(days=days)
        x_after = today + x
        #if the date + x is after the endDate
        #and the end date is in the future.
        return x_after.date() >= timezone.localtime(self.endDate).date() and (timezone.localtime(self.endDate).date() >= timezone.localtime(timezone.now()).date())

    def hasRead(self, store):
        read = False
        try:
            ReadLog.objects.get(store=store, bulletin=self)
            read = True
        except ReadLog.DoesNotExist:
            pass
        return read

    def markRead(self, store):
        try:
            readlog = ReadLog.objects.get(store=store, bulletin=self)
        except ReadLog.DoesNotExist:
            readlog = ReadLog(store=store, bulletin=self)
            readlog.save()

    def clearRead(self):
        ReadLog.objects.filter(bulletin=self).delete()

    def readLog(self, ):
        stores = [x.pk for x in self.toStores.all()]
        for group in self.toGroups.all():
            [stores.append(x.pk) for x in group.stores.all()]
        stores = Store.objects.filter(pk__in=stores)
        return stores

    def hitPercent(self):
        total = 0
        read = 0
        print self.readLog()
        for x in self.readLog():
            total += 1
            if self.hasRead(x):
                read += 1
        return float(read)/float(total) * 100

    def getChild(self):
        #returns tuple of 'type' and <instance>
        try:
            typeof, x = 'collation', self.collation
        except Collation.DoesNotExist:
            try:
                typeof, x = 'promotion', self.promotion
            except Promotion.DoesNotExist:
                typeof, x = 'bulletin', self
        return typeof, x

    def toObj(self, store): #for single object
        child = self.getChild()
        readLog = sorted([{'store':x.name, 'read':self.hasRead(x)} for x in self.readLog()], key=lambda store: store['read']) #sort by read
        obj = {
            "id": self.id,
            "collation": child[0] == 'collation',
            "responded": False,
            "type": self.type,
            "subject": self.subject,
            "content": self.content,
            "startDate": timezone.localtime(self.startDate).strftime("%d/%m/%Y") if self.startDate else "",
            "endDate": timezone.localtime(self.endDate).strftime("%d/%m/%Y") if self.endDate else "",
            "readLog": readLog,
            "hitPercent": "%.2f" % self.hitPercent()
        }
        if child[0] == 'promotion':
            obj['eligibleModels'] = self.promotion.eligibleModels
        elif child[0] == 'collation' and store: #if this is a collation and store is requesting
            obj['responded'] = child[1].hasResponded(store)
        return obj

class Collation(Bulletin):
    order_choices = (
        ('Email', 'Email'),
        ('Fax', 'Fax'),
        ('EDI', 'EDI'),
        ('Manual', 'Manual'),
        ('PDO', 'PDO'),
    )
    orderMethod = models.CharField(choices=order_choices, max_length=100)

    def hasResponded(self, store):
        try:
            CollationResponse.objects.get(store=store, collation=self)
            responded = True
        except CollationResponse.DoesNotExist:
            responded = False
        return responded

    def endingSoon(self):
        return super(Collation, self).endingSoon(2)

    def collationOrdersForStore(self, store):
        for month in self.deliveryMonths():
            order = CollationOrder.objects.get_or_create(collation=self, store=store, deliveryMonth=month)[0]
            for line in self.CollationItems():
                orderLine = CollationOrderLine.objects.get_or_create(order=order, collationLine=line)[0]
        return CollationOrderLine.objects.filter(order__collation=self, order__store=store).order_by('collationLine__line')

    def updateCollation(self):
        #update all collation orders that already exist against this collation to give them the new lines.
        for order in CollationOrder.objects.filter(collation=self, totalQuantity__gt=0):
            for line in self.CollationItems():
                orderLine = CollationOrderLine.objects.get_or_create(order=order, collationLine=line)[0]

    def deliveryMonths(self):
        return DeliveryMonth.objects.filter(collation=self).order_by('line')

    def CollationItems(self):
        return CollationItem.objects.filter(collation=self).order_by('line')

    def deliveryMonths_arr(self):
        return map(lambda month: {
            "line" : month.line,
            "month" : month.month,
            "hidden": month.hidden,
            "deleted": month.deleted
        }, self.deliveryMonths())

    def openOrders(self):
        return CollationOrder.objects.filter(collation=self, totalQuantity__gt=0).exclude(Q(status="Completed") | Q(status="Cancelled")).count()

    def lineTotals(self):
        from django.db.models import Max
        orders = CollationOrder.objects.filter(collation=self, totalQuantity__gt=0)
        maxLine = CollationOrderLine.objects.filter(order__in=orders).aggregate(Max('collationLine__line')).get('collationLine__line__max', 0)
        return [CollationOrderLine.objects.filter(order__in=orders, collationLine__line=line).aggregate(Sum('quantity')).get('quantity__sum', 0) for line in range(1, maxLine+1)]

    def completeTotal(self):
        return CollationOrder.objects.filter(collation=self, totalQuantity__gt=0).aggregate(Sum('totalQuantity')).get('totalQuantity__sum', 0)

class CollationItem(models.Model):
    line = models.PositiveIntegerField()
    collation = models.ForeignKey(Collation)
    model = models.CharField(max_length=150)
    hidden = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    description = models.CharField(max_length=150, blank=True, null=True)
    prices = models.TextField(blank=True) #store the prices in key value json

    @property
    def prices_dict(self):
        return json.loads(self.prices)

class DeliveryMonth(models.Model):
    line = models.PositiveIntegerField()
    collation = models.ForeignKey(Collation)
    month = models.CharField(max_length="250")
    hidden = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)

    def getOrder(self, store):
        return CollationOrder.objects.get(deliveryMonth=self, collation=self.collation, store=store)

class CollationResponse(models.Model):
    collation = models.ForeignKey(Collation)
    store = models.ForeignKey(Store)
    yes = models.BooleanField(default=True) #default response is yes.
    reason = models.TextField()
    #reason could be anything ranging from either the drop down or the text they entered
    created = models.DateTimeField(auto_now_add=True)

class CollationOrder(models.Model):
    collation = models.ForeignKey(Collation)
    store = models.ForeignKey(Store)
    orderNumber = models.CharField(max_length=200, default="", blank=True)
    storeComment = models.CharField(max_length=150, default="", blank=True)
    hoOrderNumber = models.CharField(max_length=200, default="", blank=True)
    hoHidden = models.BooleanField(default=False)
    deliveryMonth = models.ForeignKey(DeliveryMonth)
    status_choices = (
        ('Open', 'Open'),
        ('Pending', 'Pending'),
        ('Complete', 'Complete'),
        ('Sent to Supplier', 'Sent to Supplier'),
        ('Awaiting Target', 'Awaiting Target'),
        ('Cancelled', 'Cancelled'),
    )
    status = models.CharField(choices=status_choices, max_length=50, default="Open")
    totalQuantity = models.PositiveIntegerField(default=0)
    modified = models.DateTimeField(auto_now=True, auto_created=True)
    created = models.DateTimeField(auto_created=True, auto_now_add=True)

class CollationOrderLine(models.Model):
    order = models.ForeignKey(CollationOrder)
    collationLine = models.ForeignKey(CollationItem)
    quantity = models.PositiveIntegerField(default=0)

class ReadLog(models.Model):
    store = models.ForeignKey(Store)
    bulletin = models.ForeignKey(Bulletin)
    dateRead = models.DateTimeField(auto_now_add=True, auto_created=True)

class Promotion(Bulletin):
    eligibleModels = models.CharField(max_length=200, default="", verbose_name="Elgible Models")
    eligibleModels.help_text = ""
    promotionType_choices = (
        ('Customer', 'Customer'),
        ('Store', 'Store'),
    )
    promotionType = models.CharField(choices=promotionType_choices, max_length=50, default="Store")

    def endingSoon(self, days=7):
        return super(Promotion, self).endingSoon(days)
