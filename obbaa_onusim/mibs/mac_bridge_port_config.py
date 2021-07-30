# Copyright 2021 Broadband Forum
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

"""MAC Brigde Port Configuration Data MIB (G.988 9.3.4).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Alarm, Attr, M, R, RWC, RW, O
from ..types import Number, Bytes, Bool
 
#: Instantiated `MIB`.
mac_bridge_port_conf_mib = MIB(47, 'MAC_BRIDGE_PORT_CONF', 'MAC Bridge Port Config Data', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'bridge_id_ptr', 'Bridge ID Pointer', RWC, M, Number(2)),
    Attr(2, 'port_num', 'Port Num', RWC, M, Number(1)),
    Attr(3, 'tp_type', 'TP Type', RWC, M, Number(1)),
    Attr(4, 'tp_ptr', 'TP Pointer', RWC, M, Number(2)),
    Attr(5, 'port_priority', 'Port Priority', RWC, O, Number(2)),
    Attr(6, 'port_path_cost', 'Port Path Cost', RWC, M, Number(2)),
    Attr(7, 'port_spanning_tree_ind', 'Port Spanning Tree Ind', RWC, M, Bool(1)),
    Attr(8, 'deprecated_1', 'Deprecated 1', RWC, O, Number(1)),
    Attr(9, 'deprecated_2', 'Deprecated 2', RWC, O, Number(1)),
    Attr(10, 'port_mac_addr', 'Port MAC Address', R, O, Bytes(6)),
    Attr(11, 'outbound_tp_ptr', 'Outbound TP Pointer', RW, O, Number(2)),
    Attr(12, 'inbound_tp_ptr', 'Inbound TP Pointer', RW, O, Number(2)),
    Attr(13, 'mac_learning_depth', 'MAC Learning Depth', RWC, O, Number(1)),
    Attr(14, 'lasp_id_ptr', 'LASP ID Pointer', RWC, O, Number(2)),
), actions=(
    get_action, set_action, create_action, delete_action
), alarms=(

))
