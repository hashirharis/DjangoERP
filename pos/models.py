#local imports
from users.models import Staff, Store, StoreLevelObject
from core.models import Product
#django imports
from django.db import models
from django.db.models import Sum
from django.conf import settings
#python imports
from decimal import Decimal as D

class LedgerAccount(models.Model): #for store/customer accounts
    creditLimit = models.DecimalField(max_digits=8, decimal_places=2, default=D('0.00'))
    accountTypes = (
        ('customer', 'customer'),
        ('store', 'store'),
    )
    type = models.CharField(max_length=30, choices=accountTypes)

    def getCurrentEntries(self):
        return LedgerAccountEntry.objects.filter(account=self, status__exact="CURRENT") #amount owing

    def getCreditEntries(self):
        return LedgerAccountEntry.objects.filter(account=self, status__exact="CURRENT", total__lt=0.00) #amount owing

    def getAccountEntries(self):
        return LedgerAccountEntry.objects.filter(account=self, status__exact="CURRENT", total__gt=0.00) #amount owing

    def getAllHistoricEntries(self):
        return LedgerAccountEntry.objects.filter(account=self) #amount owing

    def getAccountBalance(self):
        balance = self.getCurrentEntries().aggregate(Sum('balance'))['balance__sum']
        return balance if balance is not None else D('0.00')

    def getAccountTotal(self):
        totals = self.getCurrentEntries().exclude(balance=0).aggregate(Sum('total'))
        balance = D('0.00') if totals['total__sum'] is None else totals['total__sum']
        return balance

    def remainingCreditLimit(self):
        return self.creditLimit + self.getAccountBalance()

    def getPaidToDate(self):
        return self.getAccountTotal() - self.getAccountBalance()

    def getMostRecentGroupedBy(self):
        try:
            return LedgerAccountPayment.objects.filter(account=self).order_by('-date')[:1].get().groupedBy
        except LedgerAccountPayment.DoesNotExist:
            return 0

