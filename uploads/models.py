from django.db import models
from core.models import Product
from users.models import Staff

type_options = (
    ('writeups', 'Write-ups'),
    ('catalogue', 'Catalogue'),
    ('products', 'Products')
)


class CSVUpload(models.Model):
    csvFile = models.FileField(upload_to="csv")
    name = models.CharField(max_length=25)
    uploadType = models.CharField(max_length=10, choices=type_options)
    creationDate = models.DateTimeField(auto_now=True)
    expiryDate = models.CharField(max_length=25)
    createdBy = models.ForeignKey(Staff, null=True)
    saved = models.BooleanField(default=False)


class ProductExtras(models.Model):
    # catalogue attributes
    cataloguePrice = models.DecimalField("Catalogue Price", max_digits=8, decimal_places=2, null=True)
    priceTicketURL = models.CharField(max_length=250, null=True)
    catalogueItemComment = models.CharField(max_length=250, null=True)
    # writeup attributes
    webPrice = models.DecimalField("Web Price", max_digits=8, decimal_places=2, null=True)
    product = models.ForeignKey(Product, primary_key=True)
    barcode = models.ImageField(upload_to="barcodes", null=True)
    name = models.CharField(max_length=250, null=True)
    specifications = models.CharField(max_length=250, null=True)
    shortDesc = models.CharField(max_length=250, null=True)
    webDesc = models.CharField(max_length=250, null=True)
    manWarranty = models.CharField(max_length=250, null=True)
    writeupSubmitted = models.BooleanField(default=False)

    def product_spec_lines(self):
        return [i for i in str(self.specifications).split('<li>') if len(i.strip()) != 0]