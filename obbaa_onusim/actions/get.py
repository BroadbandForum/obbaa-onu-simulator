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

"""The Get action's messages are defined in G.988 A.2.7-8 (extended) and
A.3.7-8 (baseline).

The relevant classes and instances are:

* `Get`: Get command message class
* `GetResponse`: Get response message class
* `get_action`: Get action instance.
"""

import logging

from ..action import Action
from ..message import Message
from ..types import Bytes, Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


# XXX could add validate() to restrict attr_mask to supported attributes
class Get(Message):
    """Get command message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(self.attr_mask)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``attr_mask``: attribute mask; 0-65535
        """
        attr_mask, _ = Number(2).decode(contents, 0)
        return {'attr_mask': attr_mask}

    def process(self, server: object) -> 'GetResponse':
        results = server.database.get(self.onu_id, self.me_class,
                                      self.me_inst, self.attr_mask,
                                      extended=self.extended)

        response = GetResponse(cterm_name=self.cterm_name, onu_id=self.onu_id,
                               extended=self.extended, tci=self.tci,
                               me_class=self.me_class, me_inst=self.me_inst,
                               reason=results.reason,
                               attr_mask=results.attr_mask,
                               opt_attr_mask=results.opt_attr_mask,
                               attr_exec_mask=results.attr_exec_mask,
                               _attrs=results.attrs)
        return response


class GetResponse(Message):
    """Get response message.
    """

    def encode_contents(self) -> bytearray:
        extended = self.extended
        contents = bytearray()

        # reason and attr_mask always come first
        contents += Number(1).encode(self.reason)
        contents += Number(2).encode(self.attr_mask)

        # extended messages have opt_attr_mask and attr_exec_mask next
        if extended:
            contents += Number(2).encode(self.opt_attr_mask)
            contents += Number(2).encode(self.attr_exec_mask)

        # both baseline and extended messages have attribute values next
        attrs = self.get('_attrs', [])
        for attr, value in attrs:
            contents += attr.encode(value)

        # baseline messages have opt_attr_mask and attr_exec_mask last
        # (we assume that baseline response length restrictions have already
        # been applied, so len(contents) <= 25)
        if not extended:
            pad_length = 28 - len(contents)
            assert pad_length >= 0
            contents += Bytes(pad_length).encode()
            contents += Number(2).encode(self.opt_attr_mask)
            contents += Number(2).encode(self.attr_exec_mask)

        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``reason``: result, reason; 0-255
            * ``attr_mask``: attribute mask; 0-65535
            * ``opt_attr_mask``: optional-attribute mask; 0-65535
            * ``opt_exec_mask``: attribute execution mask; 0-65535
            * other: MIB-specific attributes as specified by the
              attribute mask
        """
        extended = self.extended
        offset = 0

        # reason always come first
        reason, offset = Number(1).decode(contents, offset)

        # if reason is non-zero, the command failed, and the rest of the
        # contents might not be present
        # XXX reason is present in all responses? should handle generically?
        # XXX should capture any trailing content (in the event of error)

        # attr_mask always comes next
        attr_mask, offset = Number(2).decode(contents, offset)

        # extended messages have opt_attr_mask and attr_exec_mask next
        opt_attr_mask, opt_exec_mask = 0x0000, 0x0000
        if extended:
            opt_attr_mask, offset = Number(2).decode(contents, offset)
            opt_exec_mask, offset = Number(2).decode(contents, offset)

        # both baseline and extended messages have attribute values next;
        # calculate the length
        # XXX this is the opposite of some logic in Database; should move that
        #     here
        mib = self._mib
        attrs_offset = offset
        attrs_length = 0
        if not extended:
            attrs_length = 25
        else:
            for index in range(1, 17):
                index_shift = 16 - index  # 15, 14, ..., 0
                index_mask = 1 << index_shift
                if attr_mask & index_mask and not opt_attr_mask & index_mask\
                        and not opt_exec_mask & index_mask:
                    attr = mib.attr(index)
                    if attr and reason != 0b0011:
                        attrs_length += attr.size
            # XXX or just calculate the remaining space? no (at least when
            #     reason is non-zero) there could be trailing vendor info

        # baseline messages have opt_attr_mask and attr_exec_mask next
        offset += attrs_length
        if not extended:
            opt_attr_mask, offset = Number(2).decode(contents, offset)
            opt_exec_mask, offset = Number(2).decode(contents, offset)

        # now decode the attribute values
        # XXX invalid attr should be an error, because we don't know its
        #     size and therefore won't decode it
        offset = attrs_offset
        fields = {'reason': reason, 'attr_mask': attr_mask,
                  'opt_attr_mask': opt_attr_mask,
                  'opt_exec_mask': opt_exec_mask}
        for index in range(1, 17):
            index_shift = 16 - index  # 15, 14, ..., 0
            index_mask = 1 << index_shift
            if attr_mask & index_mask and not opt_attr_mask & index_mask and\
                    not opt_exec_mask & index_mask:
                attr = mib.attr(index)
                # XXX this also checked reason != 0b0011 but that prevented
                #     decoding of attributes that are present in the message
                if attr:
                    value, offset = attr.decode(contents, offset)
                    fields[attr.name] = value

        # return decoded fields
        return fields


get_action = Action(9, 'get', 'Get action', Get, GetResponse)
"""Get `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
