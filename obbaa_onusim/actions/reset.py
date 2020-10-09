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

"""The MIB reset action's messages are defined in G.988 A.2.17-18 (
extended) and A.3.17-18 (baseline).

The relevant classes and instances are:

* `MibReset`: MIB reset command message class
* `MibResetResponse`: MIB reset response message class
* `mib_reset_action`: MIB reset action instance.
"""

import logging

from ..action import Action
from ..message import Message
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class MibReset(Message):
    """MIB reset command message.
    """

    def process(self, server: object) -> 'MibResetResponse':
        """Pass this message to the server database for processing,
        and return the response.
        """
        results = server.database.reset(self.onu_id, self.me_class,
                                        self.me_inst, extended=self.extended)

        response = MibResetResponse(cterm_name=self.cterm_name,
                                    onu_id=self.onu_id,
                                    extended=self.extended, tci=self.tci,
                                    me_class=self.me_class,
                                    me_inst=self.me_inst,
                                    reason=results.reason)
        return response


class MibResetResponse(Message):
    """MIB reset response message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(1).encode(self.reason)
        return contents

    def decode_contents(self, contents) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``reason``: result, reason; 0-255
        """
        reason, _ = Number(1).decode(contents, 0)
        return {'reason': reason}


mib_reset_action = Action(15, 'mib-reset', 'MIB reset action', MibReset,
                          MibResetResponse)
"""MIB reset `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
