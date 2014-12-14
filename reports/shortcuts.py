from datetime import timedelta
from pytz import utc
from datetime import datetime
from pos.models import Sale, Terminal, SalesLine
import operator
from core.models import Product, ProductCategory
#import datetime
import xlwt
from django.db.models.query import QuerySet, ValuesQuerySet
from django.http import HttpResponse


def getSalelineObjects(self, brands, startDate, endDate, view_style, trueGP, productCategories, allSalesPerStore):
    # get SaleLine objects for each brand or category
    saleObjectsInDateRange = Sale.objects.filter(purchaseDate__range=[startDate, endDate])
    saleLineObjects = []
    if view_style == "brand":
        for brand in brands:  # get the queryset, run calculations, create dict of results
            allProductsPerBrand = Product.objects.filter(brand_id=brand.id)
            objectsInSalesLinePerBrand = SalesLine.objects.filter(item_id__in=allProductsPerBrand)
            objectsInSalesLinePerBrand = objectsInSalesLinePerBrand.filter(sale_id__in=saleObjectsInDateRange)
            objectsInSalesLinePerBrand = objectsInSalesLinePerBrand.filter(sale_id__in=allSalesPerStore)
                # start calculations on queryset
            brandHolder = calculationsOnQueryset(self, objectsInSalesLinePerBrand, brand, trueGP, view_style)
            saleLineObjects.append(brandHolder)
    else:
        for productCategory in productCategories:  # get the queryset, run calculations, create dict of results
            secondLevelCategories = ProductCategory.objects.filter(parentCategory_id=productCategory.id)
            thirdLevelCategories = ProductCategory.objects.filter(parentCategory_id__in=secondLevelCategories)
            forthLevelCategories = ProductCategory.objects.filter(parentCategory_id__in=thirdLevelCategories)
            allItemsPerLevelOneCategory = secondLevelCategories | thirdLevelCategories
            allItemsPerLevelOneCategory = allItemsPerLevelOneCategory | forthLevelCategories
            allProductsPerCategory = Product.objects.filter(category_id__in=allItemsPerLevelOneCategory)
            objectsInSalesLinePerCategory = SalesLine.objects.filter(item_id__in=allProductsPerCategory)
            objectsInSalesLinePerCategory = objectsInSalesLinePerCategory.filter(sale_id__in=saleObjectsInDateRange)
            objectsInSalesLinePerCategory = objectsInSalesLinePerCategory.filter(sale_id__in=allSalesPerStore)
                # start calculations on queryset
            productCategoryHolder = calculationsOnQueryset(self, objectsInSalesLinePerCategory, productCategory, trueGP, view_style)
            saleLineObjects.append(productCategoryHolder)
    return saleLineObjects



def setSortType(self, view_style, objects, params):
    if view_style == "brands" or "categories":
        sortTypes = self.request.GET.getlist('sortTypes') or self.request.POST.getlist('sortTypes') or []
        if not sortTypes:
            objects.sort(key=operator.itemgetter('quantity'), reverse=True)
        try:
            if sortTypes[0] == "0":
                objects.sort(key=operator.itemgetter('quantity'), reverse=True)
            elif sortTypes[0] == "1":
                objects.sort(key=operator.itemgetter('totalSalesSell'), reverse=True)
            elif sortTypes[0] == "2":
                objects.sort(key=operator.itemgetter('totalSalesNett'), reverse=True)
            elif sortTypes[0] == "3":
                objects.sort(key=operator.itemgetter('GP'), reverse=True)
            elif sortTypes[0] == "4":
                objects.sort(key=operator.itemgetter('GPPerc'), reverse=True)
            else:
                if view_style == "brand":
                    objects.sort(key=operator.itemgetter('brand'))
                else:
                    objects.sort(key=operator.itemgetter('category'))
        except IndexError:
            pass
        params['sortTypes'] = ','.join([x for x in sortTypes]) if len(sortTypes) else ''
        return objects
    else:
        return objects


