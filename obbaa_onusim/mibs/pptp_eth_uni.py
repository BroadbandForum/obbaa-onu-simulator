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

"""Physical Path Termination Point Ethernet UNI MIB (G.988 9.5.1).
"""

from ..actions.get import get_action
from ..actions.set import set_action
from ..mib import MIB, Alarm, Attr, Change, M, O, R, RW
from ..types import Enum, Number

#: Instantiated `MIB`.
pptp_eth_uni_mib = MIB(11, 'PPTP_ETH_UNI', 'Represents a physical ethernet interface', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'expected_type', 'Expected Type', RW, M, Number(1)),
    Attr(2, 'sensed_type', 'Sensed Type', R, O, Number(1)),
    Attr(3, 'auto_detection_conf', 'Auto Detection Configuration', RW, M, Number(1)),
    Attr(4, 'eth_loop_conf', 'Ethernet Loopback Configuration', RW, M, Number(1)),
    Attr(5, 'admin_state', 'Administrative state', RW, M,
         Enum(1, ('unlock', 'lock'))),
    Attr(6, 'oper_state', 'Operational state', R, O,
         Enum(1, ('enabled', 'disabled'))),
    Attr(7, 'config_ind', 'Configuration Ind', R, M, Number(1)),
    Attr(8, 'max_frame_size', 'Max Frame Size', RW, M, Number(2)),
    Attr(9, 'dte_dce_ind', 'DTE or DCE ind', RW, M, 
         Enum(1, ('dce_mdix', 'dte_mdi', 'auto'))),
    Attr(10, 'pause_time', 'Pause Time', RW, O, Number(2)),
    Attr(11, 'bridged_ip_ind', 'Bridged or IP Ind', RW, O,
         Enum(1, ('bridged', 'ip_router', 'depends_on_circuit_pack'))),
    Attr(12, 'arc', 'ARC', RW, O, Number(1)),
    Attr(13, 'arc_interval', 'ARC Interval', RW, O, Number(1)),
    Attr(14, 'pppoe_filter', 'PPPoE filter', RW, O,
         Enum(1, ('allow-all', 'pppoe-only'))),
    Attr(15, 'power_control', 'Power Control', RW, O,
         Enum(1, ('enabled', 'disabled')))
), actions=(
    get_action, set_action
), changes=(
    Change(2,  'sensed_type'),
    Change(6,  'op_state'),
    Change(12, 'arc_timer_expiration')
), alarms=(
    Alarm(0,'lan_los','No carrier at the Ethernet UNI','Loss of signal'),
))
