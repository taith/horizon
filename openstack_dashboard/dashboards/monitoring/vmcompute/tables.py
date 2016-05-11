import logging
import re

from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon.templatetags.sizeformat import filesizeformat, float_format


LOG = logging.getLogger(__name__)


class StringWithPlusOperation(str):
    """Override "+" operation for string object to make."""
    def __init__(self, *args, **kwargs):
        super(StringWithPlusOperation, self).__init__(*args, **kwargs)

    def _split_str(self, string):
        """
        Split a string to two parts.
        The first group is the float number and
        the second one is a string like unit name.
        """
        result = re.search(r'^([-+]?[0-9]*\.?[0-9]+)(.*)$', string)
        if result:
            number = float(result.groups()[0])
            unit = result.groups()[1]
            return number, unit
        return None, None


    def to_bytes(self, number, unit):
        if unit=="PB":
            bytes = number * (1024 * 1024 * 1024 * 1024 * 1024)
        elif unit=="TB":
            bytes = number * (1024 * 1024 * 1024 * 1024)
        elif unit=="GB":
            bytes = number * (1024 * 1024 * 1024)
        elif unit=="MB":
            bytes = number * (1024 * 1024)
        elif unit=="KB":
            bytes = number * (1024)
        else:
            bytes = number

        return bytes


    def __radd__(self, another):
        num_x, unit_x = self._split_str(self)
        num_y = 0
        unit_y = ""

        if isinstance(another, (int, float)):
            num_y = another
        elif isinstance(another, basestring):
            num_y, unit_y = self._split_str(another)
        elif isinstance(another, self.__class__):
            num_y, unit_y = self._split_str(another.__str__())

        if num_y is None or num_x is None:
            return '-'

        unit_x = unit_x.strip()
        unit_y = unit_y.strip()

        if unit_x == unit_y:
            return "%s%s" % (num_x + num_y, unit_x)
        else:
            converted_num_x = self.to_bytes(num_x, unit_x)
            converted_num_y = self.to_bytes(num_y, unit_y)

            total = converted_num_x + converted_num_y
            result = filesizeformat(total, float_format)
            return result


class StringWithPlusOperationForTime(str):
    """Override "+" operation for string object to make."""
    def __init__(self, *args, **kwargs):
        super(StringWithPlusOperationForTime, self).__init__(*args, **kwargs)

    def __radd__(self, another):
        seconds1 = sum(int(x) * 60 ** i for i, x
                        in enumerate(reversed(self.split(":"))))
        if isinstance(another, (int, float)):
            seconds2 = another
        else:
            seconds2 = sum(int(x) * 60 ** i for i, x
                        in enumerate(reversed(another.split(":"))))

        total_time = seconds1 + seconds2
        converted = "%02d:%02d:%02d" % \
            reduce(lambda a, b: divmod(a[0], b) + a[1:],
                   [(total_time,), 60, 60])

        return str(converted)


class DiskUsageFilterAction(tables.FilterAction):
    def filter(self, table, tenants, filter_string):
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.name.lower():
                return True
            return False

        return filter(comp, tenants)


def get_bytes(field_name=""):
    def transform(sample):
        field = getattr(sample, field_name, None)
        result = filesizeformat(field, float_format)
        return StringWithPlusOperation(result)
    return transform


class  DiskUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"), sortable=True)
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource", verbose_name=_("Resource"), sortable=True)
    disk_read_bytes = tables.Column(get_bytes("disk_read_bytes"),
                                    verbose_name=_("Disk Read Bytes"),
                                    summation="sum",
                                    sortable=True)
    disk_read_requests = tables.Column("disk_read_requests",
                                       verbose_name=_("Disk Read Requests"),
                                       summation="sum",
                                       sortable=True)
    disk_write_bytes = tables.Column(get_bytes("disk_write_bytes"),
                                     verbose_name=_("Disk Write Bytes"),
                                     summation="sum",
                                     sortable=True)
    disk_write_requests = tables.Column("disk_write_requests",
                                        verbose_name=_("Disk Write Requests"),
                                        summation="sum",
                                        sortable=True)
    def get_object_id(self, datum):
        return datum.tenant + datum.user + datum.resource

    class Meta:
        name = "global_disk_usage"
        verbose_name = _("Global Disk Usage")
        table_actions = (DiskUsageFilterAction,)
        multi_select = False


class NetworkTrafficUsageFilterAction(tables.FilterAction):
    def filter(self, table, tenants, filter_string):
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.name.lower():
                return True
            return False

        return filter(comp, tenants)

class NetworkTrafficUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    network_incoming_bytes = tables.Column(get_bytes("network_incoming_bytes"),
                                   verbose_name=_("Network incoming Bytes"),
                                   summation="sum",
                                   sortable=True)
    network_incoming_packets = tables.Column("network_incoming_packets",
                            verbose_name=_("Network incoming Packets"),
                            summation="sum", sortable=True)
    network_outgoing_bytes = tables.Column(get_bytes("network_outgoing_bytes"),
                            verbose_name=_("Network Outgoing Bytes"),
                            summation="sum", sortable=True)
    network_outgoing_packets = tables.Column("network_outgoing_packets",
                            verbose_name=_("Network Outgoing Packets"),
                            summation="sum", sortable=True)

    def get_object_id(self, datum):
        return datum.tenant + datum.user + datum.resource

    class Meta:
        name = "global_network_traffic_usage"
        verbose_name = _("Global Network Traffic Usage")
        table_actions = (NetworkTrafficUsageFilterAction,)
        multi_select = False

class CpuUsageFilterAction(tables.FilterAction):
    def filter(self, table, tenants, filter_string):
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.name.lower():
                return True
            return False

        return filter(comp, tenants)


def get_cpu_time(sample):
    cpu_seconds = sample.cpu / 1000000000
    formatted_time = "%02d:%02d:%02d" % \
        reduce(lambda a, b: divmod(a[0], b) + a[1:], [(cpu_seconds,), 60, 60])
    return StringWithPlusOperationForTime(formatted_time)


class CpuUsageTable(tables.DataTable):
    tenant = tables.Column("tenant", verbose_name=_("Tenant"))
    user = tables.Column("user", verbose_name=_("User"), sortable=True)
    instance = tables.Column("resource",
                             verbose_name=_("Resource"),
                             sortable=True)
    cpu = tables.Column(get_cpu_time,
                        verbose_name=_("CPU time"),
                        summation="sum",
                        sortable=True)
    cpu_util = tables.Column("cpu_util", verbose_name=_("Average CPU (%)"), sortable=True)
    vcpus = tables.Column("vcpus", verbose_name=_("Number of virtual CPUs"), sortable=True)
    memory = tables.Column("memory", verbose_name=_("Memory (MB)"), sortable=True)
    memory_usage = tables.Column("memory_usage", verbose_name=_("Memory Use (MB)"), sortable=True)

    def get_object_id(self, datum):
        return datum.tenant + datum.user + datum.resource

    class Meta:
        name = "global_cpu_usage"
        verbose_name = _("Global CPU Usage")
        table_actions = (CpuUsageFilterAction,)
        multi_select = False
