from django.conf.urls import patterns, url

from pos import views, signals

urlpatterns = patterns('',
    # ex: /core/login-redirect/
    url(r'^home/$', views.home, name='home'),
    #sale related URLS
    url(r'^new-sale/(?P<terminal_id>\d+)/$', views.newSale, name='newSale'),
    url(r'^new-sale/$', views.newSale, name='newSaleDefaultTerminal'),
    url(r'^newCustomerSale/(?P<customer_id>\d+)/$', views.newSaleFromCustomer, name='newSaleFromCustomer'),
    url(r'^save-sale/(?P<terminal_id>\d+)/$', views.saveSale, name='saveSale'),
    url(r'^open-sale/(?P<terminal_id>\d+)/(?P<sale_id>\d+)/$', views.openSale, name='openSale'),
    url(r'^payment-summary/(?P<sale_id>\d+)/$', views.printSummaryReceipt, name='printSummaryReceipt'),
    url(r'^payment-receipt/(?P<sale_id>\d+)/(?P<payment_grouping>\d+)/$', views.printPaymentReceipt, name='printPaymentReceipt'),
    url(r'^delivery-docket/(?P<sale_id>\d+)/$', views.printDeliveryDocket, name='printDeliveryDocket'),
    url(r'^proforma/(?P<sale_id>\d+)/$', views.printProformaInvoice, name='printProformaInvoice'),
    url(r'^tax/(?P<invoice_id>\d+)/$', views.printTaxInvoice, name='printTaxInvoice'),
    url(r'^deleteSale/(?P<sale_id>\d+)/$', views.deleteSale, name='deleteSale'),
    url(r'^searchSales/(?P<sale_type>[-\w]+)/$', views.searchSales, name='searchSales'),
    #eod related
    url(r'^new-eod/(?P<terminal_id>\d+)/$', views.newEOD, name='newEOD'),
    url(r'^save-eod/(?P<terminal_id>\d+)/$', views.saveEOD, name='saveEOD'),
    url(r'^open-eod/(?P<EOD_id>\d+)/$', views.openEOD, name='openEOD'),
    url(r'^search-eod/$', views.searchEOD, name='searchEOD'),
    #customer and accounts related.
    url(r'^customers/search/', views.CustomerSearchView.as_view(), name='searchCustomers'),
    url(r'^customer/search/ajax$', views.CustomerAjaxSearchView.as_view(), name='searchCustomerAjax'),
    url(r'^customer/new/$', views.CustomerCreateView.as_view(), name='createCustomer'),
    url(r'^customer/view/(?P<customer_id>\d+)$', views.viewCustomer, name='viewCustomer'),
    url(r'^customer/adjustLimit/(?P<customer_id>\d+)$', views.adjustCreditLimit, name='adjustCreditLimit'),
    url(r'^customer/update/(?P<pk>\d+)$', views.CustomerUpdateView.as_view(), name='updateCustomer'),
    url(r'^customer/delete/(?P<pk>\d+)$', views.CustomerDeleteView.as_view(), name='deleteCustomer'),
    url(r'^customer/(?P<customer_id>\d+)/pay/$', views.customerPayment, name='customerAccountPayment'),
    url(r'^customer/account-summary/(?P<customer_id>\d+)/$', views.printLedgerAccountSummary, name='printLedgerAccountSummary'),
    url(r'^customer/payment-receipt/(?P<customer_id>\d+)/(?P<payment_grouping>\d+)/$', views.printLedgerPaymentReceipt, name='printLedgerPaymentReceipt'),
    #payment method related
    url(r'^paymentMethod/new/$', views.PaymentMethodCreateView.as_view(), name='createPaymentMethod'),
    url(r'^paymentMethod/update/(?P<pk>\d+)$', views.PaymentMethodUpdateView.as_view(), name='updatePaymentMethod'),
    url(r'^paymentMethod/delete/(?P<pk>\d+)$', views.PaymentMethodDeleteView.as_view(), name='deletePaymentMethod'),
)
