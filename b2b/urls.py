from django.conf.urls import patterns, url

from b2b import views

urlpatterns = patterns('',
    # ex: /core/login-redirect/
    #stock orders
    url(r'^stock-order/$', views.stockOrderHome, name='stockOrderHome'),
    url(r'^stock-order/booking/(?P<order_id>\d+)/$', views.bookingStockOrder, name='bookingStockOrder'),
    url(r'^search-stock-order/(?P<type>[-\w]+)/$', views.searchStockOrder, name='searchStockOrder'),
    url(r'^stock-order/new/$', views.newStockOrder, name='newStockOrder'),
    url(r'^save-order/$', views.saveOrder, name='saveOrder'),
    url(r'^open-order/(?P<order_id>\d+)/$', views.openOrder, name='openOrder'),
    url(r'^calc-order-net/$', views.calcNetGivenInvoice, name='calcNetGivenInvoice'),
    url(r'^locality-search/$', views.searchLocalities, name='searchLocalities'),
    url(r'^view-po/(?P<etOrder_id>\d+)/$', views.viewPurchaseOrder, name='viewPurchaseOrder'),
    url(r'^view-por/(?P<etOrder_id>\d+)/$', views.viewPurchaseOrderResponse, name='viewPurchaseOrderResponse'),
    #store side ho invoices
    url(r'^invoicing/search/(?P<type>[-\w]+)/$', views.searchHOInvoices, name='searchHOInvoices'),
    url(r'^invoicing/ajax/search/$', views.searchHOInvoicesAjax, name='searchHOInvoicesAjax'),
    #head office side invoicing
    url(r'^ho/invoicing/$', views.HOInvoicingHome, name='HOInvoicingHome'),
    url(r'^ho/invoicing/new/$', views.newHOInvoice, name='newHOInvoice'),
    url(r'^ho/invoicing/reverse/(?P<invoice_id>\d+)/$', views.reverseHOInvoice, name='reverseHOInvoice'),
    url(r'^ho/invoicing/delete/(?P<invoice_id>\d+)/$', views.deleteHOInvoice, name='deleteHOInvoice'),
    url(r'^ho/invoicing/save/$', views.saveHOInvoice, name='saveHOInvoice'),
    url(r'^ho/invoicing/open/(?P<invoice_id>\d+)/$', views.openHOInvoice, name='openHOInvoice'),
    url(r'^ho/invoicing/searchB2B/$', views.B2BSearchView.as_view(), name='searchB2bInvoiceAjax'),
    url(r'^ho/invoicing/b2bInvoiceToInvoice/(?P<invoice_id>\d+)/$', views.b2bInvoiceToInvoice, name='b2bInvoiceToInvoice'),
    #recons
    url(r'^recons/dashboard/$', views.reconHome, name='reconHome'),
    url(r'^searchRecons/(?P<type>[-\w]+)/$', views.searchRecons, name='searchRecons'),
    url(r'^recons/new/$', views.newRecon, name='newRecon'),
    url(r'^recons/save/$', views.saveRecon, name='saveRecon'),
    url(r'^recons/reverse/(?P<recon_id>\d+)/$', views.reverseRecon, name='reverseRecon'),
    #charges
    url(r'^charges/dashboard/$', views.chargesHome, name='chargesHome'),
    url(r'^searchCharges/$', views.searchCharges, name='searchCharges'),
    url(r'^charges/new/produce-invoice-list/$', views.produceInvoiceList, name='newCharge'),
    url(r'^charges/new/produce-invoice-list/2/$', views.produceInvoiceLinesList, name='newChargeStepTwo'),
    url(r'^charges/new/produce-charge-sheet/$', views.produceChargeSheet, name='completeCharge'),
    url(r'^charges/print/single/(?P<charge_id>\d+)/$', views.printStoreChargeSheet, name='printStoreChargeSheet'),
    url(r'^charges/print/summary/(?P<charge_id>\d+)/$', views.printSummaryChargeSheet, name='printSummaryChargeSheet'),
    #payments
    url(r'^store-payment/create/(?P<pk>\d+)$', views.StorePaymentsCreateView.as_view(), name='createStorePayment'),
    url(r'^store-payment/view/(?P<pk>\d+)$', views.StorePaymentsListView.as_view(), name='viewStorePayments'),
    url(r'^store-payment/delete/(?P<pk>\d+)$', views.StorePaymentsDeleteView.as_view(), name='revertLastPayment'),
    #narta simulator for debugging.
    url(r'^narta-simulator/$', views.nteSim, name='nteSim'),
    url(r'^narta-simulator/accept/(?P<order_id>\d+)/$', views.nteOrderAccept, name="acceptETOrder"),
    url(r'^narta-simulator/partial-accept/(?P<order_id>\d+)/$', views.nteOrderPartialAccept, name="partialAcceptETOrder"),
    url(r'^narta-simulator/reject/(?P<order_id>\d+)/$', views.nteOrderReject, name="rejectETOrder")
)
