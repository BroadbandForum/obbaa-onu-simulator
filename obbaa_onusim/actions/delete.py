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

"""  Delete action
"""


import functools
import logging
import operator

from .. import util

from ..action import Action
from ..message import Message
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class Delete(Message):
    """MIB upload command message.
    """

    def process(self, server: object) -> 'Delete':


        func_delete = server.database.delete(self.onu_id, self.me_class,
                                         self.me_inst, extended=self.extended)

        make_delete = Delete_action(cterm_name=self.cterm_name,
                                     onu_id=self.onu_id,
                                     extended=self.extended, tci=self.tci,
                                     me_class=self.me_class,
                                     me_inst=self.me_inst,
                                     num_upload_nexts=func_delete.num_upload_nexts)
        return make_delete


# XXX note that there's no 'reason' field
class Delete_action(Message):
    """mib delete message.
     """
    def encode_contents(self) -> bytearray:
        contents = Number(1).encode(self.reason)
        return contents

    def decode_contents(self, contents) -> FieldDict:

        reason, _ = Number(1).decode(contents, 0)
        return {'reason': reason}




delete_action = Action(6, 'delete', 'Delete action', Delete, Delete_action)

##Passa por aqui
