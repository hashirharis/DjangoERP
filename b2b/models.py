from django.db import models
from django.conf import settings
from users.models import Staff, Store
from core.models import Product, Brand
from decimal import Decimal as D

import datetime

class HeadOfficeInvoice(models.Model):
    type_choices = (
        ('Purchase of stock', 'Purchase of stock'),
        ('Return of stock', 'Return of stock'),
        ('Claim', 'Claim'),
        ('Advertising Allowance', 'Advertising Allowance'),
        ('Stretch Target', 'Stretch Target'),
        ('Rebate (Credit)', 'Rebate (Credit)'),
        ('Rebate (Debit)', 'Rebate (Debit)'),
    )
    type = models.CharField(max_length=50, choices=type_choices, default="Purchase of stock")
    distributor = models.ForeignKey(Brand)
    store = models.ForeignKey(Store)
    invoiceNumber = models.CharField(max_length=100)
    invoiceDate = models.DateTimeField()
    orderReference = models.CharField(max_length=100)
    otherInvoiceReference = models.CharField(max_length=100, blank=True)
    dueDate = models.DateTimeField(null=True)
    extendedCredit = models.BooleanField(default=False)
    hoComments = models.TextField(blank=True)
    storeInformation = models.TextField(blank=True)
    freight = models.DecimalField("Freight(Ex)", max_digits=8, decimal_places=2)
    invTotalExGST = models.DecimalField("Total Invoice(Ex)", max_digits=8, decimal_places=2)
    invTotal = models.DecimalField("Total Invoice(Inc)",max_digits=8, decimal_places=2)
    netTotal = models.DecimalField("Total Store Net(Ex)", max_digits=8, decimal_places=2)
    chargedDate = models.DateTimeField(null=True)
    chargedBy = models.ForeignKey(Staff, null=True, related_name="invoice_charged")
    reconciledDate = models.DateTimeField(null=True)
    reconciledBy = models.ForeignKey(Staff, null=True)
    createdDate = models.DateTimeField(auto_now_add=True)
    modifiedDate = models.DateTimeField(auto_now=True, auto_now_add=True)
    createdBy = models.ForeignKey(Staff, related_name="invoice_created")

    def __unicode__(self):
        return u'%s' % self.invoiceNumber

class HeadOfficeInvoiceLine(models.Model):
    invoice = models.ForeignKey(HeadOfficeInvoice)
    item = models.ForeignKey(Product)
    unitPrice = models.DecimalField("Unit Price(Ex)", max_digits=8, decimal_places=2) #from ET/Invoice Price
    invoicePrice = models.DecimalField("Invoice (Inc)", max_digits=8, decimal_places=2) #unit Price * quantity * 1.10 (GST)
    quantity = models.IntegerField()
    storeNet = models.DecimalField("Store Net (Ex)", max_digits=8, decimal_places=2) #product spannnet
    line = models.PositiveIntegerField()

class Recon(models.Model):
    distributor = models.ForeignKey(Brand)
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    statementTotal = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(Staff)
    status = models.CharField(max_length=50) #COMPLETED, SAVED

    @property
    def totalInvoices(self):
        total = 0
        for line in self.reconlines_set.all():
            total += line.total
        return total

class ReconLines(models.Model):
    recon = models.ForeignKey(Recon)
    invoice = models.ForeignKey(HeadOfficeInvoice)
    selected = models.BooleanField()
    comment = models.CharField(max_length=255)

    @property
    def total(self):
        return self.invoice.invTotal

class Charge(models.Model):
    store = models.ForeignKey(Store)
    chargeGroup = models.PositiveIntegerField()
    chargeDate = models.DateTimeField()
    created = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(Staff)

    @staticmethod
    def getMostRecentChargeGroup():
        try:
            return Charge.objects.all().order_by('-created')[:1].get().chargeGroup
        except Charge.DoesNotExist:
            return 0

    @property
    def totalInvoices(self):
        total = 0
        for line in self.chargeline_set.all():
            total += line.total
        return total

