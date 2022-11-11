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

"""ONU data MIB (G.988 9.1.3).
"""

from ..actions.get import get_action
from ..actions.reset import mib_reset_action
from ..actions.set import set_action
from ..actions.upload import mib_upload_action, mib_upload_next_action
from ..actions.get_all_alarms import get_all_alarms_action, get_all_alarms_next_action
from ..mib import MIB, Attr, M, R, RW
from ..types import Number

#: Instantiated `MIB`.
onu_data_mib = MIB(2, 'ONU data', 'Models the MIB itself', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'mib_data_sync', 'MIB data sync', RW, M, Number(1))
), actions=(
    get_action, set_action, get_all_alarms_action, get_all_alarms_next_action,
    mib_reset_action, mib_upload_action, mib_upload_next_action
))
