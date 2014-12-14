from django.db import models
from users.models import Store
# Create your models here.
from core.models import Product
from b2b.models import HeadOfficeInvoice , HeadOfficeInvoiceLine

STORE_CHOICES = (('G', 'Gold'),
                ('S', 'Silver'),
                ('B', 'Bronze'),)
PRODUCT_CHOICES = (('T', 'T'),
                  ('F', 'F'),)


class StoreRange(models.Model):
    store = models.ForeignKey(Store)
    rangeType = models.CharField(max_length=1, choices=STORE_CHOICES)
    month = models.CharField(max_length=20)

    class Meta:
            unique_together = (("store", "month"), )
    def __unicode__(self):
        return self.store.name
  
    
class ProductRange(models.Model):
    product = models.ForeignKey(Product)
    productRange = models.CharField(max_length=4, choices= STORE_CHOICES)
    bonus = models.CharField(max_length=4)
    guaranteed = models.BooleanField()
    month = models.CharField(max_length=20)
    def __unicode__(self):
        return self.product.model


class StoreDetail(models.Model):
    product = models.ForeignKey(Product)
    storeRange = models.ForeignKey(StoreRange)
    passed = models.CharField(max_length=1,choices = PRODUCT_CHOICES)
    month = models.CharField(max_length=20)
    bonus = models.CharField(max_length=4)
    guaranteed = models.BooleanField(default=False)

    
    


    
    

