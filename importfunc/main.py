__author__ = 'Yussuf'

from time import clock, time
from querysets import *

start = clock()
stores = Store().djangofy()
stores.exportFile(format='json', filename="store")
categories = Category().djangofy()
categories.exportFile(format='json', filename="productcategory")
brands = Brand().djangofy()
brands.exportFile(format='json', filename="brand")
postcodes = Postcode().djangofy()
postcodes.exportFile(format='json', filename="postcode")
customers = Customer().djangofy()
customers.exportFile(format='json', filename="customer")
models = Model().djangofy()
models.exportFile(format='json', filename="product")
#warranties = Warranty().djangofy()
#warranties.exportFile(format='json', filename="warranty")

elapsed = (clock() - start)
print "algorithm completed in %.2f sec" % elapsed