class LedgerAccountEntry(models.Model):
    account = models.ForeignKey(LedgerAccount)
    dueDate = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    status = models.CharField(max_length=30) #CURRENT, FINALISED
    referenceID = models.PositiveIntegerField() #polymorphic foreign key to either invoice, order, sale or another ledger entry
    referenceNum = models.CharField(max_length=250)
    refTypes = (
        ('invoice', 'invoice'), #new entries created from balance paid forward
        ('sale', 'sale'), #reference to a sale
        ('entry', 'entry') #reference to another ledger entry
    )
    referenceType = models.CharField(max_length=30, choices=refTypes)
    paymentGrouping = models.PositiveIntegerField(null=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    comment = models.CharField(max_length=1000, blank=True)
    created = models.DateTimeField(auto_now_add=True, auto_created=True)

    def is_negative(self):
        return self.total < 0

    def total_sign_correct(self):
        if self.total < 0:
            return self.total * -1
        return self.total

    def balance_sign_correct(self):
        if self.balance < 0:
            return self.balance * -1
        return self.balance

    def getReferenceEntries(self):
        return LedgerAccountEntry.objects.filter(referenceType="entry", referenceID=self.id)

    def invoice(self):
        try:
            sale = Sale.objects.get(code=self.referenceNum)
            return sale.getMostRecentInvoiceItem().reference if sale.getMostRecentInvoiceItem() else ''
        except Sale.DoesNotExist:
            return ''

class Customer(StoreLevelObject):
    firstName = models.CharField("First Name", max_length=50)
    lastName = models.CharField("Last Name", max_length=50, blank=True)
    title_choices = (
        ('Mr','Mr'),
        ('Mrs','Mrs'),
        ('Ms','Ms'),
        ('Miss','Miss'),
        ('Dr','Dr')
    )
    title = models.CharField("Title", max_length=10, choices=title_choices, default='Staff', blank=True)
    #addresses
    address = models.CharField("Address", help_text="Used for Invoice", max_length=100)
    suburb = models.CharField("Suburb", max_length=20)
    state_choices=(
                   ('AU-NSW','New South Wales'),
                   ('AU-QLD','Queensland'),
                   ('AU-SA','South Australia'),
                   ('AU-TAS','Tasmania'),
                   ('AU-VIC','Victoria'),
                   ('AU-WA','Western Australia'),
                   ('AU-ACT','Australian Capital Territory'),
                   ('AU-NT','Northern Territory'),
                   )
    
    cityState = models.CharField("City/State", max_length=50,choices=state_choices)
    postcode = models.CharField("Post Code", max_length=10)
    paddress = models.CharField("Postal Address", help_text="Leave blank if same as address",max_length=100, blank=True, null=False)
    psuburb = models.CharField("Suburb", max_length=20, blank=True, null=False)
    pcityState = models.CharField("City/State", max_length=50, blank=True, null=False)
    ppostcode = models.CharField("Post Code", max_length=10, blank=True, null=False)

    email = models.CharField("Email", max_length=50, blank=True, null=False)
    homePhone = models.CharField("Home Phone", max_length=50, blank=True, null=False)
    workPhone = models.CharField("Work Phone", max_length=50, blank=True, null=False)
    fax = models.CharField("Fax", max_length=50, blank=True, null=False)
    mobile = models.CharField("Mobile", max_length=50, blank=True, null=False)
    contact_choices = (
        ('E', 'Email'),
        ('H', 'Home Phone'),
        ('W', 'Work Phone'),
        ('M', 'Mobile'),
    )
    preferredContact = models.CharField(max_length=50, choices=contact_choices, default='M')
    comment = models.TextField("Comment", blank=True, null=False)
    VCN = models.CharField("Valued Customer Number", max_length=50, null=False, blank=True)
    account = models.OneToOneField(LedgerAccount, unique=True, default=lambda: LedgerAccount.objects.create(type='customer'))

    def __unicode__(self):
        return u'%s %s' % (self.firstName, self.lastName)

    def htmlFormattedAddress(self):
        formattedAddress = u''
        if self.address != "":
            formattedAddress = u'%s %s %s %s' %(self.address+'<br />',self.suburb+'<br />',self.cityState,self.postcode)
            formattedAddress += u'<br />Home Phone : %s<br /> Work Phone : %s<br /> Mobile : %s' % (self.homePhone,self.workPhone,self.mobile)
        elif self.paddress != "":
            formattedAddress = u'%s %s %s %s' %(self.paddress+'<br />',self.psuburb+'<br />',self.pcityState,self.ppostcode)
            formattedAddress += u'<br />Home Phone : %s<br /> Work Phone : %s<br /> Mobile : %s' % (self.homePhone,self.workPhone,self.mobile)
        else:
            formattedAddress = ""
        return formattedAddress

    def firstContactPoint(self):
        firstContactPoint = ""
        if self.preferredContact == "M":
            firstContactPoint = self.mobile
        elif self.preferredContact == "E":
            firstContactPoint = self.email
        elif self.preferredContact == "H":
            firstContactPoint = self.homePhone
        elif self.preferredContact == "W":
            firstContactPoint = self.workPhone
        return firstContactPoint

class Terminal (models.Model):
    store = models.ForeignKey(Store)
    name = models.CharField(max_length=40)

    def recentActivitySet(self):
        return self.terminalactivity_set.order_by('-modified')[:10]

class Sale(models.Model):
    total = models.DecimalField(max_digits=8, decimal_places=2)
    customer = models.ForeignKey(Customer)
    deliveryAddress = models.CharField(max_length=1000)
    purchaseDate = models.DateTimeField()
    fullPaymentDate = models.DateTimeField(null=True, blank=True)
    salesPerson = models.ForeignKey(Staff)
    code = models.CharField(max_length=255)
    status = models.CharField(max_length=50) #COMPLETED, PENDING, QUOTE
    note = models.CharField(max_length=1000)
    storeNote = models.CharField(max_length=1000)
    terminal = models.ForeignKey(Terminal)
    modified = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'%i' % (self.id)

    @staticmethod
    def generateSaleNumber(terminal, store, saleId):
        return str(store.code) + str(terminal.name) + "-" + str(saleId)

    def getSalePayments(self):
        totalPayments = SalesPayment.objects.filter(sale=self).aggregate(Sum('amount'))
        return 0 if totalPayments['amount__sum'] is None else totalPayments['amount__sum']

    def getSalePaymentsTill(self, groupedByID):
        totalPayments = SalesPayment.objects.filter(sale=self, groupedBy__lt=groupedByID).aggregate(Sum('amount'))
        return 0 if totalPayments['amount__sum'] is None else totalPayments['amount__sum']

    def getSaleBalanceAfter(self, groupedByID):
        totalPayments = SalesPayment.objects.filter(sale=self, groupedBy__lt=groupedByID).aggregate(Sum('amount'))
        paid = D('0.00') if totalPayments['amount__sum'] is None else totalPayments['amount__sum']
        return self.total - paid

    def getGroupedPayments(self, groupedByID):
        return SalesPayment.objects.filter(sale=self, groupedBy=groupedByID)

    def getPayments(self):
        return SalesPayment.objects.filter(sale=self)

    def getPaymentServedBy(self, groupedByID):
        staff = SalesPayment.objects.filter(sale=self, groupedBy=groupedByID).get().receivedBy
        return staff.name

    def getMostRecentGroupedBy(self):
        try:
            return SalesPayment.objects.filter(sale=self).order_by('-date')[:1].get().groupedBy
        except SalesPayment.DoesNotExist:
            return 0

    def getMostRecentInvoice(self):
        try:
            return len(SaleInvoice.objects.filter(sale=self))
        except SaleInvoice.DoesNotExist:
            return 0

    def getMostRecentInvoiceItem(self):
        if self.getMostRecentInvoice():
            return SaleInvoice.objects.filter(sale=self).latest('created')
        else:
            return None

    def subtotal(self):
        GST = D(settings.GST)
        return self.total/GST

    def totalGST(self):
        subtotal = self.subtotal()
        GSTAmount = self.total - subtotal
        return GSTAmount

    def balanceDue(self):
        paidFor = self.getSalePayments()
        total = self.total
        return total-paidFor

class SalesLine(models.Model):
    sale = models.ForeignKey(Sale)
    item = models.ForeignKey(Product)
    modelNum = models.CharField(max_length=200)
    warrantyRef = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=200)
    quantity = models.IntegerField()
    released = models.IntegerField(default=0)
    #number of units released.
    unitPrice = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    line = models.PositiveIntegerField()

    def __unicode__(self):
        return u'Sale: %s. Line: %i' % (self.sale.code, self.line)

