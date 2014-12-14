#local imports
from users.models import StoreLevelObject, Staff, Store
#django imports
from django.db import models
from django.db.models import Q
from django.conf import settings
#python imports
import operator
from decimal import Decimal as D

class ProductCategory(StoreLevelObject):
    name = models.CharField(max_length=100, blank=True, null=True)
    parentCategory = models.ForeignKey('self', verbose_name="Parent Category", blank=True, null=True, help_text="A parent of the category if one exists. If this is null this is a root parent.")
    extWarrantyTypes = models.ManyToManyField('self', verbose_name="Cust Care Plan Type", related_name="warranty_type", blank=True, null=True)
    depth = models.PositiveIntegerField()


#class.objects.all.sort()

    def getExtWarrantyTypes(self):
        '''
            get the warranty types for this category otherwise just get the parent warranty type, keep looking until one of the parents has a warranty otherwise
            return empty list
        '''
        if self.extWarrantyTypes.count():
            return self.extWarrantyTypes.all()
        elif self.parentCategory:
            return self.parentCategory.getExtWarrantyTypes()
        else:
            return []

    def getChildren(self, store):
        return ProductCategory.objects.all().filterReadAll(store).filter(parentCategory=self)

    def __unicode__(self):
        return u'%s' % self.name

class ProductCategoryMarkup(models.Model):
    category = models.ForeignKey(ProductCategory)
    store = models.ForeignKey(Store)
    mif24 = models.DecimalField("24 Months Interest Free", max_digits=8, decimal_places=2, default=D('0.00'))
    mif12 = models.DecimalField("12 Months Interest Free", max_digits=8, decimal_places=2, default=D('0.00'))
    mif6 = models.DecimalField("6 Months Interest Free", max_digits=8, decimal_places=2, default=D('0.00'))
    mif3 = models.DecimalField("3 Months Interest Free", max_digits=8, decimal_places=2, default=D('0.00'))
    cash = models.DecimalField("Cash", max_digits=8, decimal_places=2, default=D('0.00'))

class ProductTag(StoreLevelObject):
    tag = models.CharField(max_length=30)
    tag_types = (
        ('Deal', 'Deal'),
        ('Brand', 'Brand'),
        ('Feature', 'Feature'),
        ('Other', 'Other')
    )
    type = models.CharField("Tag Type", max_length=10, choices=tag_types, default='Other')

    def __unicode__(self):
        return u'%s' % (self.tag)

'''
Supplier and Brand are synonymous exactly like in SPAN.
'''
class Brand(StoreLevelObject):
    brand = models.CharField("Brand", max_length=100)
    purchaser = models.CharField("Purchaser", max_length=100) #Individual or Head Office
    address = models.TextField("Address", blank=True, null=True)
    suburb = models.CharField("Suburb", max_length=100, blank=True, null=True)
    cityState = models.CharField("City/State", max_length=50, blank=True, null=True)
    postcode = models.CharField("Post Code", max_length=10, blank=True, null=True)
    paddress = models.TextField("Postal Address", blank=True, null=True)
    pcityState = models.CharField("Postal City/State", max_length=50, blank=True, null=True)
    ppostcode = models.CharField("Postal Post Code", max_length=10, blank=True, null=True)
    phone = models.CharField("Phone", max_length=50, blank=True, null=True)
    fax = models.CharField("Fax", max_length=50, blank=True, null=True)
    email = models.EmailField("Email", max_length=150, blank=True, null=True)
    repName = models.CharField("Account Manager", max_length=100, blank=True, null=True)
    distributor = models.CharField("Distributor", max_length=100)
    repPhone = models.CharField("Rep Phone", max_length=50, blank=True, null=True)
    ABN = models.CharField("Distributor ABN", max_length=100, blank=True, null=True)
    comments = models.TextField("Comments", blank=True, default="")
    hasElectronicTrading = models.BooleanField("Electronic Trading", default=False)
    GLN = models.CharField(max_length=250, blank=True, default="")
    isHOPreferred = models.BooleanField("Head Office Preferred", default=False)
    isInGFK = models.BooleanField("Include in GFK report", default=False)
    rebate = models.DecimalField("HO Rebate", max_digits=8, decimal_places=2)
    actualRebate = models.DecimalField("Supplier Rebate", max_digits=8, decimal_places=2)

    def __unicode__(self):
        return u'%s' % self.brand

    @staticmethod
    def getUniqueDistributors():
        return [{'name': brand.get('distributor')} for brand in Brand.objects.values('distributor').distinct()]

    @staticmethod
    def getUniquePurchasers():
        purchasers = []
        for brand in Brand.objects.values('purchaser').distinct():
            purchasers.append(brand.get('purchaser'))
        return purchasers

