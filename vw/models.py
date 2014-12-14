from django.db import models

"""This model links an Invoice to a StockMovement
   It is used when the Virtual Warehouse user creates an invoice
   for the VW store which in turn auto updates the stock levels
   for the VW store                                              """

class LinkInvoiceToStockMovement(models.Model):
    manualStockMovementId = models.PositiveIntegerField()
    invoiceNumber = models.CharField(max_length=100)
