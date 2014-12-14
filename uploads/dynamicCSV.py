import csv
import models
from dateutil.parser import *
from uploads.models import CSVUpload
from core.models import ProductCategory, Brand
from core.models import Product
from uploads.models import ProductExtras
from django.shortcuts import get_object_or_404
from users.models import StoreGroup
from users.models import Store
from django.core.mail import send_mail


class DTOFactory(object):

    def __init__(self):
        pass

    class Row:
        pass

    def getValidationRowsFromCSVFile(self, csvFile, uploadType):
        open(csvFile, "rb")
        f = open(csvFile, "rb")
        csvRows = csv.DictReader(f)
        counter = 0
        for row in csvRows:
            counter += 1
            if counter == 1:  # first row validation/metadata
                rowObject = self.Row()
                rowObject.headers = row.keys()
                for key, value in row.iteritems():
                    if key is not None:
                        setattr(rowObject, key, value)
                        if key == "metadata":
                            if not value in ['products', 'catalogue', 'writeups']:
                                return {'errorType': 'invalidFirstLine', 'errorRow': 0}
                        if uploadType == "catalogue":
                            if key == "start_date":
                                try:
                                    parse(value)
                                except ValueError:
                                    return {'errorType': 'invalidStartDateFormat', 'errorRow': 0}
                            if key == "end_date":
                                try:
                                    parse(value)
                                except ValueError:
                                    return {'errorType': 'invalidEndDateFormat', 'errorRow': 0}
            if not counter == 1:  # other rows validation
                rowObject = self.Row()
                rowObject.headers = row.keys()
                for key, value in row.iteritems():
                    if key is not None:
                        setattr(rowObject, key, value)
                        if uploadType == "catalogue":
                            if key == "price":
                                value = value.replace(".", "", 1)
                                if not value.isdigit():
                                    return {'errorType': 'invalidCatPrice', 'errorRow': counter+1}
                            if key == "model":
                                try:
                                    Product.objects.get(model=str(value))
                                except Product.DoesNotExist:
                                    return {'errorType': 'invalidCatModelDoesNotExist', 'errorRow': counter+1}
                        if uploadType == "products":
                            if key == "model":
                                if not len(value):
                                    return {'errorType': 'invalidModelIsNull', 'errorRow': counter+1}
                            if key == "category":
                                if not len(value):
                                    return {'errorType': 'invalidCategoryIsNull', 'errorRow': counter+1}
                            if key == "tradePrice":
                                if not len(value):
                                    return {'errorType': 'invalidTradePriceIsNull', 'errorRow': counter+1}
                            if key == "EAN":
                                if not len(value):
                                    return {'errorType': 'invalidEANIsNull', 'errorRow': counter+1}
                        if uploadType == "writeups":
                            if key == "model":
                                try:
                                    Product.objects.get(model=str(value))
                                except Product.DoesNotExist:
                                    return {'errorType': 'invalidWriteupModelDoesNotExist', 'errorRow': counter+1}
                            if key == "name":
                                if not len(value):
                                    return {'errorType': 'invalidNameIsNull', 'errorRow': counter+1}
                            if key == "short_description":
                                if not len(value):
                                    return {'errorType': 'invalidShortDescIsNull', 'errorRow': counter+1}
                            if key == "web_description":
                                if not len(value):
                                    return {'errorType': 'invalidWebDescIsNull', 'errorRow': counter+1}
                            if key == "product_specifications":
                                if not len(value):
                                    return {'errorType': 'invalidProdSpecIsNull', 'errorRow': counter+1}
                            if key == "man_warranty":
                                if not len(value):
                                    return {'errorType': 'invalidManWarrIsNull', 'errorRow': counter+1}
        return {'errorType': 'passed', 'errorRow': 0}

    def getRowsFromCSVFile(self, csvFile):
        DTO = []
        open(csvFile, "rb")
        f = open(csvFile, "rb")
        csvRows = csv.DictReader(f)
        counter = 0
        for row in csvRows:
            counter += 1
            if not counter == 1:
                rowObject = self.Row()
                rowObject.headers = row.keys()
                for key, value in row.iteritems():
                    if key is not None:
                        setattr(rowObject, key, value)
                        if key == "model":
                            product = Product.objects.filter(model=value)
                            try:
                                productId = product[0].id
                                setattr(rowObject, "id", productId)
                                setattr(rowObject, "status", "current")
                                setattr(rowObject, "descriptionEdited", False)
                            except IndexError:
                                setattr(rowObject, "id", 1)
                                setattr(rowObject, "status", "current")
                                setattr(rowObject, "descriptionEdited", False)
                DTO.append(rowObject)
        return DTO

    def getFirstRowFromCSVFile(self, csvFile):
        DTO = []
        open(csvFile, "rb")
        f = open(csvFile, "rb")
        csvRows = csv.DictReader(f)
        counter = 0
        for row in csvRows:
            counter += 1
            if counter == 1:
                rowObject = self.Row()
                rowObject.headers = row.keys()
                for key, value in row.iteritems():
                    if key is not None:
                        setattr(rowObject, key, value)
                DTO.append(rowObject)
        return DTO