class PaymentMethod(StoreLevelObject):
    name = models.CharField(max_length=50)
    parentMethod = models.ForeignKey('self', blank=True, null=True, help_text="A Parent of the payment method if one exists. If this is null this is a root parent.")

    def __unicode__(self):
        return '%s' % self.name

    def getChildren(self, store):
        return PaymentMethod.objects.all().filterReadAll(store).filter(parentMethod=self)

class SalesPayment(models.Model):
    sale = models.ForeignKey(Sale)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField()
    receivedBy = models.ForeignKey(Staff)
    paymentMethod = models.ForeignKey(PaymentMethod)
    groupedBy = models.PositiveIntegerField()

    def __unicode__(self):
        return u'Payment for sale: %i' % (self.sale.id)

class SaleInvoice(models.Model):
    sale = models.ForeignKey(Sale)
    reference = models.CharField(max_length=150)
    total = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_created=True, auto_now_add=True)
    salesPerson = models.ForeignKey(Staff)
    notes = models.CharField(max_length=1000)

    @staticmethod
    def generateInvoiceNumber(terminal, store, saleId, invoiceNum):
        return str(store.code) + str(terminal.name) + "-" + str(saleId) + "-" + str(invoiceNum)

    def subtotal(self):
        GST = D(settings.GST)
        return self.total/GST

    def totalGST(self):
        subtotal = self.subtotal()
        GSTAmount = self.total - subtotal
        return GSTAmount

