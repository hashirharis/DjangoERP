from django.contrib.auth.models import User
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils import timezone
from decimal import Decimal as D

from brutils.generic.querysets import GenericObjectManager, StoreLevelObjectQueryset
from datetime import timedelta

class StoreGroup(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey('self', null=True)

    def getImmediateAndBelowStores(self):
        #get the stores in the group here and below only to level of 2
        return Store.objects.filter(Q(group=self) | Q(group__parent=self))

class Store(models.Model):
    group = models.ForeignKey(StoreGroup)
    isHead = models.BooleanField() #is group head
    user = models.ForeignKey(User, unique=True, null=True) #will always be created if null
    name = models.CharField(max_length=250)
    code = models.CharField(max_length=50)
    contact = models.CharField("Contact Name", max_length=100)
    address = models.CharField("Address", max_length=100, blank=True, null=False)
    suburb = models.CharField("Suburb", max_length=100, blank=True, null=False)
    city = models.CharField("City", max_length=50, blank=True, null=False)
    state = models.CharField("State", max_length=50, blank=True, null=False)
    postcode = models.CharField("Post Code", max_length=10, blank=True, null=False)
    fax = models.CharField("Fax", max_length=50, blank=True, null=False)
    email = models.CharField("Email", max_length=50, blank=True, null=False)
    phone = models.CharField("Phone", max_length=50, blank=True, null=False)
    mobile = models.CharField(max_length=50, default='', help_text="Include +61 in the mobile number", blank=True)
    companyName = models.CharField("Company Name", max_length=250, blank=True, null=False)
    spanStoreID = models.CharField(max_length=50, blank=True, null=False)
    ABN = models.CharField(max_length=250,  blank=True, null=False)
    ACN = models.CharField(max_length=250, blank=True, null=False)
    GLN = models.CharField("Global Location Number(GLN)", max_length=250, blank=True, default="")
    #financials
    purchaseLimit = models.DecimalField(max_digits=8, decimal_places=2, default=D('1000.00'))
    extendedCreditTotals = models.DecimalField(max_digits=8, decimal_places=2, default=D('0.00'))
    currentDebt = models.DecimalField(max_digits=8, decimal_places=2, default=D('0.00'))
    irpInvoices = models.DecimalField(max_digits=8, decimal_places=2, default=D('0.00'))
    notInvoiced = models.DecimalField(max_digits=8, decimal_places=2, default=D('0.00'))
    #default open to buy...
    openToBuy = models.DecimalField(max_digits=8, decimal_places=2, default=D('1000.00'))

    def __unicode__(self):
        return u'%s %s' % (self.code, self.name)

    def save(self): #make sure a user is always created for the store
        if self.user is None:
            newuser = User.objects.create_user(self.code, email="", password=self.code+"123")
            self.user = newuser.save()
            #create default store manager staff member
            managerMember = Staff(
                store=self,
                name='%s manager' % self.code,
                initials=self.code[:4],
                username=self.code,
                password=self.code+'123',
                privelegeLevel=3
            )
            managerMember.save()
        super(Store, self).save()

    def displayHOMenu(self):
        if self.code == 'HO' or self.code == 'VW':
            return True
        else:
            return False

    def htmlFormattedAddress(self):
        formattedAddress = u'%s<br />%s<br />%s %s %s<br />ABN: %s' % (self.address, self.suburb, self.city, self.state, self.postcode, self.ABN)
        return formattedAddress

    def email_store(self, html_content, subject):
        if self.email == '':
            return
        from django.core.mail import EmailMultiAlternatives
        text_content = 'Reminder/Notification Message, check intranet for more details !'
        msg = EmailMultiAlternatives(subject, text_content, 'no-reply@biriteintranet.com.au', [self.email])
        print 'sending email to: %s' % self.name
        print html_content
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    #IAS
    def updateOpenToBuy(self):
        """
        This uses a formula to calculate the open to buy amount for each store. Gets updated frequently.
        """
        from b2b.models import HeadOfficeInvoice, StockOrder
        debitTypes = settings.DEBIT_TYPES

        #uncharged IRP Invoices
        totalIRPInvoices = D('0.00')
        for invoice in HeadOfficeInvoice.objects.all().filter(store=self, chargedDate__isnull=True):
            totalIRPInvoices += (invoice.netTotal if invoice.type not in debitTypes else invoice.netTotal*-1)
        self.irpInvoices = totalIRPInvoices

        #uninvoiced purchases (only in the last x days)
        today = timezone.localtime(timezone.now())
        three_days = timedelta(days=3)
        three_days_previously = today - three_days

        totalPurchases = D('0.00')
        for order in StockOrder.objects.all().filter(store=self, created__gte=three_days_previously).exclude(status="Pending"):
            totalPurchases += (order.orderTotalStoreNetExGST if order.type is not "Return to Supplier" else order.orderTotalStoreNetInGST * -1)
        self.notInvoiced = totalPurchases

        self.openToBuy = \
            self.purchaseLimit + self.extendedCreditTotals - self.currentDebt \
            - self.irpInvoices - self.notInvoiced

        self.save()

        print self.openToBuy

    #BB methods
    def send_pleaselogin_email(self):
        subject = "BiRite Intranet"
        html_content = render_to_string('emails/login_reminder.html')
        self.email_store(html_content, subject)

    def send_reminder_email(self, bulletins=None):
        subject = "BiRite Intranet"
        html_content = render_to_string('emails/bulletins_reminder.html', {'bulletins': bulletins})
        self.email_store(html_content, subject)

    def send_notification_email(self, bulletin=None):
        subject = "BiRite Intranet"
        html_content = render_to_string(bulletin.emailNotificationTemplate, {'bulletin': bulletin})
        self.email_store(html_content, subject)

    def sms_store(self, text_content):
        if self.mobile == '' or settings.DEBUG: #set to False on live
            return
        from twilio.rest import TwilioRestClient
        print 'sending sms to: %s' % self.name
        print text_content
        client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.sms.messages.create(body=text_content, to=self.mobile, from_="+12674632398")

    def send_reminder_sms(self, bulletins=None):
        text_content = render_to_string('sms/sms_reminder.txt', {'bulletins': bulletins})
        self.sms_store(text_content)

    def send_notification_sms(self, bulletin=None):
        text_content = render_to_string(bulletin.smsNotificationTemplate, {'bulletin': bulletin})
        self.sms_store(text_content)

class StoreLevelObject(models.Model):
    store = models.ForeignKey(Store)
    group = models.ForeignKey(StoreGroup)
    isShared = models.BooleanField(verbose_name="Global", default=False) #isShared indicates store level product only
    queryset = StoreLevelObjectQueryset
    objects = GenericObjectManager()

    class Meta:
        abstract = True

    def can_read(self, store):
        #can only read if store is either the owner or part of the group that owns the object
        if self.store == store:
            return True
        if self.isShared:
            if store in self.group.getImmediateAndBelowStores():
                return True
        return False

    def can_write(self, store):
        #can only write if store is either the owner or head of the group that owns the object
        if self.store == store:
            return True
        if self.isShared:
            if self.group == store.group and store.isHead:
                return True
        return False

class Staff(models.Model):
    store = models.ForeignKey(Store)
    name = models.CharField(max_length=250)
    username = models.CharField(max_length=250) #unique to store
    initials = models.CharField(max_length=4)
    password = models.CharField(max_length=250) #TODO : need to salt hash before verifying
    priveleges = (
        (0, '0 - Blocked'),
        (1, '1 - Price Lookup, Sales'),
        (2, '2 - Stock Control'),
        (3, '3 - Manager')
    )
    privelegeLevel = models.IntegerField(default=0, choices=priveleges) #blocked user

    def been_three_days(self):
        today = timezone.localtime(timezone.now())
        three_days = timedelta(days=3)
        three_days_previously = today - three_days
        return timezone.localtime(self.user.profile.last_accessed).date() < three_days_previously.date()

    def unreadBulletins(self):
        from bulletins.models import Bulletin, ReadLog
        allBulletins = Bulletin.objects.all().filter(Q(toStores=self.store)|Q(toGroups__stores=self.store), type="message", started=True).exclude(tag='Promotions').values('pk').distinct()
        read = len(ReadLog.objects.all().filter(store=self.store, bulletin__pk__in=allBulletins))
        return len(allBulletins) - read

    def unreadCollations(self):
        from bulletins.models import Bulletin, ReadLog
        allBulletins = Bulletin.objects.all().filter(Q(toStores=self.store)|Q(toGroups__stores=self.store), Q(type="short")|Q(type="long"), started=True).values('pk').distinct()
        read = len(ReadLog.objects.all().filter(store=self.store, bulletin__pk__in=allBulletins))
        return len(allBulletins) - read

    def unreadPromotions(self):
        from bulletins.models import Promotion, ReadLog
        allBulletins = Promotion.objects.all().filter(Q(toStores=self.store)|Q(toGroups__stores=self.store), started=True,).values('pk').distinct()
        read = len(ReadLog.objects.all().filter(store=self.store, bulletin__pk__in=allBulletins))
        return len(allBulletins) - read

    def is_bb_admin(self):
        #can add in different users you wish to be bulletin board admins in here by hard coding.
        return self.store.code == "HO" and self.privelegeLevel >= 3

class StoreProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    #Sales module settings
    floatValue = models.DecimalField("Float", max_digits=8, decimal_places=2, default=250.00)
    deliveryPrice = models.DecimalField("Delivery Price", max_digits=8, decimal_places=2, default=0.00)
    #template = models.ForeignKey(SalesTemplate)
    quotationsExpiry = models.PositiveIntegerField("Days after quotes expire", default=30)
    noStockWarning = models.BooleanField("Display a not in stock warning", default=True)
    warrantyOffer = models.BooleanField("Prompt for warranty", default=True)
    useGoPrice = models.BooleanField("Use Go Price if available", default=True)
    useCatalogPrice = models.BooleanField("Use Catalog Price if available", default=False)
    salePriceWarnings = models.BooleanField("Sale Price Too High Warning", default=True, help_text="The system will display alerts if the sale price is either below cost or too high")
    showSellThrough = models.BooleanField("Show Sell Through in Price Breakdown for Products", default=False)
    customerNotAttached = models.BooleanField("Display a warning if a sale is being made without a customer attached", default=True)
    paymentDetailsOnInvoice = models.BooleanField("Display payment details on the invoice", default=False)
    printDeliveryDetails = models.BooleanField("Print the delivery details", default=True)
    #privelege Levels
    priveleges = (
        (0, '0 - Blocked'),
        (1, '1 - Price Lookup, Sales'),
        (2, '2 - Stock Control'),
        (3, '3 - Manager')
    )
    reportsLevel = models.IntegerField("Privelege Level required to access reports", default=2, choices=priveleges)
    creditLimits = models.IntegerField("Privelege Level required to adjust credit limit", default=3, choices=priveleges)
    #loadingValue = models.PositiveIntegerField("Load the cost prices with a blanket %")





User.profile = property(lambda u: StoreProfile.objects.get_or_create(user=u)[0])