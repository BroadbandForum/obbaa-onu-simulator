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

"""GAL Ethernet profile MIB (G.988 9.2.7).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC
from ..types import Number

#: Instantiated `MIB`.
gal_eth_prof_mib = MIB(272, 'GAL_ETH_PROF', 'GAL Ethernet Profile', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2, fixed=0)),
    Attr(1, 'max_gem_payload_size', 'Max GEM payload Size', RWC, M, Number(2))
), actions=(
    get_action, set_action, create_action, delete_action
))
