from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from forms import LoginForm
from core import views
from bulletins import views as bulletinviews

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'br.views.home', name='home'),
    # url(r'^br/', include('br.foo.urls')),



    url(r'^$', views.home, name="home"),
    url(r'^admin/', include('users.urls', namespace="admin")),
    url(r'^pricebook/', include('core.urls', namespace="core")),
    url(r'^sales/', include('pos.urls', namespace="pos")),
    url(r'^b2b/', include('b2b.urls', namespace="b2b")),
    url(r'^stock/', include('stock.urls', namespace="stock")),
    url(r'^contacts/', include('tele.urls', namespace="tele")),
    url(r'^reports/', include('reports.urls', namespace="reports")),
    url(r'^core_stock/',include('ranges.urls',namespace="core_stock")),
    url(r'^bulletin-board/', include('bulletins.urls', namespace="bulletins")),
    url(r'^virtual-warehouse/', include('vw.urls', namespace="vw")),
    url(r'^uploads/', include('uploads.urls', namespace="uploads")),
    # Authentication functionality
    url(r'^login/$', 'django.contrib.auth.views.login', {'authentication_form':LoginForm}, 'login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/login/'}, 'logout')
)

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT, 'show_indexes': True}))
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.STATIC_ROOT, 'show_indexes': True}))