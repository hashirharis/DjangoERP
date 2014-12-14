__author__ = 'Yussuf'
import os
import yaml
import datetime
import csv
import StringIO

class GenericReader():
    '''
        This is used to provide a quick read of all files. Does not map values to human readable
    '''
    mapped = {}
    type = ""

    def __init__(self, string):
        lines = string.split("~")
        self.type = lines[0].split("|")[0]
        os.chdir(os.path.dirname(__file__))
        mappingsFile = open("./mappings/%s.yaml" % self.type)
        yamlArr = yaml.load(mappingsFile)
        mappingsFile.close()
        returnObj = {}
        for line in lines:
            values = line.split("|")
            key = values[0].strip()
            keys = yamlArr.get(key) #get the key mappings
            if key == "":
                continue
            if key == "FTXHEADER" or key == "LINEITEM" or key == "LINELOC":
                #these are keys that require arrays rather than fixed mappings.
                if returnObj.get(key, None) is None:
                    returnObj[key] = []
                returnObj[key].append(self.mapArrs(keys, values))
            else:
                returnObj[key] = self.mapArrs(keys, values)
        self.mapped = returnObj

    def mapArrs(self, keys, vals):
        mapped = {}
        index = 0
        for x in keys:
            try:
                mapped[x] = vals[index]
            except IndexError:
                #print "error on %s" %(vals[0])
                break
            index += 1
        return mapped

class GenericWriter():
    def __init__(self):
        self.stringIO = StringIO.StringIO()
        self.purchaseOrderCsv = csv.writer(self.stringIO, delimiter='|', quoting=csv.QUOTE_NONE, lineterminator='~')

    def writeLine(self, array):
        self.purchaseOrderCsv.writerow(array)

    def getVal(self):
        return self.stringIO.getvalue()

class POResponder():

    def __init__(self, poRAW, status):
        self.purchaseOrder = GenericReader(poRAW).mapped
        #status = 29,4,27
        self.createPurchaseOrderResponse(status)

    def createPurchaseOrderResponse(self, status):
        now = datetime.datetime.now().strftime("%Y%m%d%H%M")
        headerObj = self.purchaseOrder["EAPO"]
        por = GenericWriter()
        header = [
            "EAPOR",
            "ORDRSP",
            "231",
            "232155555", #generic order response number
            status, #5
            "T",
            headerObj["supplier"],
            headerObj["purchaser"],
            now,
            "", "", "", "", #datetimeexpected,shipmentrequested, deliver not after/before   #13
            headerObj["orderNumber"],
            headerObj["contractNumberReference"], #15
            headerObj["blanketOrderNoReference"],
            headerObj["promotionDealNoReference"],
            headerObj["salesDeptNoReference"],
            headerObj["purchaser"],
            headerObj["purchasersName"],   #20
            headerObj["purchasersStreetAddressLine1"],
            headerObj["purchasersStreetAddressLine2"],
            headerObj["purchasersCitySuburb"],
            headerObj["purchasersState"],
            headerObj["purchasersPostcode"],   #25
            headerObj["purchasersContactName"],
            headerObj["purchasersEmailAddress"],
            headerObj["purchasersPhoneNumber"],
            headerObj["supplier"],
            headerObj["suppliersName"], #30
            headerObj["suppliersStreetAddressLine1"],
            headerObj["suppliersStreetAddressLine2"],
            headerObj["suppliersCitySuburb"],
            headerObj["suppliersState"],
            headerObj["suppliersPostcode"], #35
            headerObj["purchasersShipToCode"],
            headerObj["purchasersShipToName"],
            headerObj["purchasersShipToStreetAddressLine1"],
            headerObj["purchasersShipToStreetAddressLine2"],
            headerObj["purchasersShipToCitySuburb"],    #40
            headerObj["purchasersShipToState"],
            headerObj["purchasersShipToPostcode"],
            headerObj["purchasersShipToAddressLocation"],
            headerObj["purchasersShipToReferenceQualifier"],
            headerObj["purchasersShipToReferenceNumber"],   #45
            headerObj["purchasersBillToCode"],
            headerObj["purchasersBillToName"],
            headerObj["purchasersBillToStreetAddressLine1"],
            headerObj["purchasersBillToStreetAddressLine2"],
            headerObj["purchasersBillToCitySuburb"],    #50
            headerObj["purchasersBillToState"],
            headerObj["purchasersBillToPostcode"],
            headerObj["finalShipToCode"],
            headerObj["finalShipToName"],
            headerObj["finalShipToStreetAddress1"],    #55
            headerObj["finalShipToStreetAddress2"],
            headerObj["finalShipToCitySuburb"],
            headerObj["finalShipToState"],
            headerObj["finalShipToPostcode"],
        ]
        por.writeLine(header)

        if status==4: #only adjust the first line
            lineitem = self.purchaseOrder["LINEITEM"]
            if isinstance(lineitem, list):
                lineitem = lineitem[0]
            porLineItem = [
                "LINEITEM",
                1,
                3,
                "",
                lineitem['gtinProductCode'],
                lineitem['suppliersProductCode'],
                "",
                lineitem['purchaserProductCode'],
                lineitem['quantity'],
                "", "",
                "11112021",#dummy date, datetime for backorder
                -1,
                "BP",
                "AV",
            ]
            por.writeLine(porLineItem)
            FTXHEADER = [
                "FTXHEADER",
                "ZZZ",
                "Model %s not fully allocated for store" % lineitem['purchaserProductCode'],
            ]
            por.writeLine(FTXHEADER)
            FTXHEADER = [
                "FTXHEADER",
                "ZZZ",
                "Model %s likely to be available on" % lineitem['purchaserProductCode'],
            ]
            por.writeLine(FTXHEADER)
            totalAmmount = float(self.purchaseOrder['END']['totalMonetaryAmount'])
            unitPrice = float(lineitem['unitPrice'])
            totalAmmount = totalAmmount - unitPrice
        else:
            totalAmmount = float(self.purchaseOrder['END']['totalMonetaryAmount'])
        END = [
            "END",
            "%.2f" % totalAmmount,
            "232155555" #generic order response number
        ]
        por.writeLine(END)
        self.PORRAW = por.getVal()