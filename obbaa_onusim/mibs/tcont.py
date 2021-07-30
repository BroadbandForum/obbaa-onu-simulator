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

"""T-CONT MIB (G.988 9.2.2).
"""

from ..actions.get import get_action
from ..actions.set import set_action
from ..mib import MIB,  Attr, M, R, RW
from ..types import Enum, Number

#: Instantiated `MIB`.
tcont_mib = MIB(262, 'T-CONT', 'Represents a T-CONT', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'alloc_id', 'Alloc ID', RW, M, Number(2, default=65535)),
    Attr(2, 'deprecated', 'Deprecated', R, M, Number(1, fixed=1)),
    Attr(3, 'policy', 'Policy', RW, M, Enum(1, ('Null', 'Strict priority', 'WRR')))
), actions=(
    get_action, set_action
))
