from django.db import models
from users.models import StoreLevelObject
from core.models import Brand

class AddressbookContact(StoreLevelObject):
    #inherits store,group,isShared
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200, blank=True)
    landline = models.CharField(max_length=200, blank=True)
    mobile = models.CharField(max_length=200, blank=True)
    email = models.CharField(max_length=200, blank=True)
    fax = models.CharField(max_length=200, blank=True)
    comment = models.CharField(max_length=200, blank=True)
    service_type = (
        ('none', 'none'),
        ('family', 'family'),
        ('staff', 'staff'),
        ('services', 'services'),
        ('delivery', 'delivery'),
        ('emergencies', 'emergencies'),
    )
    serviceType = models.CharField(max_length=20, choices=service_type, default='none')

    def __unicode__(self):
        return u'%s %s' % (self.name, self.name)

    def isContact(self):
        return True

class BrandAddressbookContact(AddressbookContact):
    #inherits store,group,isShared
    brand = models.ForeignKey(Brand)


