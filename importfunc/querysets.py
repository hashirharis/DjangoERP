__author__ = 'Yussuf'

from copy import copy
import csv
import os

class Queryset(list):
    importdatafolder = "../import-data/csv/"
    exportdatafolder = "../import-data/import/"

    def __init__(self, Filename="", *args, **kwargs):
        if Filename:
            os.chdir(os.path.dirname(__file__))
            Filename = self.importdatafolder+Filename+'.CSV'
            super(Queryset, self).__init__(self.readData(Filename))
        else:
            super(Queryset, self).__init__(*args, **kwargs)

    def readData(self, FileName):
        gathered = []
        iFile = open(FileName, "rb")
        reader = csv.reader(iFile)
        header = []
        rowNum = 0
        for row in reader:
            # Save header row.
            if rowNum == 0:
                header = row
            else:
                colNum = 0
                entry = {}
                for col in row:
                    entry[header[colNum]] = col
                    colNum += 1
                gathered.append(entry)
            rowNum += 1
        iFile.close()
        return gathered

    def get(self, **kwargs):
        '''
            can use django like kwargs eg. name=Fairfield
        '''
        match = len(kwargs)
        for item in self:
            matches = 0
            for key, value in kwargs.iteritems():
                if item.get(key) == value:
                    matches += 1
                else:
                    break
                if matches == match:
                    return item
        return None

    def parse_int_or_one(self, value):
        try:
            return int(value)
        except ValueError:
            return 1

    def parse_float_or_zero(self, value):
        try:
            return float(value)
        except ValueError:
            return 0.00

    @staticmethod
    def parse_float_or_zero(value):
        try:
            return float(value)
        except ValueError:
            return 0.00

    def parse_string_silent(self, value):
        return unicode(value, errors='ignore').encode('utf-8', errors='ignore')

    @staticmethod
    def parse_string_silent(value):
        return unicode(value, errors='ignore').encode('utf-8', errors='ignore')

    def filter(self, **kwargs):
        match = len(kwargs)
        items = Queryset()
        for item in self:
            matches = 0
            for key, value in kwargs.iteritems():
                if item.get(key) == value:
                    matches += 1
                else:
                    break
            if matches == match:
                items.append(item)
        return items

    def exclude(self, **kwargs):
        match = len(kwargs)
        items = Queryset()
        for item in self:
            matches = 0
            for key, value in kwargs.iteritems():
                if item.get(key) == value:
                    matches += 1
            if matches == match:
                continue
            else:
                items.append(item)
        return items

    def unique(self, field):
        '''
            returns all the unique values of a given field
        '''
        toReturn = Queryset()
        for item in self:
            value = item.get(field, None)
            if value is not None:
                if value not in toReturn:
                    toReturn.append(value)
        return toReturn

    def assignAI(self, key='id'):
        '''
            key is what the auto increment value will have as a key
        '''
        id = 1
        new = Queryset()
        for item in self:
            newItem = copy(item)
            new.append(newItem)
            newItem[key] = id
            id += 1
        return new

    def defaultValue(self, key, value):
        '''
            all items in list will have this default applied to them
        '''
        new = Queryset()
        for item in self:
            newItem = copy(item)
            new.append(newItem)
            newItem[key] = value
        return new

    def djangofy(self, modelName, mappingDict=None):
        '''
            create a django export array from the current queryset
        '''
        djangofied = Queryset()
        mapped = []
        if mappingDict: #will map if specified
            mapped = self.keyMap(mappingDict)
        else:
            mapped = self
        for item in mapped:
            fields = copy(item)
            newItem = {}
            newItem['fields'] = fields
            djangofied.append(newItem)
        djangofied = djangofied.assignAI(key="pk")
        djangofied = djangofied.defaultValue(key="model", value=modelName)
        return djangofied

    def export(self, format='yaml'):
        if format=='yaml':
            import yaml
            return yaml.dump(list(self))
        elif format=='json':
            import json
            return json.dumps(list(self))
        elif format=='xml':
            import xmlrpclib
            return xmlrpclib.dumps(list(self))
        return None

    def exportFile(self, format='yaml', filename=''):
        iFile = open(self.exportdatafolder + filename + "."+format, "wb")
        iFile.write(self.export(format))
        iFile.close()

    def keyMap(self, mappingDict):
        '''
            Maps a set of keys to the current queryset
             mainly for exporting the models
             must be in form of dict {newval: oldval}
             will only return the values that are being mapped
        '''
        new = Queryset()
        for item in self:
            newItem = {}
            for key, val in mappingDict.iteritems():
                newItem[key] = item.get(val) #map old key to new key
            new.append(newItem)
        return new

