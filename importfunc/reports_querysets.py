from copy import copy
import csv
import os


class Queryset(list):
    importdatafolder = "../import-data/csv/testdata/"
    exportdatafolder = "../import-data/import/testdata/"

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


class Tester(Queryset):
    mapping = {
        'one': '111',
        'two': '222',
        'three': '333',
        'four': '444',
    }

    def __init__(self, Filename="Tester"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        newMapped = Queryset()
        newMapped.extend(self.keyMap()[:500])
        return Queryset.djangofy(newMapped, modelName='reports.tester')


class Sale(Queryset):
    mapping = {
        'total': '1',
        'customer': '2',
        'deliveryAddress': '3',
        'purchaseDate': '4',
        'fullPaymentDate': '5',
        'salesPerson': '6',
        'code': '7',
        'status': '8',
        'note': '9',
        'storeNote': '10',
        'terminal': '11',
        'modified': '12',
        'created': '13',
    }

    def __init__(self, Filename="Sale"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='pos.sale')

    def djangoMap(self):
        mapped = self.keyMap()
        newMap = Queryset()
        for item in mapped:
            item['purchaseDate'] = item.get('purchaseDate')
            item['fullPaymentDate'] = item.get('fullPaymentDate')
            item['modified'] = item.get('modified')
            item['created'] = item.get('created')
            newMap.append(item)
        return newMap


class SalesPayment(Queryset):
    mapping = {
        'sale': '1',
        'amount': '2',
        'date': '3',
        'receivedBy': '4',
        'paymentMethod': '5',
        'groupedBy': '6',

    }

    def __init__(self, Filename="SalesPayment"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='pos.salespayment')

    def djangoMap(self):
        mapped = self.keyMap()
        newMap = Queryset()
        for item in mapped:
            item['date'] = item.get('date')
            newMap.append(item)
        return newMap


class SaleInvoice(Queryset):
    mapping = {
        'created': '1',
        'sale': '2',
        'reference': '3',
        'total': '4',
        'salesPerson': '5',
        'notes': '6',
    }

    def __init__(self, Filename="SaleInvoice"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='pos.saleinvoice')

    def djangoMap(self):
        mapped = self.keyMap()
        newMap = Queryset()
        for item in mapped:
            item['created'] = item.get('created')
            newMap.append(item)
        return newMap


class SaleInvoiceLine(Queryset):
    mapping = {
        'invoice': '1',
        'salesLine': '2',
        'quantity': '3',
        'unitPrice': '4',
        'price': '5',
    }

    def __init__(self, Filename="SaleInvoiceLine"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='pos.saleinvoiceline')

    def djangoMap(self):
        mapped = self.keyMap()
        return mapped


class SalesLine(Queryset):
    mapping = {
        'sale': '1',
        'item': '2',
        'modelNum': '3',
        'warrantyRef': '4',
        'description': '5',
        'quantity': '6',
        'released': '7',
        'unitPrice': '8',
        'price': '9',
        'line': '10',
    }

    def __init__(self, Filename="SalesLine"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        newMapped = Queryset()
        newMapped.extend(self.keyMap()[:500])
        return Queryset.djangofy(newMapped, modelName='pos.salesline')


class Terminal(Queryset):
    mapping = {
        'store': '1',
        'name': '2',
    }

    def __init__(self, Filename="Terminal"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        newMapped = Queryset()
        newMapped.extend(self.keyMap()[:500])
        return Queryset.djangofy(newMapped, modelName='pos.terminal')


class HOInvoice(Queryset):
    mapping = {
        'type': '2',
        'distributor': '3',
        'store': '4',
        'invoiceNumber': '5',
        'invoiceDate': '6',
        'orderReference': '7',
        'extendedCredit': '10',
        'freight': '13',
        'invTotalExGST': '14',
        'invTotal': '15',
        'netTotal': '16',
        'createdDate': '21',
        'modifiedDate': '22',
        'createdBy': '23',
    }

    def __init__(self, Filename="HOinv"):
        Queryset.__init__(self, Filename=Filename)

    def keyMap(self):
        return Queryset.keyMap(self, self.mapping)

    def djangofy(self):
        return Queryset.djangofy(self.djangoMap(), modelName='b2b.headofficeinvoice')

    def djangoMap(self):
        mapped = self.keyMap()
        newMap = Queryset()
        for item in mapped:
            item['invoiceDate'] = item.get('invoiceDate')
            item['dueDate'] = item.get('dueDate')
            item['chargedDate'] = item.get('chargedDate')
            item['reconciledDate'] = item.get('reconciledDate')
            item['createdDate'] = item.get('createdDate')
            item['modifiedDate'] = item.get('modifiedDate')
            newMap.append(item)
        return newMap


        #
        # 'created': '1',
        # 'sale': '2',
        # 'reference': '3',
        # 'total': '4',
        # 'salesPerson': '5',
        # 'notes': '6',
        # 'xxx': '7',
        # 'xxx': '8',
        # 'xxx': '9',
        # 'xxx': '10',
        # 'xxx': '11',
        # 'xxx': '12',
        # 'xxx': '13',
        # 'xxx': '14',
        # 'xxx': '15',
        # 'xxx': '16',
        # 'xxx': '17',
        # 'xxx': '18',
        # 'xxx': '19',
        # 'xxx': '20',
        # 'xxx': '21',
        # 'xxx': '22',
        # 'xxx': '23',