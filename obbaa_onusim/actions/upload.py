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


class MibUpload(Message):
    """MIB upload command message.
    """

    def process(self, server: object) -> 'MibUploadResponse':
        results = server.database.upload(self.onu_id, self.me_class,
                                         self.me_inst, extended=self.extended)

        response = MibUploadResponse(cterm_name=self.cterm_name,
                                     onu_id=self.onu_id,
                                     extended=self.extended, tci=self.tci,
                                     me_class=self.me_class,
                                     me_inst=self.me_inst,
                                     num_upload_nexts=results.num_upload_nexts)
        return response


# XXX note that there's no 'reason' field
class MibUploadResponse(Message):
    """MIB upload response message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(self.num_upload_nexts)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``num_upload_nexts``: number of `MibUploadNext` commands
              required; 0-65535
        """
        num_upload_nexts, _ = Number(2).decode(contents, 0)
        return {'num_upload_nexts': num_upload_nexts}


class MibUploadNext(Message):
    """MIB upload next command message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(self.seq_num)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``seq_num``: command sequence number; 0-65535
        """
        seq_num, _ = Number(2).decode(contents, 0)
        return {'seq_num': seq_num}

    def process(self, server: object) -> 'MibUploadNextResponse':
        results = server.database.upload_next(self.onu_id, self.me_class,
                                              self.me_inst, self.seq_num,
                                              extended=self.extended)

        response = MibUploadNextResponse(cterm_name=self.cterm_name,
                                         onu_id=self.onu_id,
                                         extended=self.extended, tci=self.tci,
                                         me_class=self.me_class,
                                         me_inst=self.me_inst,
                                         _body=results.body)
        return response


# XXX note that there's no 'reason' field
class MibUploadNextResponse(Message):
    """MIB upload next response message.
    """

    def encode_contents(self) -> bytearray:
        contents = bytearray()
        length, chunks = self.get('_body')
        logger.debug('length=%r' % length)
        if self.extended:
            contents += Number(2).encode(length)
        for size, attr_values, me_class, me_inst in chunks:
            attr_mask = functools.reduce(operator.or_,
                                         [a.mask for a, _ in attr_values])
            logger.debug('  size=%r, me_class=%r, me_inst=%r, '
                         'attr_mask=%#06x' % (size, me_class, me_inst,
                                              attr_mask))
            if self.extended:
                contents += Number(2).encode(size)
            contents += Number(2).encode(me_class)
            contents += Number(2).encode(me_inst)
            contents += Number(2).encode(attr_mask)
            for attr, value in attr_values:
                logger.debug('    attr=%r, value=%r' % (attr, value))
                contents += attr.encode(value)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``me_class.me_inst.attr_name``: the item name is the
               dot-separated ME class (MIB number), ME instance,
               and attribute name.
        """
        offset = 0
        fields = {}

        # XXX length isn't currently used
        # noinspection PyUnusedLocal
        length = 32  # XXX ????
        if self.extended:
            length, offset = Number(2).decode(contents, offset)

        # XXX review this termination criterion
        while offset < len(contents):
            if self.extended:
                size, offset = Number(2).decode(contents, offset)

            me_class, offset = Number(2).decode(contents, offset)
            # XXX this is baseline-only; should be an error for extended
            if me_class == 0:
                break

            # if can't find MIB, can't proceed for baseline
            # XXX but should proceed to the next chunk for extended
            from ..mib import mibs
            mib = mibs.get(me_class, None)
            if mib is None:
                raise Exception('MIB %d not found' % me_class)

            me_inst, offset = Number(2).decode(contents, offset)

            attr_mask, offset = Number(2).decode(contents, offset)
            for index, index_mask in util.indices(attr_mask):

                # if can't find attr, can't proceed for baseline
                # XXX but should proceed to the next chunk for extended
                attr = mib.attr(index)
                if attr is None:
                    raise Exception(
                            'MIB %s #%d %d not found' % (mib, me_inst, index))

                value, offset = attr.decode(contents, offset)
                fields['%d.%d.%s' % (me_class, me_inst, attr.name)] = value
                logger.debug('MIB %s #%d %s = %r' % (mib, me_inst, attr,
                                                     value))

        # return decoded fields
        return fields


mib_upload_action = Action(13, 'mib-upload', 'MIB upload action', MibUpload,
                           MibUploadResponse)
"""MIB upload `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""

mib_upload_next_action = Action(14, 'mib-upload-next', 'MIB upload next '
                                                       'action', MibUploadNext,
                                MibUploadNextResponse)
"""MIB upload next `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