class ChargeLine(models.Model):
    charge = models.ForeignKey(Charge)
    invoice = models.ForeignKey(HeadOfficeInvoice)

    @property
    def total(self):
        return self.invoice.invTotal

class B2BInvoice(models.Model):
    distributor = models.ForeignKey(Brand) #supplier-code
    store = models.ForeignKey(Store) #purchasers-ship-to-code
    invoiceNumber = models.CharField(max_length=100) #document-number
    invoiceDate = models.DateTimeField() #accounting-datetime
    orderNumber = models.CharField(max_length=100) #order-no-reference
    linkedTo = models.ForeignKey(HeadOfficeInvoice, null=True, blank=True)

    @staticmethod
    def testB2BInvoice():
        #for testing pre-NARTA
        if(len(B2BInvoice.objects.filter(pk=1))):
            return B2BInvoice.objects.get(pk=1)
        else:
            test = B2BInvoice()
            test.distributor = Brand.objects.get(pk=1)
            test.store = Store.objects.get(pk=1)
            test.invoiceNumber = "TEST-INV-12345"
            test.invoiceDate = datetime.datetime.now()
            test.orderNumber = "HO-CP-12345"
            test.save()
            testLine = B2BInvoiceLine()
            testLine.line = 1
            testLine.invoice = test
            testLine.item = Product.objects.get(pk=1)
            testLine.unitPrice = D(250.00)
            testLine.quantity = 1
            testLine.invoicePrice = D(250.00 * 1 * 1.1)
            testLine.save()
            testLine.pk = 0
            testLine.line = 2
            testLine.item = Product.objects.get(pk=2)
            testLine.unitPrice = D(335.00)
            testLine.quantity = 4
            testLine.invoicePrice = 335.00 * 4 * 1.1
            testLine.save()
            return test

class B2BInvoiceLine(models.Model):
    line = models.PositiveIntegerField() #line-item-number
    invoice = models.ForeignKey(B2BInvoice)
    item = models.ForeignKey(Product) #from GTIN
    unitPrice = models.DecimalField("Unit Price(Ex)", max_digits=8, decimal_places=2) #unit-price
    invoicePrice = models.DecimalField("Invoice (Inc)", max_digits=8, decimal_places=2) #monetary-amountgst-inclusive
    quantity = models.IntegerField()

class StockOrder(models.Model):
    store = models.ForeignKey(Store) #this is always the store the order is being placed FOR
    type_choices = (
        ('Order from Supplier', 'Order from Supplier'),
        ('Return to Supplier', 'Return to Supplier'),
        ('Transfer to Other Store', 'Transfer to Other Store'),
        ('Transfer from Other Store', 'Transfer from Other Store'),
    )
    type = models.CharField(max_length=250, choices=type_choices, default="Order from Supplier")
    reference = models.CharField(max_length=250, unique=True)
    packingSlipNumber = models.CharField(max_length=250, blank=True)
    invoice = models.ForeignKey(HeadOfficeInvoice, null=True)
    status = models.CharField(max_length=50)
    '''
    status for Regular Orders: SAVED,PENDING,ACCEPTED,REJECTED
    status for EDI Orders: SAVED,PENDING,ACCEPTED,REJECTED
    status for stock transfers: SAVED,PENDING,ACCEPTED,REJECTED,SENT,RECIEVED
    '''
    orderedBy = models.ForeignKey(Staff) #this indicates which store placed the order.
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    supplier = models.ForeignKey(Brand)
    comment = models.CharField(max_length=1000)
    orderTotalInvoiceExGST = models.DecimalField(max_digits=8, decimal_places=2)
    orderTotalInvoiceInGST = models.DecimalField(max_digits=8, decimal_places=2)
    orderTotalStoreNetInGST = models.DecimalField(max_digits=8, decimal_places=2)
    is_et = models.BooleanField()

    def __unicode__(self):
        return u'%s' % self.reference

    @property
    def orderTotalStoreNetExGST(self):
        return self.orderTotalStoreNetInGST / D('1.10')

    def orderTotalGST(self):
        return self.orderTotalInvoiceInGST - self.orderTotalInvoiceExGST

    def purchaser(self):
        return self.supplier.purchaser

