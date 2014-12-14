from django.db import models
from core.models import Product
from pos.models import Sale
from users.models import Staff, Store

from django.db import models
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse_lazy

class StoreInventory(models.Model):
    #TODO: Every day at midnight a snapshot to be taken and the figures to be put into a model table similar to Sales History
    #TODO: Every month a snapshot to be taken for the SalesHistory for Merchandiser
    product = models.ForeignKey(Product)
    store = models.ForeignKey(Store)
    level = models.IntegerField(default=0) #products in stock
    available = models.IntegerField(default=0) #products in stock - customer order
    customerOrder = models.IntegerField(default=0) #product on order
    stockOrder = models.IntegerField(default=0) #stock on order
    quotation = models.IntegerField(default=0) #products quotedd

    @property
    def req(self):
        return (self.available+self.stockOrder - self.customerOrder) < 1

    @property
    def req(self):
        return True if self.available + self.stockOrder - self.customerOrder < 1 else False

    def updateAll(self):
        #this updates the figures after something has changed, decided against querying for each figure everytime to avoid load on database.
        self.updateCustomerOrder()
        self.updateAvailable()
        self.updateStockOrder()
        self.updateQuotation()
        return self

    def updateCustomerOrder(self):
        from pos.models import SalesLine
        lines = SalesLine.objects.all().filter(sale__terminal__store=self.store, sale__status="PENDING", item=self.product)
        total = 0
        for sale in lines:
            if sale.quantity != sale.released:
                total += sale.quantity - sale.released
        self.customerOrder = total
        self.save()
        return total

    def updateAvailable(self):
        self.available = self.level - self.customerOrder
        self.save()
        return self.available

    def updateStockOrder(self):
        from b2b.models import StockOrderLine
        total = StockOrderLine.objects.all().filter(order__store=self.store, order__status="PENDING", item=self.product).aggregate(Sum('quantity'))['quantity__sum']
        if total:
            self.stockOrder = total
            self.save()
        return total

    def updateQuotation(self):
        from pos.models import SalesLine
        total = SalesLine.objects.all().filter(sale__terminal__store=self.store, sale__status="QUOTE", item=self.product).aggregate(Sum('quantity'))['quantity__sum']
        if total:
            self.quotation = total
            self.save()
        return total

    def __unicode__(self):
        return u'%s | %s | %i' % (self.store.name, self.product.model, self.level)

class StoreInventoryItemMovement(models.Model):
    movementChoices = (
        ('IN', 'IN'), #Refund, Stock Order, Book-in found stock (Manual), stocktake
        ('OUT', 'OUT'), #Sale, Refund from supplier, Book-out lost stock (Manual), stocktake
    )
    docTypes = (
        ('Sale', 'Sale'),
        ('Stock Order', 'Stock Order'),
        ('Manual', 'Manual'),
        ('Stocktake', 'Stocktake'),
    )
    docType = models.CharField("Document Type", max_length=100, choices=docTypes)
    docReference = models.CharField(max_length=300) #reference to document number
    docDate = models.DateTimeField("Documentation Date", auto_now_add=True, auto_created=True)
    createdBy = models.ForeignKey(Staff)

    '''
    This will create a url to the documentation that describes the movement for a product into or out of a store.
    '''
    def url(self):
        if self.docType == "Sale":
            sale = Sale.objects.get(code=self.docReference)
            return reverse_lazy('pos:openSale', args=(sale.terminal.id, sale.id,))
        elif self.docType == "Stock Order":
            from b2b.models import StockOrder
            order = StockOrder.objects.get(reference=self.docReference)
            return reverse_lazy('b2b:openOrder', args=(order.id,))
        elif self.docType == "StockTake":
            return reverse_lazy('stock:openStockTake', args=(self.docReference,))
        elif self.docType == "Manual":
            return '#'

    '''
    This will automatically create a movement for the documentation type filled out with relevant information
    according to document type.
    '''
    @staticmethod
    def movementFromReference(reference, referenceType):
        item = StoreInventoryItemMovement()
        item.docType = referenceType
        if referenceType == "Sale":
            item.docReference = reference.code
            item.createdBy = reference.salesPerson
        elif referenceType == "Stock Order":
            item.docReference = reference.reference
            item.createdBy = reference.orderedBy
        elif referenceType == "StockTake":
            item.docReference = reference.id
            item.createdBy = reference.createdBy
        elif referenceType == "Manual":
            item.docReference = reference.id
            item.createdBy = reference.createdBy
        return item

