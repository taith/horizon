import operator

from django.utils.translation import ugettext_lazy as _
from django.core.context_processors import csrf

from horizon import tabs

from openstack_dashboard.api import ceilometer

from .tables import (DiskUsageTable, NetworkTrafficUsageTable,
                     CpuUsageTable, ObjectStoreUsageTable, NetworkUsageTable)


class DiskUsageTab(tabs.TableTab):
    table_classes = (DiskUsageTable,)
    name = _("Global Disk Usage")
    slug = "global_disk_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_disk_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_disk_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class NetworkTrafficUsageTab(tabs.TableTab):
    table_classes = (NetworkTrafficUsageTable,)
    name = _("Global Network Traffic Usage")
    slug = "global_network_traffic_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_traffic_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_network_traffic_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class NetworkUsageTab(tabs.TableTab):
    table_classes = (NetworkUsageTable,)
    name = _("Global Network Usage")
    slug = "global_network_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_network_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_network_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class CpuUsageTab(tabs.TableTab):
    table_classes = (CpuUsageTable,)
    name = _("Global CPU Usage")
    slug = "global_cpu_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_cpu_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_cpu_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class GlobalObjectStoreUsageTab(tabs.TableTab):
    table_classes = (ObjectStoreUsageTable,)
    name = _("Global Object Store Usage")
    slug = "global_object_store_usage"
    template_name = ("horizon/common/_detail_table.html")

    def get_global_object_store_usage_data(self):
        request = self.tab_group.request
        result = sorted(ceilometer.global_object_store_usage(request),
                        key=operator.itemgetter('tenant', 'user'))
        return result


class StatsTab(tabs.Tab):
    name = _("Stats")
    slug = "stats"
    template_name = ("monitoring/vmcompute/stats.html")

    def get_context_data(self, request):
        context = {}
        meter_list = ceilometer.meter_list(self.request)

        meters = []
        meter_types = [
            ("Compute (Nova)", [
                {"name": "cpu", "unit": "ns", "type": "cumulative"},
                {"name": "disk.read.requests", "unit": "requests", "type": "cumulative"},
                {"name": "disk.read.bytes", "unit": "B", "type": "cumulative"},
                {"name": "disk.write.bytes", "unit": "B", "type": "cumulative"},
                {"name": "disk.write.requests", "unit": "requests", "type": "cumulative"}, 
                {"name": "network.incoming.bytes", "unit": "B",
                         "type": "cumulative"},
                {"name": "network.outgoing.bytes", "unit": "B",
                         "type": "cumulative"},
                {"name": "network.incoming.packets", "unit": "packets",
                         "type": "cumulative"},
                {"name": "network.outgoing.packets", "unit": "packets",
                         "type": "cumulative"}])
        ]

        # grab different resources for metrics,
        # and associate with the right type
        meters = ceilometer.meter_list(self.request)
        metersx = ceilometer.Meters(request)
        if not metersx._ceilometer_meter_list:
            msg = _("There are no meters defined yet.")
            messages.warning(request, msg)
        resources = {}
        for meter in meters:
            # group resources by meter names
            if meter.type=='delta' or meter.type=='cumulative':
                if meter.name not in resources:
                    resources[meter.name] = []
                if meter.resource_id not in resources[meter.name]:
                    resources[meter.name].append(meter.resource_id)

        context = {'meters': meter_types, 'resources': resources}
        context.update(csrf(request))
        return context

class CeilometerOverviewTabs(tabs.TabGroup):
    slug = "ceilometer_overview"
    tabs = (DiskUsageTab, NetworkTrafficUsageTab, NetworkUsageTab,
            GlobalObjectStoreUsageTab, CpuUsageTab, StatsTab,)
    sticky = True
