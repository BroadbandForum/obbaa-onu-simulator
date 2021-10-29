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

"""Extended VLAN tagging operation configuration data MIB (G.988 9.3.13).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, RWC, RW, R, O
from ..types import Enum, Number, Bytes
 
#: Instantiated `MIB`.
extended_vlan_tag_op_conf_data_mib = MIB(171, 'EXT_VLAN_TAG_OP_CONF_DATA', 'Extended VLAN Tagging Operation Configuration Data', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'association_type', 'Association Type', RWC, M, Number(1)),
    Attr(2, 'received_frame_vlan_tag_op_table_max_size', 'Received Frame VLAN tagging operation table max size', 
    	R, M, Number(2, fixed=1)),
    Attr(3, 'input_tpid', 'Input TPID', RW, M, Number(2)),
    Attr(4, 'output_tpid', 'Output TPID', RW, M, Number(2)),
    Attr(5, 'downstream_mode', 'Downstream Mode', RW, M, Number(1)),
    Attr(6, 'received_frame_vlan_tag_op_table', 'Received Frame VLAN Tagging Operation Table', 
    	RW, M, Bytes(16)),
    Attr(7, 'associated_me_ptr', 'Associated ME Pointer', RWC, M, Number(2)),
    Attr(8, 'dscp_pbit_mapping', 'DSCP to Pbit Mapping', RW, O, Bytes(24)),
    Attr(9, 'enhanced_mode', 'Enhanced Mode', RWC, O, 
    	Enum(1, 'false', 'true')),
    Attr(10, 'enhanced_received_classification_processing_table', 'Enhanced Received Classification and Operation Table', 
    	RW, M, Bytes(16))
), actions=(
    get_action, set_action, create_action, delete_action
))
