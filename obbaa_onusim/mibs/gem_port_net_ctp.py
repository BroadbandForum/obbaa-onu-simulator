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

"""GEM Port Network CTP Data MIB (G.988 9.2.3).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Alarm, Attr,Change, M, R, RWC, O
from ..types import Enum,Number
 
#: Instantiated `MIB`.
gem_port_net_ctp_mib = MIB(268, 'GEM_PORT_NET_CTP', 'GEM Port Network CTP ', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'port_id', 'Port ID', RWC, M, Number(2)),
    Attr(2, 'tcont_ptr', 'TCONT Pointer', RWC, M, Number(2)),
    Attr(3, 'direction', 'Direction', RWC, M, Number(1)),
    Attr(4, 'traffic_mgmt_ptr_us', 'Traffic Management Pointer for US', RWC, M, Number(2)),
    Attr(5, 'traffic_desc_prof_ptr_us', 'Traffic Descriptor Profile Pointer for US', RWC, O, Number(2)),
    Attr(6, 'uni_count', 'Uni counter', R, O, Number(1)),
    Attr(7, 'pri_queue_ptr_ds', 'Priority Queue Pointer for downstream', RWC, M, Number(2)),
    Attr(8, 'encryption_state', 'Encryption State', R, O, Number(1)),
    Attr(9, 'traffic_desc_prof_ptr_ds', 'Traffic Descriptor profile pointer for DS', RWC, O, Number(2)),
     Attr(10, 'encryption_key_ring', 'Encryption Key Ring', RWC, O,
         Enum(1,('no_encryption',
               'unicast_encryption_both_dir',
               'broadcast_encryption',
               'unicast_encryption_ds'))),


), actions=(
    get_action, set_action, create_action, delete_action
),alarms=(
    Alarm(5,'end-to-end_loss_of_continuity',
    'Loss of continuity can be detected when the GEM port network CTP supports a GEM interworking termination point'),
))
