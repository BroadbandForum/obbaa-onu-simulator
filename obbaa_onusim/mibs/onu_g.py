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

"""ONU-G MIB (G.988 9.1.1).
"""

from ..actions.get import get_action
from ..actions.set import set_action
from ..actions.other import reboot_action, test_action, sync_time_action
from ..mib import MIB, Alarm, Attr, Change, M, O, R, RW, \
    test_result_notification
from ..types import Bits, Bool, Enum, Number, String

#: Instantiated `MIB`.
onu_g_mib = MIB(256, 'ONU-G', 'Represents the ONU as equipment', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'vendor_id', 'Vendor ID', R, M, Number(4)),
    Attr(2, 'version', 'Version', R, M, String(14, default='v1')),
    Attr(3, 'serial_number', 'Serial number', R, M, (String(4), Number(4))),
    Attr(4, 'traffic_management', 'Traffic management option', R, M, Enum(1, (
        'priority-controlled', 'rate-controlled',
        'priority-and-rate-controlled'))),
    # XXX should be able to indicate 'deprecated', 'obsoleted' etc. and then
    #     could provide options controlling whether they're implemented
    # Attr(5, 'deprecated0', 'Deprecated', R, O, Number(1, fixed=0)),
    Attr(6, 'battery_backup', 'Battery backup', RW, M, Bool(1)),
    Attr(7, 'admin_state', 'Administrative state', RW, M,
         Enum(1, ('unlock', 'lock'))),
    Attr(8, 'oper_state', 'Operational state', R, O,
         Enum(1, ('enabled', 'disabled'))),
    Attr(9, 'survival_time', 'ONU survival time', R, O, Number(1, units='ms')),
    Attr(10, 'logical_onu_id', 'Logical ONU ID', R, O, String(24, default='')),
    Attr(11, 'logical_password', 'Logical password', R, O,
         String(12, default='')),
    Attr(12, 'credentials_status', 'Credentials status', RW, O,
         Enum(1, ('initial', 'successful', 'loid-error', 'password-error',
                  'duplicate-loid'))),
    Attr(13, 'extended_tc_options', 'Extended TC-layer options', R, O,
         Bits(1, ('annex-c', 'annex-d')))
), actions=(
    get_action, set_action, reboot_action, test_action, sync_time_action
), notifications=(
    test_result_notification,
), changes=(
    Change(8, 'oper_state'),
    Change(10, 'logical_onu_id'),
    Change(11, 'logical_password')
), alarms=(
    Alarm(0, 'equipment', 'Equipment alarm'),
    Alarm(1, 'powering', 'Powering Alarm')
))