class GLN(Queryset):
    def __init__(self, Filename="GLN"):
        Queryset.__init__(self, Filename=Filename)

    def getGLNFor(self, name):
        '''
        searches a polymorphic foreign key (GLNAME) for references to either a store or distributor
        returns blank string if not found
        '''
        gln = self.get(GLNAME=name)
        if gln is not None:
            return gln.get("GLN", "")
        return ""

    def hasElectronicTrading(self, gln):
        '''
        returns whether the specified gln has electronic trading
        '''
        gln = self.get(GLN=gln)
        if gln is not None:
            hasET = gln.get("B2B", "N")
        else:
            return False
        return True if hasET == "Y" else False

class Postcode(Queryset):
    mapping = {
        'code': 'Pcode',
        'locality': 'Locality',
        'state': 'State',
        'deliveryOffice': 'DeliveryOffice',
    }

    def __init__(self, Filename="Postcode"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        newMapped = Queryset()
        newMapped.extend(self.keyMap()[:500])
        return Queryset.djangofy(newMapped, modelName='core.postcode')

class Store(Queryset):
    mapping = {
        'name': 'STORENAME',
        'code': 'SCODE',
        #need to put in contact
        'address': 'ADDRESS',
        'suburb': 'SUBURB',
        'city': 'CITY',
        'state': 'State',
        'postcode': 'PCODE',
        'fax': 'FAX',
        'email': 'EMAIL',
        'phone': 'Phone',
        'companyName': 'COMPANYNAME',
        'spanStoreID': 'STOREID',
        'ABN': 'ABN',
        'ACN': 'ACN'
    }

    def __init__(self, Filename="Stores", glns=GLN()):
        Queryset.__init__(self, Filename=Filename)
        self.glns = glns

    def keyMap(self):
        mapped = Queryset.keyMap(self, self.mapping)
        for item in mapped:
            itemsGLN = self.glns.getGLNFor(item.get('name'))
            item['GLN'] = itemsGLN
            item['isHead'] = True if item.get('code') == 'HO' else False
            rawItem = self.get(STORENAME=item.get('name'))
            item['contact'] = "%s %s %s" % (rawItem.get("MAN_TITLE"), rawItem.get("MAN_FIRST"), rawItem.get("MAN_LAST"))
        #SUPER Store
        mapped.append({
            "name": "SUPER",
            "code": "SUPER",
            "isHead": True,
            "contact": "",
            "address": "",
            "suburb": "",
            "city": "",
            "state": "",
            "postcode": "",
            "fax": "",
            "phone": "",
            "email": "",
            "companyName": "",
            "spanStoreID": "",
            "ABN": "",
            "ACN": "",
            "GLN": ""
        })
        return mapped

    def djangofy(self):
        mapped = self.keyMap()
        for item in mapped:
            item['group'] = 1
        return Queryset.djangofy(mapped, modelName='users.store')

class Customer(Queryset):
    mapping = {
        'firstName': 'FIRSTNAME',
        'lastName': 'LASTNAME',
        'title': 'TITLE',
        #need to put in store
        'store': 'STORE',
        'address': 'ADDRESS',
        'suburb': 'SUBURB',
        'cityState': 'CITYSTATE',
        'postcode': 'POSTCODE',
        'paddress': 'PADDRESS',
        'psuburb': 'PSUBURB',
        'pcityState': 'PCITY',
        'ppostcode': 'PPCODE',
        'email': 'EMAIL',
        'homePhone': 'HOMEPHONE',
        'workPhone': 'WORKPHONE',
        'fax': 'FAX',
        'mobile': 'MOBILE',
        'comment': 'Comment',
    }

    def __init__(self, Filename="Customer"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        mapped = self.keyMap()
        idstore = Store().assignAI()
        hoid = idstore.get(SCODE='HO').get('id')
        newMapped = Queryset()
        newMapped.extend(mapped[:2000])
        mapped = newMapped
        for i, item in enumerate(mapped):
            store = idstore.get(TABID=item['store'])
            item['store'] = hoid #store.get('id') if store is not None else hoid
            item['group'] = 1
            #else:
                #print "found customer for another store: " + str(item['store'])
        return Queryset.djangofy(mapped, modelName='pos.customer')

class Brand(Queryset):
    mapping = {
        'brand': 'BRAND',
        'purchaser': 'SUPPLIER',
        'address': 'ADDRESS1',
        'suburb': 'LOCALITY',
        'cityState': 'CITY',
        'postcode': 'PCODE',
        'paddress': 'ADDRESS2',
        'pcityState': 'CITY2',
        'ppostcode': 'PCODE2',
        'phone': 'PHONE',
        'fax': 'FAX',
        'email': 'EMAIL',
        'repName': 'REP',
        'distributor': 'DISTRIBUTOR',
        'repPhone': 'REPPHONE',
        'ABN': 'DISTABN',
        'comments': 'HOCMNT1',
        'isHOPreferred': 'HOPREF',
        'rebate': 'REBATE',
        'actualRebate': 'REBATE'
    }

    def __init__(self, Filename="Supplier", glns=GLN()):
        '''always returns raw values'''
        Queryset.__init__(self, Filename=Filename)
        self.glns = glns
        self.master = Queryset('masterBrand') #master EAN listing from narta.

    def brandInMaster(self, item):
        return [product for product in self.master if item['brand'].lower() in product.get('Description','').lower()]

    def keyMap(self):
        mapped = Queryset.keyMap(self, self.mapping)
        newMap = Queryset()
        [newMap.append(item) for item in mapped if len(self.brandInMaster(item))]
        mapped = newMap
        for item in mapped:
            itemsGLN = self.glns.getGLNFor(item.get('distributor'))
            hasET = self.glns.hasElectronicTrading(itemsGLN)
            rebate = self.parse_float_or_zero(item.get('rebate'))
            rebate = rebate * 100 if rebate >= 0 else rebate * -100
            item['rebate'] = rebate
            item['actualRebate'] = rebate
            item['GLN'] = itemsGLN
            item['hasElectronicTrading'] = hasET
            item['isHOPreferred'] = True if item.get('isHOPreferred', "N") == "Y" else False
            item['masterBrand'] = self.brandInMaster(item)[0].get('Description')
        return mapped

    def djangofy(self):
        mapped = self.keyMap()
        hoid = Store().assignAI().get(SCODE='HO').get('id')
        for item in mapped:
            item['store'] = hoid
            item['group'] = 1
            item['isShared'] = True
            del item['masterBrand']
        return Queryset.djangofy(mapped, modelName='core.brand')

class Category(Queryset):
    mapping = {
        'name': 'L4'
    }

    def __init__(self, Filename="masterCategory", warranty_cat=Queryset('Warranty_Categories')):
        self.warranty_link = warranty_cat
        Queryset.__init__(self, Filename=Filename)

    def getExtWarrantyLinks(self, categoryName):
        cat = self.keyMap().assignAI('id')
        links = self.warranty_link.filter(CATEGORY=categoryName)
        ids = []
        for link in links:
            ids.append(cat.get(name=link.get('WARRANTY'), depth=2).get('id')) #get that warranty id from the keyMapping
        return ids

    def keyMap(self):
        mapped = Queryset.keyMap(self, self.mapping).exclude(name='')
        mapped = mapped.defaultValue(key="depth", value=4)
        level1 = self.unique('L1')
        level2 = self.unique('L2')
        level3 = self.unique('L3')
        for category in level3:
            newObj = {
                'name': category,
                'depth': 3
            }
            mapped.append(newObj)
        for category in level2:
            newObj = {
                'name': category,
                'depth': 2
            }
            mapped.append(newObj)
        for category in level1:
            newObj = {
                'name': category,
                'depth': 1
            }
            mapped.append(newObj)
        return mapped

    def djangofy(self):
        mapped = self.keyMap()
        IDmapped = self.keyMap().assignAI()
        hoid = Store().assignAI().get(SCODE='HO').get('id')
        for item in mapped:
            if item.get('depth') == 4:
                parentName = self.get(L4=item.get('name')).get('L3')
                parent = IDmapped.get(name=parentName, depth=3).get('id')
            elif item.get('depth') == 3:
                parentName = self.get(L3=item.get('name')).get('L2')
                parent = IDmapped.get(name=parentName, depth=2).get('id')
            elif item.get('depth') == 2:
                parentName = self.get(L2=item.get('name')).get('L1')
                parent = IDmapped.get(name=parentName, depth=1).get('id')
            else:
                parent = None
            item['parentCategory'] = parent
            item['extWarrantyTypes'] = self.getExtWarrantyLinks(item.get('name'))
            item['store'] = hoid
            item['group'] = 1
            item['isShared'] = True
        return Queryset.djangofy(mapped, modelName='core.productcategory')

class Model(Queryset):
    mapping = {
        'status': 'STATUS',
        'model': 'MODEL',
        #category
        #brand
        'brand' : 'BRANDID',
        'category' : 'CLASSID',
        'EAN': 'EAN',
        'packSize': 'MINPURCH',
        'costPrice': 'COST',
        'tradePrice': 'TRADE',
        'goPrice': 'GO',
        'isCore': 'HOCORE',
        'isGSTExempt': 'G',
        'description': 'DESCR',
        'manWarranty': 'MANWARRANT',
        'comments': 'COMMENTS',
    }

    def __init__(self, Filename="Models", category=Category(), brand=Brand(), store=Store(), master=Queryset('Master')):
        Queryset.__init__(self, Filename=Filename)
        self.idCategory = category.keyMap().assignAI()
        self.idBrand = brand.keyMap().assignAI()
        self.store = store
        self.master = master
        self.eans = [item.get('EAN ID') for item in master]

    def eanInMaster(self, item):
        '''
            only return models which are contained in the master ean list.
        '''
        return item['EAN'] in self.eans

    def getBrandID(self, item):
        brandName = self.master.get(**{'EAN ID': item.get('EAN')}).get('Description', '')
        brand = self.idBrand.get(masterBrand=brandName)
        return brand.get('id') if brand is not None else 0

    def getCategoryID(self, item):
        categoryName = self.master.get(**{'EAN ID': item.get('EAN')}).get('L4', '')
        if categoryName == "": self.master.get(**{'EAN ID': item.get('EAN')}).get('L3', '')
        return self.idCategory.get(name=categoryName).get('id')

    def keyMap(self):
        mapped = Queryset.keyMap(self, self.mapping)
        newMap = Queryset()
        [newMap.append(item) for item in mapped if self.eanInMaster(item)]
        mapped = newMap
        for item in mapped:
            item['isGSTExempt'] = True if item.get('isGSTExempt', "N") is "Y" else False
            item['isCore'] = True if item.get('isCore', "N") is "Y" else False
            item['isGSTExempt'] = True if item.get('isGSTExempt', "N") is "Y" else False
        return mapped

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='core.product')

    def djangoMap(self):
        '''
            before importing models make sure the BRANDID 1-99 is not Jan-99
        '''
        mapped = self.keyMap()
        newMap = Queryset()
        idstore = self.store.assignAI()
        hoid = idstore.get(SCODE='HO').get('id')
        for item in mapped:
            item['brand'] = self.getBrandID(item)
            item['category'] = self.getCategoryID(item)
            item['status'] = self.parse_string_silent(item.get('status'))
            item['EAN'] = self.parse_string_silent(item.get('EAN'))
            item['packSize'] = self.parse_int_or_one(item.get('packSize'))
            item['costPrice'] = self.parse_float_or_zero(item.get('costPrice'))
            item['spanNet'] = self.parse_float_or_zero(item.get('costPrice'))
            item['tradePrice'] = self.parse_float_or_zero(item.get('tradePrice'))
            item['goPrice'] =  self.parse_float_or_zero(item.get('goPrice'))
            item['description'] = self.parse_string_silent(item.get('description'))
            item['model'] = self.parse_string_silent(item.get('model'))
            item['manWarranty'] = self.parse_string_silent(item.get('manWarranty'))
            item['comments'] = self.parse_string_silent(item.get('comments'))
            item['isShared'] = True
            item['store'] = hoid
            item['group'] = 1
            if item.get('costPrice') > 1000000 or\
                item.get('tradePrice') > 1000000 or\
                item.get('goPrice') > 1000000:
                continue
            if item['brand'] < 1:
                #print "%s : brand does not exist in master brands" % item['brand']
                continue
            newMap.append(item)
        return newMap

class Warranty(Queryset):
    mapping = {
        #warranty specific
        'model': 'CODE',
        'startValue': 'LOWER',
        'endValue': 'UPPER',
        'costPrice': 'COST',
        'goPrice': 'GOPRICE',
        'category' : 'TYPE',
    }

    def __init__(self, Filename="Warranty", category=Category(), brands=Brand(), store=Store()):
        Queryset.__init__(self, Filename=Filename)
        self.category = category.keyMap().assignAI('id')
        self.hoid = store.get(SCODE='HO').get('id')
        self.blanketBrand = brands.keyMap().assignAI('id').get(masterBrand='Narta').get('id', 0) #All warranties come under the narta brand.

    def keyMap(self):
        mapped = Queryset.keyMap(self, self.mapping)
        for item in mapped:
            pass
            #item['EAN'] = ''
            #item['description'] = ''
            #item['manWarranty'] = ''
            #item['comments'] = ''
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        mapped = self.keyMap()
        newMap = Queryset()
        for item in mapped:
            item['brand'] = self.blanketBrand
            item['category'] = self.category.get(name=item['category'], depth=2).get('id')
            #item['EAN'] = self.parse_string_silent(item.get('EAN'))
            item['costPrice'] = self.parse_float_or_zero(item.get('costPrice'))
            item['tradePrice'] = item['costPrice']
            item['spanNet'] = item['costPrice']
            item['startValue'] = self.parse_float_or_zero(item.get('startValue'))
            item['endValue'] = self.parse_float_or_zero(item.get('endValue'))
            item['goPrice'] = self.parse_float_or_zero(item.get('goPrice'))
            #item['description'] = self.parse_string_silent(item.get('description'))
            item['model'] = self.parse_string_silent(item.get('model'))
            #item['manWarranty'] = self.parse_string_silent(item.get('manWarranty'))
            #item['comments'] = self.parse_string_silent(item.get('comments'))
            item['isShared'] = True
            item['store'] = self.hoid
            item['group'] = 1
            newMap.append(item)
        return Queryset.djangofy(newMap, modelName='core.warranty')