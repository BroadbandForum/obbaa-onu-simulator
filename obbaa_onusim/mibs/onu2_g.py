# Copyright 2020 Broadband Forum
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""ONU2-G MIB (G.988 9.1.2).
"""

from ..actions.get import get_action
from ..actions.set import set_action
from ..mib import MIB, Attr, Change, M, O, R, RW
from ..types import Bits, Enum, Number, String

enum_1_aes = Enum(1, ('reserved', 'aes-128'), default='aes-128')
conn_values = ('N:1', '1:M', '1:P', 'N:M', '1:MP', 'N:P', 'N:MP')

# noinspection PyPep8
#: Instantiated `MIB`.
onu2_g_mib = MIB(257, 'ONU2-G', 'Contains additional attributes associated '
                                'with a PON ONU', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'equipment_id', 'Equipment ID', R, O, String(20)),
    Attr(2, 'omcc_version', 'OMCC version', R, M, Number(1)),
    # XXX is vendor_product_code a string or number?
    Attr(3, 'vendor_product_code', 'Vendor product code', R, O, String(2)),
    Attr(4, 'security_capability', 'Security capability', R, M, enum_1_aes),
    Attr(5, 'security_mode', 'Security mode', RW, M, enum_1_aes),
    Attr(6, 'total_priority_queue_number', 'Total priority queue number', R, M,
         Number(2)),
    Attr(7, 'total_traf_sched_number', 'Total traffic scheduler number', R, M,
         Number(1)),
    # Attr(8, 'deprecated0', 'Deprecated', R, O, Number(1, fixed=0)),
    Attr(9, 'total_gem_port_number', 'Total GEM port-ID number', R, O,
         Number(2)),
    Attr(10, 'sys_up_time', 'SysUpTime', R, O, Number(4, units='10ms')),
    Attr(11, 'connectivity_capability', 'Connectivity capability', R, O,
         Bits(2, conn_values)),
    Attr(12, 'connectivity_mode', 'Current connectivity mode', RW, O,
         Enum(1, conn_values)),
    # XXX I couldn't be bothered to define good short bit names
    Attr(13, 'qos_config_flexibility', 'QoS configuration flexibility', R, O,
         Bits(2, ('1', '2', '3', '4', '5', '6'))),
    Attr(14, 'priority_queue_scale_factor', 'Priority queue scale factor', RW,
         O, Number(2))), actions=(get_action, set_action),
                 changes=(Change(2, 'omcc_version'),))
