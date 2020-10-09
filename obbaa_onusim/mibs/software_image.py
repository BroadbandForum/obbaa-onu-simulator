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

"""Software image MIB (G.988 9.1.4).
"""

from ..actions.get import get_action
from ..actions.other import start_download_action, download_section_action, \
    end_download_action, activate_image_action, commit_image_action
from ..mib import MIB, Attr, Change, M, O, R
from ..types import Bool, Bytes, Number, String

#: Instantiated `MIB`.
software_image_mib = MIB(
        7, 'Software image', 'Models an executable software image', attrs=(
            Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
            Attr(1, 'version', 'Version', R, M, String(14)),
            Attr(2, 'is_committed', 'Is committed', R, M, Bool(1)),
            Attr(3, 'is_active', 'Is active', R, M, Bool(1)),
            Attr(4, 'is_valid', 'Is committed', R, M, Bool(1)),
            Attr(5, 'product_code', 'Product code', R, O, String(25)),
            # XXX is Bytes correct?
            Attr(6, 'image_hash', 'Image hash', R, O, Bytes(16))
        ), actions=(
            get_action, start_download_action, download_section_action,
            end_download_action, activate_image_action, commit_image_action
        ), changes=(
            Change(1, 'version'), Change(2, 'is_committed'),
            Change(3, 'is_active'), Change(4, 'is_valid'),
            Change(5, 'product_code'),
            Change(6, 'image_hash')
        )
)