#All the 'confusing' status are from the NARTA EDI Spec documentation
class ElectronicStockOrder(models.Model):
    #presend fields
    stockOrder = models.OneToOneField(StockOrder)
    type_choices = (
        ('220', 'Purchase'),
        ('221', 'Blanket Order'),
        ('226', 'Call off Order'),
    )
    et_type = models.CharField(max_length=250, choices=type_choices, default="Purchase")
    ddAddress1 = models.CharField("Street Addres Line 1", max_length=100, blank=True)
    ddAddress2 = models.CharField("Street Addres Line 2", max_length=100, blank=True)
    ddSuburb = models.CharField("Suburb", max_length=20, blank=True)
    ddState = models.CharField("State", max_length=50, blank=True)
    ddPostcode = models.CharField("Post Code", max_length=10, blank=True)
    ddName = models.CharField("Contact name", max_length=150, blank=True)
    ddPhone = models.CharField("Phone", max_length=50, blank=True)
    ddEmail = models.CharField("Email", max_length=50, blank=True)
    promotionalReference = models.CharField(max_length=50, blank=True)
    quotationReference = models.CharField(max_length=50, blank=True)
    blanketOrderReference = models.CharField(max_length=50, blank=True)
    dateRequired = models.DateField()
    deliveryWindowStart = models.DateField()
    deliveryWindowEnd = models.DateField()
    cancelOrderDate = models.DateField()
    status = models.CharField(max_length=50) #pending,partially accepted,accepted
    #post-send fields for Data being sent to NARTA
    sentDate = models.DateTimeField(null=True)
    sentRAW = models.TextField()
    #post-recieved fields for Data recieved from NARTA
    responseReceivedDate = models.DateTimeField(null=True)
    responseValue = models.CharField(max_length=50) #4=Change,27=Not Accepted,29=Accept in full
    responseOrderNumber = models.CharField(max_length=250)
    responseRAW = models.TextField()

    def __unicode__(self):
        return u'%s' % (self.stockOrder.reference)

    def markAsSent(self):
        self.sentDate = datetime.datetime.now()
        self.save()

    def is_dd(self):
        if self.ddAddress1 != "" or self.ddAddress2 != "":
            return True
        return False

class StockOrderLine(models.Model):
    order = models.ForeignKey(StockOrder)
    item = models.ForeignKey(Product)
    description = models.CharField(max_length=500)
    invoiceList = models.DecimalField(max_digits=8, decimal_places=2)
    invoiceActual = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.IntegerField()
    unitNet = models.DecimalField("Unit Net (Inc)", max_digits=8, decimal_places=2)
    lineNet = models.DecimalField("Line Net (Inc)", max_digits=8, decimal_places=2)
    line = models.PositiveIntegerField()
    etStatus = models.CharField(max_length=50, blank=True, null=True) #4=Change,27=Not Accepted,29=Accept in full, can be blank if the line isn't ET.

    def totalLineInvoice(self):
        return self.invoiceActual * self.quantity

    def quantityBooked(self):
        from stock.models import StoreInventoryItemMovement
        return StoreInventoryItemMovement.objects.filter(docType="Stock Order", docReference=self.order.reference).count()

    def quantityRemaining(self):
        return self.quantity - self.quantityBooked()

class StorePayment(models.Model):
    store = models.ForeignKey(Store)
    paymentAmount = models.DecimalField("Amount", max_digits=8, decimal_places=2)
    paymentDate = models.DateTimeField("Date", help_text="format DD/MM/YYY")
    created = models.DateTimeField(auto_now_add=True, auto_created=True)

    def processPayment(self):
        store = self.store
        store.currentDebt = store.currentDebt - self.paymentAmount
        store.save()

    def revertPayment(self):
        store = self.store
        store.currentDebt = store.currentDebt + self.paymentAmount
        store.save()