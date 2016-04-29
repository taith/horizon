from django.utils.translation import ugettext_lazy as _

import horizon


class Monitoring(horizon.Dashboard):
    name = _("Monitoring")
    slug = "monitoring"
    panels = ('vmcompute')  # Add your panels here.
    default_panel = 'vmcompute'  # Specify the slug of the dashboard's default panel.


horizon.register(Monitoring)