class Product(StoreLevelObject):
    #inherits store,group,isShared
    tags = models.ManyToManyField(ProductTag, blank=True)
    tags.help_text = ''
    product_status = (
        ('current', 'current'),
        ('superceded', 'superceded'),
        ('obsolete', 'obsolete'),
    )
    status = models.CharField(max_length=20, choices=product_status, default='current')
    model = models.CharField(max_length=250)
    category = models.ForeignKey(ProductCategory)
    brand = models.ForeignKey(Brand)
    EAN = models.CharField(max_length=100)
    packSize = models.PositiveIntegerField("Pack Size", default=1)
    costPrice = models.DecimalField("Cost Price", max_digits=8, decimal_places=2)
    tradePrice = models.DecimalField("Trade Price", max_digits=8, decimal_places=2)
    goPrice = models.DecimalField("Suggested Sell", max_digits=8, decimal_places=2)
    spanNet = models.DecimalField("SPAN Net", max_digits=8, decimal_places=2)
    isCore = models.BooleanField("Core stock", default=False)
    isGSTExempt = models.BooleanField("GST Exempt", default=False)
    description = models.TextField()
    manWarranty = models.CharField("Man. Warranty", max_length=250, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        unique_together = ('EAN', 'model')

    def __unicode__(self):
        return u'%s %s' % (self.model, self.description)

    def getCurrentModelDiscount(self): #Off Invoice
        totalOffInvoice = D('0.00')
        for offInvoice in Deal.objects.filter(type="OI", percent=False, product=self, active=1):
                totalOffInvoice += offInvoice.amount
        return totalOffInvoice

    def getCurrentClassVendorBonus(self):
        totalVendorBonus = D('0.00')
        bonuses = ClassVendorBonus.objects.filter(brand=self.brand, active=1)
        categorySearch = [Q(type=self.category), Q(type=self.category.parentCategory)]
        if self.category.parentCategory.parentCategory:
            categorySearch.append(Q(type=self.category.parentCategory.parentCategory))
            if self.category.parentCategory.parentCategory.parentCategory:
                categorySearch.append(Q(type=self.category.parentCategory.parentCategory.parentCategory))
        bonuses = bonuses.filter(reduce(operator.or_, categorySearch))
        for vendorBonus in bonuses:
            totalVendorBonus += vendorBonus.amount
        return totalVendorBonus

    def getCurrentDollarBonus(self):
        totalDollarBonus = D('0.00')
        for dollarBonus in Deal.objects.filter(type="MB", percent=False, product=self, active=1):
            totalDollarBonus += dollarBonus.amount
        return totalDollarBonus

    def getCurrentPercentBonus(self):
        totalPercentBonus = D('0.00')
        for percentBonus in Deal.objects.filter(type="MB", percent=True, product=self, active=1):
            totalPercentBonus += percentBonus.amount
        return totalPercentBonus

    '''
    This calculates SpanNET from the off invoice price for
    '''
    def calculateSPANNet(self, offInvoice):
        one = D('1.00')
        hundred = D('100.00')
        GSTInclusive = D(settings.GST)
        self.costPrice = offInvoice
        self.spanNet = (self.costPrice * (one-(self.getCurrentClassVendorBonus()/hundred)) - self.getCurrentDollarBonus()) * (one-(self.getCurrentPercentBonus()/hundred)) * (one-self.brand.rebate/hundred)
        return self.spanNet * GSTInclusive

    def spanNetPlusGST(self):
        GSTInclusive = D(settings.GST)
        return self.updateCurrentSPANNet() * GSTInclusive

    def updateCurrentSPANNet(self):
        #see SPANNET calculations. this also calls updateCostPrice().
        one = D('1.00')
        hundred = D('100.00')
        self.costPrice = self.tradePrice - self.getCurrentModelDiscount()
        self.spanNet = (self.costPrice * (one-(self.getCurrentClassVendorBonus()/hundred)) - self.getCurrentDollarBonus()) * (one-(self.getCurrentPercentBonus()/hundred)) * (one-self.brand.rebate/hundred)
        self.save()
        ProductHistoricalPricing.createHistory(self)
        return self.spanNet

    def getStockCounts(self, store):
        from stock.models import StoreInventory
        return StoreInventory.objects.get_or_create(store=store, product=self)[0].updateAll()

    def getNSBICount(self, store):
        from stock.models import StoreInventoryItem
        return StoreInventoryItem.objects.filter(inventory=self.getStockCounts(store), movementIn__isnull=True).count()

    '''
    This function removes or adds to this product for a specific stores inventory and handles all the movements, adding inventory items etc.
    @store          is the store inventory to add to
    @difference     is the amount to add or subtract to the inventory.
    @reference      is the reference, invoice, sale, stocktake etc.
    @referenceType  is the referenceType as above in plain text
    @purchaseNet    is the price the goods were purchased for if @difference is positive.
    @serials        are the serial numbers to change movements for, if this is blank then new movements are created for products without serials attached.
    '''
    def deltaStockCounts(self, store, difference, reference=None, referenceType=None, purchaseNet=None, serials=None):
        from stock.models import StoreInventoryItemMovement
        count = self.getStockCounts(store)
        serials = [] if serials is None else serials
        adjustedDifference = difference * -1 if difference < 0 else difference #positive int for ranging
        movement = StoreInventoryItemMovement.movementFromReference(reference, referenceType)

        for x in range(0, adjustedDifference):
            #add/remove stock inventory items
            if x < len(serials) and len(serials[x].strip()): #exists and is not blank string.
                serial = serials[x]
            else:
                serial = None
            self.AddOrRemoveStoreInventoryItem(count, movement, add=difference<=0, serial=serial, purchaseNet=purchaseNet)

        #after all is well and good we can deduct the movements
        count.level = count.level - difference
        count.save()
        count.updateAll()

    #pass in a serial if you want to remove a specific
    def AddOrRemoveStoreInventoryItem(self, count, movement, add=True, serial=None, purchaseNet=None):
        from stock.models import StoreInventoryItem
        movement.pk = None
        movement.save()
        filters = {'inventory': count}
        if add:
            filters['movementIn__isnull'] = True
        else:
            filters['movementOut__isnull'] = True
        if serial:
            filters['serial'] = serial
        else:
            filters['serial__isnull'] = True
        try:
            item, created = StoreInventoryItem.objects.get_or_create(**filters)
        except StoreInventoryItem.MultipleObjectsReturned:
            item = StoreInventoryItem.objects.filter(**filters).order_by('pk')[0]
        if add:
            item.purchaseNet = purchaseNet if purchaseNet else 0.00
            item.movementIn = movement
        else:
            item.movementOut = movement
        item.save()
        return item

    def getPriceAtDate(self, date, priceType="SPAN"):
        """
        get price at a certain point in time. will return nothing if no price history exists at that date.
        @param date:        python date when to query for, gets the latest price before this date.
        @param priceType:   price type of the pricing history, see ProductHistoricalPricing model for more information
        """
        return ProductHistoricalPricing.objects.all().filter(created__lte=date, priceType=priceType).latest('created').price

class ProductHistoricalPricing(models.Model):
    price_type_choices = (
        ('SPAN', 'Span Net Price'), #apply whole pricing structure
        ('COST', 'Cost Price'), #subtract model discounts
        ('TRADE', 'Trade Price')
    )
    product = models.ForeignKey(Product)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True, auto_created=True)
    priceType = models.CharField(max_length=100, choices=price_type_choices, default='SPAN')

    @staticmethod
    def createHistory(product):
        spanPrice = ProductHistoricalPricing(product=product, priceType="SPAN", price=product.spanNet)
        spanPrice.save()
        costPrice = ProductHistoricalPricing(product=product, priceType="COST", price=product.costPrice)
        costPrice.save()
        tradePrice = ProductHistoricalPricing(product=product, priceType="TRADE", price=product.tradePrice)
        tradePrice.save()