class SaleInvoiceLine(models.Model):
    invoice = models.ForeignKey(SaleInvoice)
    salesLine = models.ForeignKey(SalesLine)
    quantity = models.IntegerField()
    unitPrice = models.DecimalField(max_digits=8, decimal_places=2)
    price = models.DecimalField(max_digits=8, decimal_places=2)

class LedgerAccountPayment(models.Model):
    account = models.ForeignKey(LedgerAccount)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date = models.DateTimeField()
    notes = models.TextField(null=True, blank=True)
    receivedBy = models.ForeignKey(Staff)
    paymentMethod = models.ForeignKey(PaymentMethod)
    groupedBy = models.PositiveIntegerField()

    def __unicode__(self):
        return u'Payment for account: %i' % (self.account.id)

#for historical payment receipts
class LedgerAccountPaymentSnapshot(models.Model):
    account = models.ForeignKey(LedgerAccount)
    accountTotal = models.DecimalField(max_digits=8, decimal_places=2)
    paidToDate = models.DecimalField(max_digits=8, decimal_places=2)
    balanceDue = models.DecimalField(max_digits=8, decimal_places=2)
    paymentGrouping = models.PositiveIntegerField()
    balanceCarried = models.DecimalField(max_digits=8, decimal_places=2)
    created = models.DateTimeField(auto_now=True, auto_created=True)

class CreditNote(models.Model):
    customer = models.ForeignKey(Customer)
    sale = models.ForeignKey(Sale) #refund sale
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)
    payment = models.OneToOneField(LedgerAccountPayment, null=True)#if no longer active then this will need a value

class TerminalClosure(models.Model):
    startDate = models.DateTimeField()
    endDate = models.DateTimeField()
    terminal = models.ForeignKey(Terminal)
    status = models.CharField(max_length=10) #BALANCED, NOBALANCED
    total = models.DecimalField(max_digits=8,decimal_places=2)
    count = models.DecimalField(max_digits=8,decimal_places=2)
    difference = models.DecimalField(max_digits=8,decimal_places=2) # negative amount indicates less, positive more
    #total payments should be the salespayment on that given date.
    comment = models.TextField("Comment", blank=True, null=False)
    closedBy = models.ForeignKey(Staff)

class TerminalCount(models.Model):
    paymentMethod = models.ForeignKey(PaymentMethod)
    total = models.DecimalField(max_digits=8,decimal_places=2)
    count = models.DecimalField(max_digits=8,decimal_places=2)
    difference = models.DecimalField(max_digits=8,decimal_places=2) # negative amount indicates less, positive more
    eod = models.ForeignKey(TerminalClosure)

class TerminalActivity(models.Model):
    terminal = models.ForeignKey(Terminal)
    sale = models.ForeignKey(Sale, null=True)
    closure = models.ForeignKey(TerminalClosure, null=True)
    created = models.DateTimeField(auto_created=True, auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u'%s' % self.text

    def text(self):
        if self.sale:
            if self.sale.status == "QUOTE":
                action = "<strong>New</strong> Quote"
                icon_class = "glyphicon glyphicon-file"
            elif self.sale.status == "COMPLETED":
                action = "<strong>Completed</strong> Sale/Order"
                icon_class = "glyphicon glyphicon-ok"
            elif self.sale.status == "PENDING":
                action = "<strong>New</strong> Sale/Order"
                icon_class = "glyphicon glyphicon-time"
            else:
                action = "<strong>Action</strong> Sale/Order"
                icon_class = "glyphicon glyphicon-question-sign"
        else: # Balanced Till
            action = "<strong>Balanced</strong> Till"
            icon_class = "glyphicon glyphicon-repeat"

        icon = '<i class="%s"></i>' % icon_class
        if self.sale:
            return u'%s %s (%s) <span> - %s</span>' % (icon, action, self.sale.code, self.sale.salesPerson.name)
        else:
            return u'%s %s <span> - %s</span>' % (icon, action, self.closure.closedBy.name)