def validateProducts(pk, uploadType, rowsFromUpload, firstRowFromUpload, context):
    context['pk'] = pk
    result = getValidationRowsFromUpload(pk, uploadType)
    # rowsFromUpload = getRowsFromUpload(pk)
    # firstRowFromUpload = getFirstRowFromUpload(pk)
    if result['errorType'] == "invalidFirstLine":
        context['invalidFirstLine'] = True
        return False
    if result['errorType'] == "invalidModelIsNull":
        context['invalidModelIsNull'] = True
        context['invalidModelIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidCategoryIsNull":
        context['invalidCategoryIsNull'] = True
        context['invalidCategoryIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidTradePriceIsNull":
        context['invalidTradePriceIsNull'] = True
        context['invalidTradePriceIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidEANIsNull":
        context['invalidEANIsNull'] = True
        context['invalidEANisNullRow'] = result['errorRow']
        return False
    else:
        if doProductsValidation(pk, uploadType, rowsFromUpload, firstRowFromUpload, context):
            addContext(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
            return True
        else:
            return False


def validateCatalogue(pk, uploadType, rowsFromUpload, firstRowFromUpload, context):
    context['pk'] = pk
    result = getValidationRowsFromUpload(pk, uploadType)
    # rowsFromUpload = getRowsFromUpload(pk)
    # firstRowFromUpload = getFirstRowFromUpload(pk)
    if result['errorType'] == "invalidFirstLine":
        context['invalidFirstLine'] = True
        return False
    if result['errorType'] == "invalidStartDateFormat":
        context['invalidStartDateFormat'] = True
        return False
    if result['errorType'] == "invalidEndDateFormat":
        context['invalidEndDateFormat'] = True
        return False
    if result['errorType'] == "invalidCatPrice":
        context['invalidCatPrice'] = True
        context['invalidCatPriceRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidCatModelDoesNotExist":
        context['invalidCatModelDoesNotExist'] = True
        context['invalidCatModelDoesNotExistRow'] = result['errorRow']
        return False
    else:
        addContext(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
        return True


def validateWriteup(pk, uploadType, rowsFromUpload, firstRowFromUpload, context):
    context['pk'] = pk
    result = getValidationRowsFromUpload(pk, uploadType)
    # rowsFromUpload = getRowsFromUpload(pk)
    # firstRowFromUpload = getFirstRowFromUpload(pk)
    if result['errorType'] == "invalidFirstLine":
        context['invalidFirstLine'] = True
        return False
    if result['errorType'] == "invalidWriteupModelDoesNotExist":
        context['invalidWriteupModelDoesNotExist'] = True
        context['invalidWriteupModelDoesNotExistRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidNameIsNull":
        context['invalidNameIsNull'] = True
        context['invalidNameIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidShortDescIsNull":
        context['invalidShortDescIsNull'] = True
        context['invalidShortDescIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidWebDescIsNull":
        context['invalidWebDescIsNull'] = True
        context['invalidWebDescIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidProdSpecIsNull":
        context['invalidProdSpecIsNull'] = True
        context['invalidProdSpecIsNullRow'] = result['errorRow']
        return False
    if result['errorType'] == "invalidManWarrIsNull":
        context['invalidManWarrIsNull'] = True
        context['invalidManWarrIsNullRow'] = result['errorRow']
        return False
    else:
        addContext(pk, uploadType, rowsFromUpload, firstRowFromUpload, context)
        return True


def writeToDB(store, uploadId, context, doNotSupersedeList, uploadType, listPendingSuperseding, rowsFromUpload, firstRowFromUpload):
    if uploadType.lower() == "writeups" or uploadType.lower() == "catalogue":
        writeRowsToDB(store, rowsFromUpload, firstRowFromUpload, uploadType, uploadId, doNotSupersedeList=[], listPendingSuperseding=[])
    if getTypeFromUpload(uploadId).lower() == "products":
        return doEANValidationThenWriteOrFail(store, rowsFromUpload, firstRowFromUpload, context, uploadType, doNotSupersedeList, listPendingSuperseding, uploadId)
    return True


def writeRowsToDB(store, rowsFromUpload, firstRowFromUpload, uploadType, uploadId, doNotSupersedeList, listPendingSuperseding):
    if uploadType == "writeups":
        addWriteup(rowsFromUpload)
    elif uploadType == "catalogue":
        addCatalogue(rowsFromUpload)
    elif uploadType == "products":
        addProducts(store, rowsFromUpload, firstRowFromUpload, doNotSupersedeList, listPendingSuperseding, uploadId)


def doEANValidationThenWriteOrFail(store, rowsFromUpload, firstRowFromUpload, context, uploadType, doNotSupersedeList, listPendingSuperseding, uploadId):
    if getEANErrorStatusForBlanks(rowsFromUpload, context) and getEANErrorStatusForAlreadyExists(rowsFromUpload, context):
        writeRowsToDB(store, rowsFromUpload, firstRowFromUpload, uploadType, uploadId, doNotSupersedeList, listPendingSuperseding)
        return True
    else:
        return False


def doValidation(rowsFromUpload, firstRowFromUpload, context):
    valid = True
    loopCounter = 0

    for row in firstRowFromUpload:
        loopCounter += 1
        if loopCounter == 1:
           # brand - must be a number
            brands = Brand.objects.all()
            numberOfBrands = brands.count()
            productCategories = ProductCategory.objects.all()
            numberOfCategories = productCategories.count()
            try:
                brand = int(row.brand)
                if brand > numberOfBrands or brand < 1 or not row.brand.isdigit():
                    context["invalidBrand"] = True
                    return False
            except ValueError:
                context["invalidBrand"] = True
                return False
    for row in rowsFromUpload:
        #tradePrice - must be digit
        tradePrice = row.tradePrice.replace(".", "", 1)
        if not tradePrice.isdigit():
            context["invalidTradePrice"] = True
            return False
        # goPrice - must be digit
        goPrice = row.goPrice.replace(".", "", 1)
        if not goPrice.isdigit():
            if len(goPrice):
                context["invalidGoPrice"] = True
                return False
        # suggestedSell - digit
        suggestedSell = row.suggestedSell.replace(".", "", 1)
        if not suggestedSell.isdigit():
            context["invalidSuggestedSell"] = True
            return False
        # category - must be a number
        try:
            category = int(row.category)
            if category > numberOfCategories or category < 1 or not row.category.isdigit():
                context["invalidCategory"] = True
                context["invalidCategoryMax"] = numberOfCategories

                return False
        except ValueError:
            context["invalidCategory"] = True
            return False
        # packSize - digit
        try:
            packSize = int(row.packSize)
            if packSize < 1:
                context["invalidPackSize"] = True
                return False
        except ValueError:
            context["invalidPackSize"] = True
            return False
        # isCore - true or false
        if row.isCore.lower() == "true" or row.isCore.lower() == "false":
            pass
        else:
            context["invalidIsCore"] = True
            return False
    return valid


def appendBeforeBlankRow(uploadBrand, product, EANErrorProductsList):
    row = {}
    row['model'] = str(product.model)
    row['brand'] = uploadBrand
    row['category'] = product.category.id
    row['tradePrice'] = product.tradePrice
    row['description'] = product.description
    row['goPrice'] = product.goPrice
    row['suggestedSell'] = product.goPrice
    row['packSize'] = product.packSize
    row['isCore'] = product.isCore
    row['manWarranty'] = product.manWarranty
    row['EAN'] = product.EAN
    row['status'] = product.status
    row['isBefore'] = True
    row['id'] = product.id
    EANErrorProductsList.append(row)


def editExistingProduct(row):
    category = get_object_or_404(ProductCategory, pk=row.category)
    product = Product.objects.get(id=row.id)
    product.category = category
    product.tradePrice = row.tradePrice
    product.description = row.description
    product.goPrice = row.goPrice
    product.packSize = row.packSize
    product.manWarranty = row.manWarranty
    product.EAN = row.EAN
    product.status = "current"
    if row.isCore.lower() == 'false':
        product.isCore = 0
    if row.isCore.lower() == 'true':
        product.isCore = 1
    product.save()


def assignProducts(context, uploadId, rowsFromUpload, firstRowFromUpload):
    listAdded = []
    listEdited = []
    listNoChanges = []
    listPendingSuperseding = []
    listResurrected = []
    listConfused = []
    uploadBrand = getUploadBrand(firstRowFromUpload)
    for row in rowsFromUpload:
        if models.Product.objects.filter(model=str(row.model)).exists():
            products = models.Product.objects.filter(model=str(row.model))
            for product in products:
                if str(product.brand.id) == str(uploadBrand):
                    listNoChanges = showResultsForNoChanges(uploadBrand, row, listNoChanges)
                    addBeforeEditedItem(row, listEdited, uploadBrand, listNoChanges)
                    listEdited = showResultsForEdited(uploadBrand, row, listEdited)
        else:
            if eanAlreadyExists(row):
                showResultsForConfused(row, listConfused)
                addMatchingConfusedItem(context, row, listConfused, uploadBrand)
            else:
                listAdded = showResultsForAdded(row, listAdded)
        listResurrected = showResultsForResurrected(uploadBrand, row, listResurrected)
    listPendingSuperseding = showResultsForSupersede(uploadBrand, listPendingSuperseding, rowsFromUpload)
    context['listEdited'] = listEdited
    context['listAdded'] = listAdded
    context['listNoChanges'] = listNoChanges
    context['listPendingSuperseding'] = listPendingSuperseding
    context['listResurrected'] = listResurrected


def appendEditedRow(uploadBrand, product, listEdited):
    row = {}
    row['model'] = str(product.model)
    row['brand'] = uploadBrand
    row['category'] = product.category.id
    row['tradePrice'] = product.tradePrice
    row['description'] = product.description
    row['goPrice'] = product.goPrice
    row['suggestedSell'] = product.goPrice
    row['packSize'] = product.packSize
    row['isCore'] = product.isCore
    row['manWarranty'] = product.manWarranty
    row['EAN'] = product.EAN
    row['status'] = product.status
    row['isBefore'] = True
    row['id'] = product.id
    listEdited.append(row)


def modelAndBrandAlreadyExist(row, product):
    return models.Product.objects.filter(model=str(row.model)).exists() and str(product.brand.id) == str(row.brand)


def eanAlreadyExists(row):
    return models.Product.objects.filter(EAN=str(row.EAN)).exists()


def doProductsValidation(uploadId, uploadType, rowsFromUpload, firstRowFromUpload, context):
    try:
        CSVUpload.objects.get(id=uploadId)
        if uploadType == "products":
            EANAlreadyExistsProducts = getEANAlreadyExistsProducts(context, uploadId, rowsFromUpload, firstRowFromUpload)
            blankEANS = getListOfBlankEANS(uploadId, rowsFromUpload, firstRowFromUpload, context)
            validation = doValidation(rowsFromUpload, firstRowFromUpload, context)
            EANErrorStatusForBlanks = getEANErrorStatusForBlanks(rowsFromUpload, context)
            EANErrorStatusForAlreadyExists = getEANErrorStatusForAlreadyExists(rowsFromUpload, context)
            if EANAlreadyExistsProducts or blankEANS:
                return False
            if not validation or not EANErrorStatusForBlanks or not EANErrorStatusForAlreadyExists:
                return False
            return True
    except CSVUpload.DoesNotExist:
        pass


def sendConfirmationEmail(uploadType):
    if uploadType.lower() == 'products':
        emailMsg = "A new products bulk upload has been added, please review the upload below."
        send_mail('Products Upload', emailMsg, 'adee.macdowell@gmail.com',
            ['adee.macdowell@gmail.com'], fail_silently=False)



def showResultsForResurrected(uploadBrand, row, listResurrected):
    productRelatingToNewRow = getProductRelatingToNewRow(uploadBrand, row)
    if not productRelatingToNewRow == 0:
        if not productRelatingToNewRow.status == "current":
            row.status = productRelatingToNewRow.status
            listResurrected.append(row)
    return listResurrected


def showResultsForSupersede(uploadBrand, listPendingSuperseding, rowsFromUpload):
    allProductsFromBrand = getAllProductsFromBrand(uploadBrand)
    if allProductsFromBrand:
        allProductsFromBrand = allProductsFromBrand.exclude(status="superceded")
        allProductsFromBrand = allProductsFromBrand.exclude(status="obsolete")
        for row in rowsFromUpload:
            allProductsFromBrand = allProductsFromBrand.exclude(model=row.model)
        for i in allProductsFromBrand:
            row = {}
            row['model'] = str(i.model)
            row['category'] = i.category.id
            row['tradePrice'] = i.tradePrice
            row['description'] = i.description
            row['goPrice'] = i.goPrice
            row['suggestedSell'] = i.goPrice
            row['packSize'] = i.packSize
            row['isCore'] = i.isCore
            row['manWarranty'] = i.manWarranty
            row['EAN'] = i.EAN
            row['status'] = "current"
            row['id'] = i.id
            listPendingSuperseding.append(row)
    else:
        pass
    return listPendingSuperseding


def showResultsForAdded(row, listAdded):
    listAdded.append(row)
    return listAdded


def showResultsForConfused(rowFromCaller, listConfused):
    listConfused.append(rowFromCaller)


def showResultsForEdited(uploadBrand, row, listEdited):
    edited = False
    try:
        product = Product.objects.filter(brand=uploadBrand)
        product = product.filter(model=row.model)
        if product:
            product = product[0]
            if not str(row.model) == str(product.model):
                edited = True
                row.modelEdited = True
            if not str(uploadBrand) == str(product.brand.id):
                edited = True
                row.brandEdited = True
            if not str(row.category) == str(product.category.id):
                edited = True
                row.categoryEdited = True
            if not str(row.tradePrice) == str(product.tradePrice):
                edited = True
                row.tradePriceEdited = True
            if not str(row.description) == str(product.description):
                edited = True
                row.descriptionEdited = True
            if not str(row.goPrice) == str(product.goPrice):
                edited = True
                row.goPriceEdited = True
            if not str(row.suggestedSell) == str(product.goPrice):
                edited = True
                row.suggestedSellEdited = True
            if not str(row.packSize) == str(product.packSize):
                edited = True
                row.packSizeEdited = True
            if not str(row.isCore).lower() == str(product.isCore).lower():
                edited = True
                row.isCoreEdited = True
            if not str(row.manWarranty) == str(product.manWarranty):
                edited = True
                row.manWarrantyEdited = True
            if not str(row.EAN) == str(product.EAN):
                edited = True
                row.EANEdited = True
            if edited:
                row.statusEdited = True
                listEdited.append(row)
    except Product.DoesNotExist:
        pass
    return listEdited


def showResultsForNoChanges(uploadBrand, row, listNoChanges):
    noChanges = True
    try:
        product = Product.objects.filter(brand=uploadBrand)
        product = product.filter(model=row.model)
        if product:
            product = product[0]
            if not str(row.model) == str(product.model):
                noChanges = False
            if not str(uploadBrand) == str(product.brand.id):
                noChanges = False
            if not str(row.category) == str(product.category.id):
                noChanges = False
            if not str(row.tradePrice) == str(product.tradePrice):
                noChanges = False
            if not str(row.description) == str(product.description):
                noChanges = False
            if not str(row.goPrice) == str(product.goPrice):
                noChanges = False
            if not str(row.suggestedSell) == str(product.goPrice):
                noChanges = False
            if not str(row.packSize) == str(product.packSize):
                noChanges = False
            if not str(row.isCore).lower() == str(product.isCore).lower():
                noChanges = False
            if not str(row.manWarranty) == str(product.manWarranty):
                noChanges = False
            if not str(row.EAN) == str(product.EAN):
                noChanges = False
            if noChanges:
                listNoChanges.append(row)
    except Product.DoesNotExist:
        pass
    return listNoChanges


def addWriteup(rowsFromUpload):
    for row in rowsFromUpload:
        try:
            product = Product.objects.get(model=str(row.model))
            productExtras = ProductExtras.objects.get_or_create(product=product)
            productExtras[0].webDesc = row.web_description
            productExtras[0].webPrice = row.web_price
            productExtras[0].name = row.name
            productExtras[0].shortDesc = row.short_description
            productExtras[0].specifications = row.product_specifications
            productExtras[0].barcode = ""
            productExtras[0].manWarranty = row.man_warranty
            productExtras[0].writeupSubmitted = 1
            productExtras[0].save()
        except Product.DoesNotExist:
            pass


def addCatalogue(rowsFromUpload):
    for row in rowsFromUpload:
        try:
            product = Product.objects.get(model=str(row.model))
            productExtras = ProductExtras.objects.get_or_create(product=product)
            productExtras[0].cataloguePrice = row.price
            productExtras[0].priceTicketURL = row.price_ticket_image_URL
            productExtras[0].catalogueItemComment = row.comment
            productExtras[0].save()
        except Product.DoesNotExist:
            pass


def addProducts(store, rowsFromUpload, firstRowFromUpload, doNotSupersedeList, listPendingSuperseding, uploadId):
    brand = getUploadBrand(firstRowFromUpload)
    for row in rowsFromUpload:
        if models.Product.objects.filter(model=str(row.model)).exists():
            editExistingProduct(row)
        else:
            addNewProduct(store, row, brand)
    setSupersededProducts(listPendingSuperseding, doNotSupersedeList)
    setUploadSaved(uploadId)


def addNewProduct(store, row, brand):
    try:
        store = Store.objects.get(id=store.id)
        group = get_object_or_404(StoreGroup, pk=store.group.id)
        category = get_object_or_404(ProductCategory, pk=row.category)
        brand = get_object_or_404(Brand, pk=brand)
        isCore = 1
        if row.isCore.lower() == 'false':
            isCore = 0
        if str(row.goPrice) == "0":
            row.goPrice = 9999
        try:
            product = Product.objects.get_or_create(model=str(row.model),
                                                    store=store,
                                                    group=group,
                                                    category=category,
                                                    brand=brand,
                                                    EAN=row.EAN,
                                                    packSize=row.packSize,
                                                    costPrice=9999,
                                                    tradePrice=row.tradePrice,
                                                    goPrice=row.goPrice,
                                                    spanNet=0,
                                                    isCore=isCore,
                                                    isGSTExempt=False,
                                                    description=row.description,
                                                    manWarranty=row.manWarranty,
                                                    status="current",
                                                    comments="")
        except BaseException as e:
            pass
    except Product.DoesNotExist:
        pass


def addContext(uploadId, uploadType, rowsFromUpload, firstRowFromUpload, context):
    try:
        CSVUpload.objects.get(id=uploadId)
        addMainContext(uploadType, uploadId, context, rowsFromUpload, firstRowFromUpload)
        context['writeupIsValid'] = True
        context['catalogueIsValid'] = True
        if uploadType == "products":
            addProductsContext(uploadType, uploadId, rowsFromUpload, firstRowFromUpload, context)
    except CSVUpload.DoesNotExist:
        pass


def addWriteContext(uploadId, context, rowsFromUpload, firstRowFromUpload):
    return addProductsWriteContext(context, uploadId, rowsFromUpload, firstRowFromUpload)


def addContextForViewAllWidget(self, context):
    context['form'] = self.form_class
    lastTenCatalogues = models.CSVUpload.objects.filter(uploadType="catalogue").order_by('-id')[:10]
    lastTenProducts = models.CSVUpload.objects.filter(uploadType="products").order_by('-id')[:10]
    lastTenWriteups = models.CSVUpload.objects.filter(uploadType="writeups").order_by('-id')[:10]
    context['catalogue_uploads'] = reversed(lastTenCatalogues)
    context['products_uploads'] = reversed(lastTenProducts)
    context['writeups_uploads'] = reversed(lastTenWriteups)


def addMainContext(uploadType, uploadId, context, rowsFromUpload, firstRowFromUpload):
    metaData = firstRowFromUpload[0]
    context['rowsFromUpload'] = rowsFromUpload
    context['uploadType'] = uploadType
    context['metaData'] = metaData
    context['hasPK'] = True
    context['uploadId'] = uploadId


def addProductsContext(uploadType, uploadId, rowsFromUpload, firstRowFromUpload, context):
    if uploadType == "products":
        assignProducts(context, uploadId, rowsFromUpload, firstRowFromUpload)
        context['products'] = True

def addProductsWriteContext(context, uploadId, rowsFromUpload, firstRowFromUpload):
    assignProducts(context, uploadId, rowsFromUpload, firstRowFromUpload)
    getListOfBlankEANS(uploadId, rowsFromUpload, firstRowFromUpload, context)
    return context['listPendingSuperseding']


def addWriteupContext(uploadType, context):
    if uploadType == "writeups":
        context['writeupIsValid'] = True
    else:
        context['writeupIsValid'] = False

def addCataloguesContext(uploadType, context):
    if uploadType == "catalogue":
        context['catalogueIsValid'] = True
    else:
        context['catalogueIsValid'] = False


def addMatchingConfusedItem(context, rowFromCaller, listConfused, uploadBrand):
    print rowFromCaller.EAN, "rowFromCaller.EAN"
    product = Product.objects.get(EAN=rowFromCaller.EAN)
    try:
        context["isConfusedItem"] = rowFromCaller.model
    except TypeError:
        pass
    row = {}
    row['model'] = str(product.model) + " (Existing item)"
    row['brand'] = uploadBrand
    row['category'] = product.category.id
    row['tradePrice'] = product.tradePrice
    row['description'] = product.description
    row['goPrice'] = product.goPrice
    row['suggestedSell'] = product.goPrice
    row['packSize'] = product.packSize
    row['isCore'] = product.isCore
    row['manWarranty'] = product.manWarranty
    row['EAN'] = product.EAN
    row['status'] = product.status
    row['id'] = product.id
    listConfused.append(row)


def addBeforeEditedItem(rowFromCaller, listEdited, uploadBrand, listNoChanges):
    match = False
    product = Product.objects.get(model=rowFromCaller.model)
    if listNoChanges:
        for noChangeItem in listNoChanges:
            if noChangeItem.EAN == rowFromCaller.EAN:
                match = True
        if not match:
            appendEditedRow(uploadBrand, product, listEdited)
    else:
        appendEditedRow(uploadBrand, product, listEdited)


def getRowsFromUpload(uploadId):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        dto = DTOFactory()
        rowsFromUpload = dto.getRowsFromCSVFile(csvUpload.csvFile.path)
        return rowsFromUpload
    except CSVUpload.DoesNotExist:
        return []


def getFirstRowFromUpload(uploadId):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        dto = DTOFactory()
        rowsFromUpload = dto.getFirstRowFromCSVFile(csvUpload.csvFile.path)
        return rowsFromUpload
    except CSVUpload.DoesNotExist:
        return []


def getValidationRowsFromUpload(uploadId, uploadType):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        dto = DTOFactory()
        result = dto.getValidationRowsFromCSVFile(csvUpload.csvFile.path, uploadType)
        return result
    except CSVUpload.DoesNotExist:
        return []


def getTypeFromUpload(uploadId):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        uploadType = csvUpload.uploadType.lower()
        return str(uploadType)
    except CSVUpload.DoesNotExist:
        return "DoesNotExist"


def getEANErrorStatusForBlanks(rowsFromUpload, context):
    valid = True
    for row in rowsFromUpload:
        newEAN = str(row.EAN)
        if newEAN.isdigit() and len(newEAN) > 0:
            valid = True
        else:
            context["EANBlankError"] = True
            print "context[EANBlankError] = True"
            return False
    return valid


def getEANErrorStatusForAlreadyExists(rowsFromUpload, context):
    valid = True
    for row in rowsFromUpload:
        product = Product.objects.get(id=row.id)
        if not row.EAN == product.EAN and eanAlreadyExists(row):  # means you are adding an ean that already exists
            context["EANExists"] = True
            return False
    return valid


def getNonExistentProducts(rowsFromUpload, uploadType):
    nonExistentList = []
    for row in rowsFromUpload:
        try:
            Product.objects.get(model=str(row.model))
        except Product.DoesNotExist:
            if uploadType == "writeups":
                rowHolder = {}
                rowHolder['model'] = row.model
                rowHolder['web_description'] = row.web_description
                rowHolder['name'] = row.name
                rowHolder['short_description'] = row.short_description
                rowHolder['product_specifications'] = row.product_specifications
                rowHolder['barcode'] = ""
                rowHolder['man_warranty'] = row.man_warranty
                rowHolder['writeupSubmitted'] = True
                nonExistentList.append(rowHolder)
            elif uploadType == "catalogue":
                rowHolder = {}
                rowHolder['model'] = row.model
                rowHolder['price'] = row.price
                rowHolder['comment'] = row.comment
                rowHolder['price_ticket_image_URL'] = row.price_ticket_image_URL
                nonExistentList.append(rowHolder)
            else:
                pass
    return nonExistentList


def getListOfBlankEANS(uploadId, rowsFromUpload, firstRowFromUpload, context):
    uploadBrand = getUploadBrand(firstRowFromUpload)
    EANBlankErrorProductsList = []
    counter = 0
    for row in rowsFromUpload:
        counter += 1
        product = Product.objects.get(id=row.id)
        newEAN = str(row.EAN)
        if newEAN.isdigit() or len(newEAN) > 0:
            pass
        else:
            context['listOfBlankEANSRow'] = counter+2
            EANBlankErrorProductsList.append(row)
            appendBeforeBlankRow(uploadBrand, product, EANBlankErrorProductsList)
    if EANBlankErrorProductsList:
        CSVUploadObj = CSVUpload.objects.get(id=uploadId)
        CSVUploadObj.delete()
    context['listOfBlankEANS'] = EANBlankErrorProductsList
    return EANBlankErrorProductsList


def getEANAlreadyExistsProducts(context, uploadId, rowsFromUpload, firstRowFromUpload):
    uploadBrand = getUploadBrand(firstRowFromUpload)
    EANErrorProductsList = []
    counter = 0
    for row in rowsFromUpload:
        counter += 1
        product = Product.objects.get(id=row.id)
        if not row.EAN == product.EAN and eanAlreadyExists(row):
            context['EANExists'] = True
            context['EANExistsRow'] = counter+2
            showResultsForConfused(row, EANErrorProductsList)
            addMatchingConfusedItem(context, row, EANErrorProductsList, uploadBrand)
    if EANErrorProductsList:
        CSVUploadObj = CSVUpload.objects.get(id=uploadId)
        CSVUploadObj.delete()
    context['listConfusedEANExists'] = EANErrorProductsList
    return EANErrorProductsList


def getUploadBrand(firstRowFromUpload):
    uploadBrand = None
    loopCounter = 0
    for row in firstRowFromUpload:
        loopCounter += 1
        if loopCounter == 1:
            uploadBrand = row.brand
    return uploadBrand


def getAllProductsFromBrand(uploadBrand):
    try:
        brand = Brand.objects.get(id=uploadBrand)
        products = Product.objects.filter(brand=brand)
        return products
    except Brand.DoesNotExist:
        pass


def getProductRelatingToNewRow(uploadBrand, row):
    product = Product.objects.filter(brand=uploadBrand)
    product = product.filter(model=row.model)
    if product:
        product = product[0]
    else:
        product = 0
    return product


def setUploadSaved(uploadId):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        csvUpload.saved = True
        csvUpload.save()
    except CSVUpload.DoesNotExist:
        return "none"


def setUploadExpiry(uploadId, uploadType):
    if uploadType.lower() in ['catalogue']:
        rowsFromUpload = getFirstRowFromUpload(uploadId)
        try:
            csvUpload = models.CSVUpload.objects.get(id=uploadId)
            csvUpload.expiryDate = rowsFromUpload[0].end_date
            csvUpload.save()
        except CSVUpload.DoesNotExist:
            pass


from users.models import Staff

def setCreatedBy(uploadId, pk):
    try:
        csvUpload = models.CSVUpload.objects.get(id=uploadId)
        staff = get_object_or_404(Staff, pk)
        csvUpload.createdBy = staff
        csvUpload.save()
    except CSVUpload.DoesNotExist:
        pass


def setSupersededProducts(listPendingSuperseding, doNotSupersedeList):
    for product in listPendingSuperseding:
        i = Product.objects.get(model=product['model'])
        match = False
        for doNotSupersedeItem in doNotSupersedeList:
            if doNotSupersedeItem == i.model:
                match = True
            else:
                pass
        if match is False:
            i.status = 'superceded'
            i.save()