def calculationsOnQueryset(self, objects, typeChoice, trueGP, view_style):
    quantityTotal = 0
    for obj in objects:
        quantityTotal += obj.quantity
    sellTotal = 0
    for obj in objects:
        sellTotal += obj.price
    nettTotal = 0
    for obj in objects:
        nettHolder = obj.price / 2
        nettTotal += nettHolder
    GP = sellTotal - nettTotal
    if len(trueGP):
        GP = sellTotal - (nettTotal + 10)
    GPPerc = "TBA"
    objHolder = {}
    if view_style == "brand":
        objHolder['brand'] = typeChoice.brand
    else:
        objHolder['category'] = typeChoice.name
    objHolder['quantity'] = quantityTotal
    objHolder['totalSalesSell'] = sellTotal
    objHolder['totalSalesNett'] = nettTotal
    objHolder['GP'] = GP
    objHolder['GPPerc'] = GPPerc
    return objHolder

def getSalesPerStoreOrHO(self):
    if self.request.store.isHead:
        allSalesPerStore = Sale.objects.all()
    else:
        terminalsPerStore = Terminal.objects.filter(store_id=self.request.store)
        allSalesPerStore = Sale.objects.filter(terminal_id__in=terminalsPerStore)
    return allSalesPerStore


def filterCategories(self, params, productCategories):
    productCategory = self.request.GET.getlist('category') or self.request.POST.getlist('category') or []
    productCategory = filter(len, productCategory)
    if len(productCategory):
        productCategoryList = [int(x) for x in productCategory]
        productCategories = productCategories.filter(id__in=productCategoryList)
    params['category'] = ','.join([x for x in productCategory]) if len(productCategory) else ''
    return productCategories




#         # get sales per store or HO
#     if self.request.store.isHead:
#         allSalesPerStore = Sale.objects.all()
#     else:
#         terminalsPerStore = Terminal.objects.filter(store_id=self.request.store)
#         allSalesPerStore = Sale.objects.filter(terminal_id__in=terminalsPerStore)
#     return allSalesPerStore

def setTrueGP(self, params):
    trueGP = self.request.GET.getlist('chkTrueGP') or self.request.POST.getlist('chkTrueGP') or []
    trueGP = filter(len, trueGP)
    params['chkTrueGP'] = ','.join([x for x in trueGP]) if len(trueGP) else ''
    if len(trueGP):
        self.context_append['isTrueGP'] = True
    return trueGP


def filterBrands(self, params, brands):
    brand = self.request.GET.getlist('brand') or self.request.POST.getlist('brand') or []
    brand = filter(len, brand)
    if len(brand):
        brandList = [int(x) for x in brand]
        brands = brands.filter(id__in=brandList)
    params['brand'] = ','.join([x for x in brand]) if len(brand) else ''
    return brands


def getStartDate(self, params):
       # get start date for report
    startDate = "2000-04-01 09:11:24.880000"  # default dates
    startDateList = self.request.GET.getlist('startDate') or self.request.POST.getlist('startDate') or []
    startDateList = filter(len, startDateList)
    if len(startDateList):
        try:
            startDate = startDateList[0]
            startDate = datetime.strptime(startDate, "%d/%m/%Y")
            startDate = startDate.replace(tzinfo=utc)
        except IndexError:
            pass
    params['startDate'] = ','.join([x for x in startDateList]) if len(startDateList) else ''
    return startDate

def get_current_path(request):
    # just a small context processor , to be used in the reports export page
    print request
    print '8888888888888888888'
    if "?" in request.get_full_path():
        return {
           'search_string': ''+request.get_full_path().split('?').pop()
         }
    else:
        return {
            'search_string': ''
        }
def getEndDate(self, params):
    endDate = "3014-04-01 09:11:24.880000"  # default dates
    endDateList = self.request.GET.getlist('endDate') or self.request.POST.getlist('endDate') or []
    endDateList = filter(len, endDateList)
    if len(endDateList):
        try:
            endDate = endDateList[0]
            endDate = datetime.strptime(endDate, "%d/%m/%Y")
            endDate = endDate.replace(tzinfo=utc)
            endDate = endDate + timedelta(days=1)
        except IndexError:
            pass
    params['endDate'] = ','.join([x for x in endDateList]) if len(endDateList) else ''
    return endDate




