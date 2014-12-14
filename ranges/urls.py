#!/usr/bin/env python
from django.conf.urls import patterns, url
from views import *


urlpatterns = patterns('',
    # ex: /core/login-redirect/
    url(r'^stock_range/(?P<month>\d+)/(?P<year>\d+)/$', StoreRangesView.as_view(), name='stock_range'),
    url(r'^stock_range/$', 'ranges.views.core_stock_main', name='stock_range'),
    url(r'^edit_ranges/(?P<month>\d+)/(?P<year>\d+)/$', EditRangesListView.as_view(), name='editRange'),
    url(r'^edit_ranges/$', 'ranges.views.editRangesMain', name='editRange'),
    url(r'^updatestock/(?P<pk>\d+)/$',StockRangeUpdateView.as_view() , name="updatestock"),
    url(r'^updateprodct/(?P<pk>\d+)/$',ProductRangeUpdateView.as_view() , name="updateprodct"),
    url(r'^storedetail/(?P<pk>\d+)/$',StoreDetailView.as_view() , name="storedetail"),
    url(r'^deleteproductrange/(?P<pk>\d+)/$',ProductRangeDeleteView.as_view(),name="deleteproductrange"),
    url(r'^deletestorerange/(?P<pk>\d+)/$',StoreRangeDeleteView.as_view(),name="deletestorerange"),
    
    )

