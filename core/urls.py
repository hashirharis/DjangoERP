from django.conf.urls import patterns, url

from core import views, signals

urlpatterns = patterns('',
    url(r'^home/$', views.home, name="home"),
    #product CRUD
    url(r'^product/create/$', views.ProductCreateView.as_view(), name='createProduct'),
    url(r'^warranty/create/$', views.WarrantyCreateView.as_view(), name='createWarranty'),
    url(r'^product/view/(?P<pk>\d+)$', views.ProductDetailView.as_view(), name='viewProduct'),
    url(r'^product/calculation-summary/$', views.ProductCalculationSummaryView.as_view(), name='getProductCalcSummary'),
    url(r'^product/update/(?P<pk>\d+)$', views.ProductUpdateView.as_view(), name='updateProduct'),
    url(r'^warranty/update/(?P<pk>\d+)$', views.WarrantyUpdateView.as_view(), name='updateWarranty'),
    url(r'^product/delete/(?P<pk>\d+)$', views.ProductDeleteView.as_view(), name='deleteProduct'),
    #product list
    url(r'^product/pricelookup/$', views.ProductPriceLookupView.as_view(), name='priceLookup'),
    url(r'^product/search/$', views.ProductPriceBookLookup.as_view(), name='searchProducts'),
    url(r'^product/search/ajax/$', views.ProductAjaxLookupView.as_view(), name='searchProductsAjax'),
    #product deals CRUD
    url(r'^product/(?P<product_id>\d+)/deals/$', views.ProductDealSearchView.as_view(), name='searchProductDeals'),
    url(r'^product/(?P<product_id>\d+)/deals/create/$', views.ProductDealCreateView.as_view(), name='createProductDeal'),
    url(r'^discount/update/(?P<pk>\d+)$', views.ProductDealUpdateView.as_view(), name='updateProductDeal'),
    url(r'^discount/delete/(?P<pk>\d+)$', views.ProductDealDeleteView.as_view(), name='deleteProductDeal'),
    #tags CUD
    url(r'^tag/update/(?P<pk>\d+)$', views.ProductTagUpdateView.as_view(), name='updateProductTag'),
    url(r'^tag/delete/(?P<pk>\d+)$', views.ProductTagDeleteView.as_view(), name='deleteProductTag'),
    url(r'^tag/create/$', views.ProductTagCreateView.as_view(), name='createProductTag'),
    #tags list
    url(r'^tags/search/$', views.ProductTagSearchView.as_view(), name='searchProductTags'),
    #brand CRUD
    url(r'^brand/create/$', views.BrandCreateView.as_view(), name='createBrand'),
    url(r'^brand/view/(?P<pk>\d+)$', views.BrandDetailView.as_view(), name='viewBrand'),
    url(r'^brand/update/(?P<pk>\d+)$', views.BrandUpdateView.as_view(), name='updateBrand'),
    url(r'^brand/delete/(?P<pk>\d+)$', views.BrandDeleteView.as_view(), name='deleteBrand'),
    #brand list
    url(r'^brand/search/$', views.BrandSearchView.as_view(), name='searchBrands'),
    #product categories CRUD
    url(r'^category/create/$', views.ProductCategoryCreateView.as_view(), name='createProductCategory'),
    url(r'^category/update/(?P<pk>\d+)$', views.ProductCategoryUpdateView.as_view(), name='updateProductCategory'),
    url(r'^category-markup/update/(?P<pk>\d+)$', views.ProductCategoryMarkupUpdateView.as_view(), name='updateProductCategoryMarkup'),
    url(r'^category/delete/(?P<pk>\d+)$', views.ProductCategoryDeleteView.as_view(), name='deleteProductCategory'),
    #product categories list
    url(r'^category/search/$', views.ProductCategoryListView.as_view(), name='searchProductCategory'),
    #vendor bonus'
    url(r'^vendorBonus/(?P<brand_id>\d+)/create/$', views.VendorBonusCreateView.as_view(), name='createVendorBonus'),
    url(r'^vendorBonus/update/(?P<pk>\d+)$', views.VendorBonusUpdateView.as_view(), name='updateVendorBonus'),
    url(r'^vendorBonus/delete/(?P<pk>\d+)$', views.VendorBonusDeleteView.as_view(), name='deleteVendorBonus'),
    #vendor bonus list
    url(r'^vendorBonus/(?P<brand_id>\d+)/search/$', views.VendorBonusSearchView.as_view(), name='searchVendorBonus'),
)
