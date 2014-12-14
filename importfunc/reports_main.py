from time import clock, time
from reports_querysets import *

start = clock()

tester = Tester().djangofy()
tester.exportFile(format='json', filename="tester")

terminal = Terminal().djangofy()
terminal.exportFile(format='json', filename="terminal")

sale = Sale().djangofy()
sale.exportFile(format='json', filename="sale")

salesLine = SalesLine().djangofy()
salesLine.exportFile(format='json', filename="salesLine")

saleInvoice = SaleInvoice().djangofy()
saleInvoice.exportFile(format='json', filename="saleInvoice")

saleInvoiceLine = SaleInvoiceLine().djangofy()
saleInvoiceLine.exportFile(format='json', filename="saleInvoiceLine")

salesPayment = SalesPayment().djangofy()
salesPayment.exportFile(format='json', filename="salesPayment")

HOInvoice = HOInvoice().djangofy()
HOInvoice.exportFile(format='json', filename="HOInvoice")


elapsed = (clock() - start)
print "algorithm completed in %.2f sec" % elapsed