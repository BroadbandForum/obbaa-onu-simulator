# Copyright 2023 Broadband Forum
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

""" Ethernet Frame Performance Monitoring History Data Downstream (G.988 9.3.31).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC
from ..types import Number, Bytes, Bool
 
#: Instantiated `MIB`.
eth_frame_downstream_pm_mib = MIB(321, 'ETH_FRAME_DOWNSTREAM_PM', 'Ethernet Frame Performance Monitoring History Data Downstream', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'interval_end_time', 'Interval end time', R, M, Number(1)),
    Attr(2, 'threshold_data_1_2_ID', 'Threshold data 1/2 ID', RWC, M, Number(2)),
    Attr(3, 'drop_events', 'Drop events', R, M, Number(4)),
    Attr(4, 'octets', 'Octets', R, M, Number(4)),
    Attr(5, 'packets', 'Packets', R, M, Number(4)),
    Attr(6, 'broadcast_packets', 'Broadcast packets', R, M, Number(4)),
    Attr(7, 'multicast_packets', 'Multicast packets', R, M, Number(4)),
    Attr(8, 'crc_errored_packets', 'CRC errored packets', R, M, Number(4)),
    Attr(9, 'undersize_packets', 'Undersize packets', R, M, Number(4)),
    Attr(10, 'oversize_packets', 'Oversize packets', R, M, Number(4)),
    Attr(11, 'packets_64_octets', 'Packets 64 octets', R, M, Number(4)),
    Attr(12, 'packets_65_to_127_octets', 'Packets 65 to 127 octets', R, M, Number(4)),
    Attr(13, 'packets_128_to_255_octets', 'Packets 128 to 255 octets', R, M, Number(4)),
    Attr(14, 'packets_256_to_511_octets', 'Packets 256 to 511 octets', R, M, Number(4)),
    Attr(15, 'packets_512_to_1023_octets', 'Packets 512 to 1023 octets', R, M, Number(4)),
    Attr(16, 'packets_1024_to_1518_octets', 'Packets 1024 to 1518 octets', R, M, Number(4))
), actions=(
    get_action, set_action, create_action, delete_action
), alarms=(

))