from django.conf.urls import patterns, url

from stock import views

urlpatterns = patterns('',
    # ex: /core/login-redirect/
    url(r'^home/$', views.dashboard, name='dashboard'),
    #stocktakes
    url(r'^stocktake/dashboard/$', views.stockTakeHome, name='stockTakeHome'),
    url(r'^searchStockTake/(?P<type>[-\w]+)/$', views.searchStockTake, name='searchStockTake'),
    url(r'^stocktake/new/$', views.newStockTake, name='newStockTake'),
    url(r'^stocktake/new-barcode/$', views.newBarcodeStockTake, name='newBarcodeStockTake'),
    url(r'^stocktake/stocktake-from-barcode/$', views.stocktakeFromBarcodeDump, name='stocktakeFromBarcodeDump'),
    url(r'^stocktake/new/$', views.newStockTake, name='newStockTake'),
    url(r'^stocktake/save/$', views.saveStockTake, name='saveStockTake'),
    url(r'^stocktake/open/(?P<stocktake_id>\d+)/$', views.openStockTake, name='openStockTake'),
    #claims
    url(r'^claim/dashboard/$', views.claimHome, name='claimHome'),
    url(r'^searchClaim/(?P<type>[-\w]+)/$', views.searchClaim, name='searchClaim'),
    url(r'^claim/new/$', views.newClaim, name='newClaim'),
    url(r'^claim/save/$', views.saveClaim, name='saveClaim'),
    url(r'^claim/open/(?P<claim_id>\d+)/$$', views.openClaim, name='openClaim'),
    #movements
    url(r'^movement/create/$', views.ManualStockMovementCreateView.as_view(), name='createMovement'),
    url(r'^searchInventory/$', views.InventoryAjaxLookupView.as_view(), name='searchInventory'),
    # url(r'^brand/view/(?P<pk>\d+)$', views.BrandDetailView.as_view(), name='viewBrand'),
    # url(r'^brand/update/(?P<pk>\d+)$', views.BrandUpdateView.as_view(), name='updateBrand'),
    # url(r'^brand/delete/(?P<pk>\d+)$', views.BrandDeleteView.as_view(), name='deleteBrand'),
	#merchandiser urls
    url(r'^merchandiser/lookup/$', views.ProductPriceLookupView.as_view(), name='merchandiser'),
    url(r'^merchandiser/view-product/(?P<pk>\d+)$', views.ProductDetailView.as_view(), name='viewProduct'),
)
