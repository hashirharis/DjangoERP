from django.db.models.signals import post_save
from pos.models import SalesPayment, LedgerAccountEntry, CreditNote
from django.conf import settings

def SalesPaymentAdded(sender, **kwargs): #for creating ledger entries
    if kwargs['created']:
        accountsParent = settings.ACCOUNTS_ID #Accounts Payment Method
        creditMethod = settings.CREDIT_ID
        salesPayment = kwargs['instance']
        if salesPayment.paymentMethod.parentMethod is not None and salesPayment.paymentMethod.parentMethod.id == accountsParent:
            sale = salesPayment.sale
            ledgerAccount = sale.customer.account
            ledgerEntry = LedgerAccountEntry(
                account=ledgerAccount,
                status="CURRENT",
                referenceID=sale.id,
                referenceNum=sale.code,
                referenceType='sale',
                balance=salesPayment.amount,
                total=salesPayment.amount,
                description=salesPayment.paymentMethod.name,
                comment=sale.storeNote,
            ) #fix up the due date based on x Day Account
            ledgerEntry.save()
        if salesPayment.paymentMethod.id == creditMethod: #create a credit note !
            sale = salesPayment.sale
            customer = sale.customer
            note = CreditNote( #defaults to active
                sale=sale,
                customer=customer,
                amount=salesPayment.amount
            )
            note.save()
post_save.connect(SalesPaymentAdded, sender=SalesPayment)