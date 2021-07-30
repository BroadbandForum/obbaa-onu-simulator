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

"""Priority Queue MIB (G.988 9.2.10).
"""
from ..actions.set import set_action
from ..actions.get import get_action
from ..mib import MIB, Attr, Alarm, M, R, RW, RWC, O
from ..types import Number, Bytes, Enum
 
#: Instantiated `MIB`.
priority_queue_mib = MIB(277, 'PRIORITY_QUEUE', 'Priority Queue', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'queue_configuration_option', 'Queue Configuration Option', 
    	R, M, Number(1, fixed=0)),
    Attr(2, 'max_queue_size', 'Maximum Queue Size', R, M, Number(2, fixed=100)),
    Attr(3, 'allocated_queue_size', 'Allocated Queue Size', RW, M, Number(2)),
    Attr(4, 'discard_block_counter_rst_interval', 'Discard-block Counter Reset Interval', 
    	RW, O, Number(2)),
    Attr(5, 'threshold_val_discarded_blocks_due_buffer_overflow', 
    	'Threshold Value for Discarded Blocks due to Buffer Overflow', RWC, O, Number(2)),
    Attr(6, 'related_port', 'Related Port', RW, M, Number(4)),
    Attr(7, 'traffic_scheduler_ptr', 'Traffic Scheduller Pointer', RW, M, Number(2)),
    Attr(8, 'weight', 'Weight', RW, M, Number(1)),
    Attr(9, 'back_pressure_op', 'Back Pressure Operation', RW, M, Number(2)),
    Attr(10, 'back_pressure_time', 'Back Pressure Time', RW, M, Number(4)),
    Attr(11, 'back_pressure_occur_queue_threshold', 'Back Pressure Occur Queue Threshold', 
    	RW, M, Number(2)),
    Attr(12, 'back_pressure_clear_queue_threshold', 'Back Pressure Clear Queue Threshold', 
    	RW, M, Number(2)),
    Attr(13, 'packet_drop_queue_threshold', 'Packet Drop Queue Threshold', RW, O, Bytes(8)),
    Attr(13, 'packet_drop_max_p', 'Packet Drop Max_p', RW, O, Number(2)),
    Attr(14, 'queue_drop_w_q', 'Queue Drop w_p', RW, O, Number(1)),
    Attr(15, 'drop_precedence_colour_marking', 'Drop President Colour Marking', RW, O, 
    	Enum(1, ('no_marking',
    		 'internal_marking',
    		 'dei',
    		 'pcp_8p0d',
    		 'pcp_7p1d',
    		 'pcp_6p2d',
    		 'pcp_5p3d',
    		 'dscp_af_class')))
), actions=(
    get_action, set_action
), alarms=(
    Alarm(0, 'block_loss', 'Content loss in excess of threshold'),
))
