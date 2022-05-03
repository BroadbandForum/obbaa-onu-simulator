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

"""GEM Interworking Termination Point Data MIB (G.988 9.2.4).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Alarm, Attr, Change, M, R, RWC, RW, O
from ..types import Enum,Number
 
#: Instantiated `MIB`.
gem_iw_tp_mib = MIB(266, 'GEM_INT_TER_POINT', 'GEM Interworking Termination Point Data ', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'gem_port_net_ctp_conn_ptr', 'GEM port network CTP connectivity pointer', RWC, M, Number(2)),
    Attr(2, 'iw_opt', 'Interworking option', RWC, M, Number(1)),
    Attr(3, 'svc_prof_ptr', 'Service profile pointer', RWC, M, Number(2)),
    Attr(4, 'iw_tp_ptr', 'Interworking termination point pointer', RWC, M, Number(2)),
    Attr(5, 'pptp_count', 'PPTP Counter', R, O, Number(1)),
    Attr(6, 'oper_state', 'Operational State', R, O,
    	Enum(1,('enabled','disabled'))),
    Attr(7, 'gal_prof_ptr', 'GAL Profile Pointer', RWC, M, Number(2)),
    Attr(8, 'gal_lpbk_config', 'GAL Loopback Config', RW, M,
    	Enum(1,('no_loopback','loopback_ds'))),

), actions=(
    get_action, set_action, create_action, delete_action
),changes=(
    Change(6,'op_state','operational state change'),
),alarms=(
    Alarm(0,'Deprecated','Deprecated'),
))
