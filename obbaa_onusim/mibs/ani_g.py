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
from ..mib import MIB, Alarm, Attr, Change, M, O, R, RW, Notification
from ..types import Enum, Number

#: Instantiated `MIB`.
ani_g_mib = MIB(263,'ANI_G', 'Represents a physical PON interface', attrs = (
        Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(1)),
        Attr(1, 'sr_indication', '', R, M, Number(1)),
        Attr(2, 'total_tcont_number', '', R, M, Number(2)),
        Attr(3, 'gem_block_length', '', RW, M, Number(2)),
        Attr(4, 'piggy_back_dba_reporting', '', R, M, Number(1)),
        Attr(5, 'deprecated', '', R, M, Number(1)),
        Attr(6, 'sf_threshold', '', RW, M, Number(1)),
        Attr(7, 'sd_threshold', '', RW, M, Number(1)),
        Attr(8, 'arc', '', RW, O, Number(1)),
        Attr(9, 'arc_interval', '', RW, O, Number(1)),
        Attr(10, 'optical_signal_level', '', R, O, Number(2)),
        Attr(11, 'lower_optical_threshold', '', RW, O, Number(1)),
        Attr(12, 'upper_optical_threshold', '', RW, O, Number(1)),
        Attr(13, 'onu_response_time', '', R, O, Number(2)),
        Attr(14, 'transmit_optical_level', '', R, O, Number(2)),
        Attr(15, 'lower_transmit_power_threshold', '', RW, O, Number(1)),
        Attr(16, 'upper_transmit_power_threshold', '', RW, O, Number(1)),
    )
    ,actions = (get_action, set_action
), notifications=(
    Notification(8,  'Alarm-reporting control cancellation'),

), alarms=(
            Alarm(0,'bbf-hardware-transceiver-alarm-types:rx-power-low','Low receive (RX) input power'),
            Alarm(1,'bbf-hardware-transceiver-alarm-types:rx-power-high','High receive (RX) input power'),
            Alarm(2,'bbf-obbaa-xpon-onu-alarm-types:signal-fail','Signal Fail'),
            Alarm(3,'bbf-obbaa-xpon-onu-alarm-types:signal-degraded','Signal Degraded'),
            Alarm(4,'bbf-hardware-transceiver-alarm-types:tx-power-low','Low transmit (TX) input power'),
            Alarm(5,'bbf-hardware-transceiver-alarm-types:tx-power-high','High transmit (TX) input power'),
            Alarm(6,'bbf-hardware-transceiver-alarm-types:tx-bias-high','High transmit (TX) bias current'),
))