class Warranty(Product):
    startValue = models.DecimalField("Start Cost", max_digits=8, decimal_places=2)
    endValue = models.DecimalField("End Cost", max_digits=8, decimal_places=2)

class Deal(models.Model):
    types = (
        ('OI', 'Model Discount'), #Off Invoice/Model Discount
        ('MB', 'Model Bonus'), #Model Bonus
        #('PB', 'Percent Bonus'), #Percent Bonus
        ('ST', 'Sell Through')  #Sell Through
    )
    product = models.ForeignKey(Product)
    type = models.CharField(max_length=100, choices=types, default='Model Discount')
    startDate = models.DateTimeField("Start Date", null=True, blank=True)
    endDate = models.DateTimeField("End Date", null=True, blank=True)
    active = models.BooleanField(default=False)
    comments = models.TextField()
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    percent = models.BooleanField(default=False) #can be either fixed or percent
    #for sell throughs
    claimFromChoices = (
        ('HO', 'HO'),
        ('Supplier', 'Supplier'),
    )
    claimFrom = models.CharField("Claim From", max_length=20, choices=claimFromChoices, blank=True, null=True, help_text="<br>If the deal is sell through this must be filled")
    createdBy = models.ForeignKey(Staff)
    createdOn = models.DateTimeField(auto_now_add=True)

    def get_verbose_type(self):
        return dict(self.types)[self.type]

class ClassVendorBonus(models.Model):
    type = models.ForeignKey(ProductCategory)
    brand = models.ForeignKey(Brand)
    amount = models.DecimalField("Amount %", max_digits=8, decimal_places=2)
    startDate = models.DateTimeField("Start Date", null=True, blank=True)
    endDate = models.DateTimeField("End Date", null=True, blank=True)
    active = models.BooleanField(default=False)
    comments = models.TextField()
    createdBy = models.ForeignKey(Staff)
    createdOn = models.DateTimeField(auto_now_add=True)

class Postcode(models.Model):
    code = models.CharField(max_length=10)
    locality = models.CharField(max_length=250)
    state = models.CharField(max_length=50)
    deliveryOffice = models.CharField(max_length=50)

    # def __unicode__(self):
    #     return u'%s | %s | %i' % (self.store.name, self.product.name, self.level)