class ManualStockMovement(models.Model):
    createdBy = models.ForeignKey(Staff)
    comments = models.TextField(null=True, blank=True)

'''
    All In-Stock Items have an IN movement but no OUT movement
    All Stock Items with movement OUT but not IN are NSBI Items (No Stock Booked In)
'''
class StoreInventoryItem(models.Model):
    class Meta:
        ordering = ['-pk']

    serial = models.CharField(max_length=255, null=True, blank=True)
    inventory = models.ForeignKey(StoreInventory)
    movementOut = models.ForeignKey(StoreInventoryItemMovement, related_name='movementOut', null=True) #movement out without movement in is a NSBI.
    movementIn = models.ForeignKey(StoreInventoryItemMovement, related_name='movementIn', null=True) #movement in without movement out regular purchase order by store.
    purchaseNet = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0.00) #ex GST
    created = models.DateTimeField(auto_now_add=True)

    def claimPendingNet(self):
        #TODO: Get the pending claims on this item. For View Product Page
        pass

    def adjustedNet(self):
        #TODO: get the adjusted Net after all completed claims. For View Product Page
        pass

class Claim(models.Model):
    reference = models.CharField(max_length=250)
    status = models.CharField(max_length=50) #SAVED, PENDING (For HO Claims), COMPLETED
    movementChoices = ( #All Claims
        ('PP', 'Price Protection'), #PP charge
        ('MD', 'Mark Down'), #Damages, Claims from HO
        ('ICIS', 'Incorrectly Charged Invoice (Supplier)'),
        ('ICIHO', 'Incorrectly Charged Invoice (Head Office)'),
    )
    type = models.CharField("Claim Type", max_length=20, choices=movementChoices)
    comments = models.TextField()
    store = models.ForeignKey(Store)
    created = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(Staff)

    @staticmethod
    def generateDocReference(store):
        nums = Claim.objects.filter(store=store).count()
        return "CLM-%s-%i" % (store.code, nums)

class ClaimLine(models.Model):
    claim = models.ForeignKey(Claim)
    inventoryItem = models.ForeignKey(StoreInventoryItem)
    description = models.CharField(max_length=250)
    oldNetPrice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0.00) #ex GST
    newNetPrice = models.DecimalField(max_digits=8, decimal_places=2, blank=True, default=0.00) #ex GST
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

'''
All ClaimLines are also StoreInventoryItemPriceMovements (This is for readability)
'''
class StoreInventoryItemPriceMovement(models.Model):
    claimline = models.ForeignKey(ClaimLine)

    @property
    def status(self): #charge status determines whether this movement was processed or not.
        return self.claimline.claim.status

class StockTake(models.Model):
    status = models.CharField(max_length=50) #COMPLETED, SAVED
    store = models.ForeignKey(Store)
    created = models.DateTimeField(auto_now_add=True)
    createdBy = models.ForeignKey(Staff)

class StockTakeLine(models.Model):
    stocktake = models.ForeignKey(StockTake)
    product = models.ForeignKey(Product)
    quantity = models.IntegerField()
    systemQuantity = models.IntegerField() #dynamic but when getting completed stocktake

    @property
    def variance(self):
        #dynamic but when getting completed stocktake
        return self.quantity - self.systemQuantity

class SalesHistory(models.Model):
    product = models.ForeignKey(Product)
    store = models.ForeignKey(Store)
    purchased = models.IntegerField(default=0)
    sold = models.IntegerField(default=0)
    year = models.IntegerField(default=0)

    month_choices = (
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    )
    month = models.CharField(max_length=10, choices=month_choices)
