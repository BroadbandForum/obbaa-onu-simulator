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

"""Onu remote debug MIB (G.988 9.3.11).
"""
from ..actions.create import create_action
from ..actions.set import set_action
from ..actions.get import get_action, get_next_action
from ..actions.delete import delete_action
from ..mib import MIB, Attr, M, R, RWC, RW
from ..types import Number, Bytes, Table
 
#: Instantiated `MIB`.
onu_remote_debug_mib = MIB(158, 'Onu_Remote_Debug', 'onu_remote_debug', attrs=(
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
    Attr(1, 'Command_format', 'command_format', RWC, M, Number(1)),
    Attr(2, 'Command_Onu', 'command_send_to_onu', RWC, M, Bytes(24)),
    Attr(3, 'reply_table', 'Reply_table', RW, M, Table(25))
), actions=(
    get_action, set_action, create_action, delete_action, get_next_action
))
