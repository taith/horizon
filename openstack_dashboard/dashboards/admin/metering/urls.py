from django.conf.urls import patterns
from django.conf.urls import url

from .views import IndexView, SamplesView, ExportView


urlpatterns = patterns('openstack_dashboard.dashboards.monitoring.vmcompute.views',
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^samples$', SamplesView.as_view(), name='samples'),
    url(r'^export$', ExportView.as_view(), name='export')
)
