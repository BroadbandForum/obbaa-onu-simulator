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

"""IEEE 802.1p Mapper Service Profile MIB (G.988 9.3.10).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC, RW, O
from ..types import Enum, Number, Bytes
 
#: Instantiated `MIB`.
ieee_8021p_mapper_svc_prof_mib = MIB(130, 'IEEE_802_1P_MAPPER', 'IEEE 802.1p Mapper Service Profile', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'tp_ptr', 'TP pointer', RWC, M, Number(2)),
    Attr(2, 'iw_tp_ptr_pbit0', 'Interwork TP pointer for Pbit priority 0', RWC, M, Number(2)),
    Attr(3, 'iw_tp_ptr_pbit1', 'Interwork TP pointer for Pbit priority 1', RWC, M, Number(2)),
    Attr(4, 'iw_tp_ptr_pbit2', 'Interwork TP pointer for Pbit priority 2', RWC, M, Number(2)),
    Attr(5, 'iw_tp_ptr_pbit3', 'Interwork TP pointer for Pbit priority 3', RWC, M, Number(2)),
    Attr(6, 'iw_tp_ptr_pbit4', 'Interwork TP pointer for Pbit priority 4', RWC, M, Number(2)),
    Attr(7, 'iw_tp_ptr_pbit5', 'Interwork TP pointer for Pbit priority 5', RWC, M, Number(2)),
    Attr(8, 'iw_tp_ptr_pbit6', 'Interwork TP pointer for Pbit priority 6', RWC, M, Number(2)),
    Attr(9, 'iw_tp_ptr_pbit7', 'Interwork TP pointer for Pbit priority 7', RWC, M, Number(2)),
    Attr(10, 'unmarked_frame_option', 'Unmarked Frame option', RWC, M, 
    	Enum(1, ('derive_pcp_from_dscp',
    	         'set_pcp_by_default_pbit_assumption_attr'))),
    Attr(11, 'dscp_to_pbit_mapping', 'DSCP to Pbit Mapping', RW, M, Bytes(24)),
    Attr(12, 'default_pbit_assumption', 'Default Pbit Assumption', RWC, M, Number(1)),
    Attr(13, 'tp_type', 'TP Type', RWC, O, Number(1))
), actions=(
    get_action, set_action, create_action, delete_action
))
