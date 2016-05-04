from django.utils.translation import ugettext_lazy as _

import horizon
from openstack_dashboard.dashboards.monitoring import dashboard

class Vmcompute(horizon.Panel):
    name = _("Virtual Machine Meter")
    slug = "vmcompute"


dashboard.Monitoring.register(Vmcompute)
