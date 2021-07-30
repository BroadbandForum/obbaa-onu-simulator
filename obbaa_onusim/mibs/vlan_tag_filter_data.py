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

"""VLAN tagging filter data MIB (G.988 9.3.11).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC
from ..types import Number, Bytes
 
#: Instantiated `MIB`.
vlan_tag_filter_data_mib = MIB(84, 'VLAN_TAG_FILTER_DATA', 'VLAN Tagging Filter Data', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'vlan_filter_list', 'VLAN Filter List', RWC, M, Bytes(24)),
    Attr(2, 'forward_operation', 'Forward Operation', RWC, M, Number(1)),
    Attr(3, 'number_of_entries', 'Number of Entries', RWC, M, Number(1))
), actions=(
    get_action, set_action, create_action, delete_action
))
