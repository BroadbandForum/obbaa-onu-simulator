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

"""The Set action's messages are defined in G.988 A.2.5-6 (extended) and
A.3.5-6 (baseline).

The relevant classes and instances are:

* `Set`: Set command message class
* `SetResponse`: Set response message class
* `set_action`: Set action instance
"""

import logging
import re

from .. import util

from ..action import Action
from ..message import Message
from ..mib import RW, RWC
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class Set(Message):
    """Set command message."""

    # XXX should permit or convert to raw values? be careful! this is called on
    #     both the client and server side! should it be?
    def validate(self) -> FieldDict:
        """Validate the ``values`` field (a dictionary), returning new values
        for the  ``attr_mask`` and ``values`` fields.

        For each item in the ``values`` dictionary:

            * Check it's a valid attribute name or number
            * Check it's a writable attribute

        If any of the checks fail, output a warning and ignore the attribute.

        Returns:
            Dictionary with the following items.
                * ``attr_mask``: attribute mask containing bits for valid
                  attributes from the supplied values
                * ``values``: dictionary containing valid attributes from the
                  supplied values, and with raw attribute values
        """
        mib = self._mib
        values = self.values
        attr_mask = 0x0000
        values_ = {}
        if not values:
            logger.warning('no attributes specified; writable attributes: '
                           '%s' % mib.attr_names(RW))
        for name_or_number, value in sorted(values.items(),
                                            key=lambda i: i[0]):
            # XXX mib.attr() could contain this logic
            if re.match(r'^\d+$', name_or_number):
                name_or_number = int(name_or_number)
            attr = mib.attr(name_or_number)
            if not attr:
                logger.warning(
                        'MIB %s %r not found; supported attributes: %s' % (
                            mib, name_or_number, mib.attr_names(RW)))
            elif attr.access != RW and attr.access !=RWC:
                logger.warning('MIB %s %s is not writable (ignored)' % (mib,
                                                                        attr))
            else:
                attr_mask |= attr.mask
                # XXX for now, convert to int
                values_[attr.name] = (value)
        return {'attr_mask': attr_mask, 'values': values_}

    def encode_contents(self) -> bytearray:
        extended = self.extended
        contents = bytearray()

        # attr_mask comes first
        attr_mask = self.attr_mask
        contents += Number(2).encode(attr_mask)

        # encode the attribute values
        mib = self._mib
        values = self.values
        size = 0
        for index, index_mask in util.indices(attr_mask):
            attr = mib.attr(index)
            if not attr:
                logger.error('MIB %s %d not found; supported attributes: %s'
                             % (mib, index, mib.attr_names()))
            elif not extended and size + attr.size > 25:
                # XXX should detect this in validate()
                logger.error('MIB %s %s ignored (too long for baseline '
                             'message)' % (mib, attr))
            elif attr.name in values:
                contents += attr.encode(values[attr.name])
                size += attr.size

        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``attr_mask``: attribute mask; 0-65535
            * ``values``: MIB-specific attribute names and values as specified
              by the attribute mask

        Note:
            `!Set` and `GetResponse` are inconsistent: here the dictionary
            contains a ``values`` item, but `GetResponse` places the
            attributes directly in the object. This inconsistency will be
            resolved.
        """
        offset = 0

        # attr_mask comes first
        attr_mask, offset = Number(2).decode(contents, offset)

        # decode the attribute values
        mib = self._mib
        values = {}
        for index, index_mask in util.indices(attr_mask):
            attr = mib.attr(index) if mib else None
            if not attr:
                # XXX this isn't really of interest
                logger.debug(
                        'MIB %s %d not found; supported attributes: %s' % (
                            mib, index, mib.attr_names()))
            else:
                value, offset = attr.decode(contents, offset)
                values[attr.name] = value
        
        return {'attr_mask': attr_mask, 'values': values}

    def process(self, server: object) -> 'SetResponse':
        results = server.database.set(self.onu_id, self.me_class,
                                      self.me_inst, self.attr_mask,
                                      self.values, extended=self.extended)

        response = SetResponse(cterm_name=self.cterm_name, onu_id=self.onu_id,
                               extended=self.extended, tci=self.tci,
                               me_class=self.me_class, me_inst=self.me_inst,
                               reason=results.reason,
                               opt_attr_mask=results.opt_attr_mask,
                               attr_exec_mask=results.attr_exec_mask)
        return response


class SetResponse(Message):
    """Set response message.
    """

    def encode_contents(self) -> bytearray:
        contents = bytearray()
        contents += Number(1).encode(self.reason)
        if self.reason == 0b1001:
            contents += Number(2).encode(self.opt_attr_mask)
            contents += Number(2).encode(self.attr_exec_mask)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``reason``: result, reason; 0-255
            * ``attr_mask``: attribute mask; 0-65535
            * If ``reason`` is ``0b1001`` (9):
              * ``opt_attr_mask``: optional-attribute mask; 0-65535
              * ``opt_exec_mask``: attribute execution mask; 0-65535
        """
        offset = 0
        reason, offset = Number(1).decode(contents, offset)
        opt_attr_mask, attr_exec_mask = None, None
        if reason == 0b1001:
            opt_attr_mask, offset = Number(2).decode(contents, offset)
            attr_exec_mask, offset = Number(2).decode(contents, offset)
        return {'reason': reason, 'opt_attr_mask': opt_attr_mask,
                'attr_exec_mask': attr_exec_mask}


set_action = Action(8, 'set', 'Set action', Set, SetResponse)
"""Set `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
