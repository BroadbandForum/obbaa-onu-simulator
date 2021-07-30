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

"""The MIB upload and MIB upload next actions' messages are defined in
G.988 A.2.13-16 (extended) and A.3.13-16 (baseline).

The relevant classes and instances are:

* `MibUpload` and `MibUploadNext`: MIB upload and MIB upload next command
  message classes
* `MibUploadResponse` and `MibUploadNextResponse`: MIB upload and MIB upload
  next response message classes
* `mib_upload_action` and `mib_upload_next_action`: MIB upload and MIB
  upload next action instances.
"""

import functools
import logging
import operator

from .. import util

from ..action import Action
from ..message import Message
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class Create(Message):
    """MIB upload command message.
    """

    def process(self, server: object) -> 'CreateResponse':

        print('\n\nThis is the create message!!!!!!!!!\n\n')
        # TODO: need to implement the create handler. For now just increment the mib_data_sync
        server.database.increment_mib_sync(self.onu_id)

        response = CreateResponse(cterm_name=self.cterm_name,
                                     onu_id=self.onu_id,
                                     extended=self.extended, tci=self.tci,
                                     me_class=self.me_class,
                                     me_inst=self.me_inst)
        return response


# XXX note that there's no 'reason' field
class CreateResponse(Message):
    """MIB upload response message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(0)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.
        """
        return {}




create_action = Action(4, 'create', 'Create action', Create, CreateResponse)
"""Create `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
