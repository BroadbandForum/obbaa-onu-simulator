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

"""Mac Bridge Service Profile MIB (G.988 9.3.1).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC, O
from ..types import Number
 
#: Instantiated `MIB`.
mac_bridge_svc_prof_mib = MIB(45, 'MAC_BRIDGE_SVC_PROF', 'MAC Bridge Service Profile', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'spanning_tree_ind', 'Spanning Tree Indication (bool)', RWC, M, Number(1)),
    Attr(2, 'learning_ind', 'Learning Indication (bool)', RWC, M, Number(1)),
    Attr(3, 'port_bridging_ind', 'Port Bridging Indication (bool)', RWC, M, Number(1)),
    Attr(4, 'pri', 'Priority', RWC, M, Number(2)),
    Attr(5, 'max_age', 'Max Age', RWC, M, Number(2)),
    Attr(6, 'hello_time', 'Hello Time', RWC, M, Number(2)),
    Attr(7, 'forward_delay', 'Forward Delay', RWC, M, Number(2)),
    Attr(8, 'unknown_mac_addr_discard', 'Unknown MAC Address Discard (Bool)', RWC, M, Number(1)),
    Attr(9, 'mac_learning_depth', 'MAC Learning Depth', RWC, O, Number(1)),
    Attr(10, 'dynamic_filtering_ageing_time', 'Dynamic Filtering Ageing Time', RWC, O, Number(4)),

), actions=(
    get_action, set_action, create_action, delete_action
))
