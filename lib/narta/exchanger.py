__author__ = 'Yussuf'
import urllib2
import os
import datetime

from b2b.models import B2BInvoice
from b2b.models import ElectronicStockOrder

class nartaExchanger():

    def __init__(self, test=False):
        if test:
            self.sendUrl = 'https://bureau4.pacificcommerce.com.au/websuite/PACCOMHTTPIn.asp?MBX=birite&pwd=bhf54s'
            self.recieveUrl = 'https://bureau4.pacificcommerce.com.au/websuite/PACCOMHTTPOut.asp?MBX=birite&pwd=bhf54s'
            self.instance = "test"
        else:
            self.sendUrl = 'https://bureau1.pacificcommerce.com.au/websuite/PACCOMHTTPIn.asp?MBX=birite&pwd=bhf54s'
            self.recieveUrl = 'https://bureau1.pacificcommerce.com.au/websuite/PACCOMHTTPOut.asp?MBX=birite&pwd=bhf54s'
            self.instance = "prod"

    def send(self, string):
        os.chdir(os.path.dirname(__file__))
        today = datetime.datetime.today()
        now = datetime.datetime.now()
        mappingsFile = open("./logs/%s_sent_%s-%s-%s.txt" % (self.instance, today.month, today.day, today.year), "ab")
        request = urllib2.Request(self.sendUrl, string)
        opener = urllib2.build_opener()
        feeddata = opener.open(request).read()
        if feeddata == "<IDOC/>":
            mappingsFile.write(str(now) + " : SUCCESS\n" + string + "\t\n")
            mappingsFile.close()
        else:
            mappingsFile.write(str(now) + " : FAILED\n" + feeddata + "\t\n")
            mappingsFile.close()

    def recieve(self):
        today = datetime.datetime.today()
        now = datetime.datetime.now()
        request = urllib2.Request(self.recieveUrl)
        opener = urllib2.build_opener()
        feeddata = opener.open(request).read()
        os.chdir(os.path.dirname(__file__))
        mappingsFile = open("./logs/%s_recieved_%s-%s-%s.txt" % (self.instance, today.month, today.day, today.year), "ab")
        if feeddata == "":
            #no more responses
            mappingsFile.write(str(now) + " : NO RESPONSE\n")
            mappingsFile.close()
        else:
            #keep doing this till all responses are taken
            #TODO: populate response RAW for Electronic Stock Orders
            #TODO: populate B2BInvoices fields for B2B Invoices
            mappingsFile.write(str(now) + " : RECIEVED\n" + feeddata + "\t\n")
            mappingsFile.close()
            self.recieve()