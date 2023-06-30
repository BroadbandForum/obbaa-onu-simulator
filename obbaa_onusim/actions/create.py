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
from os import access
from obbaa_onusim.mib import RWC,RC
import operator
import re

from .. import util

from ..action import Action
from ..message import Message
from ..types import Number, String, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class Create(Message):
    
    def validate(self) -> FieldDict:
   
        mib = self._mib
        values = self.values
        values_ = {}
      
        if not values:
            logger.warning('no attributes specified; set-by-create: '
                           '%s' % mib.attr_names(RWC))
        for name_or_number, value in sorted(values.items(),
                                            key=lambda i: i[0]):
            # XXX mib.attr() could contain this logic
            if re.match(r'^\d+$', name_or_number):
                name_or_number = int(name_or_number)
            attr = mib.attr(name_or_number)
            if not attr:
                logger.warning(
                        'MIB %s %r not found; supported attributes: %s' % (
                            mib, name_or_number, mib.attr_names(RWC)))
            elif attr.access != RWC and attr.access != RC:
                logger.warning('MIB %s %s is not set-by-create' % (mib,
                                                                        attr))
            else:                
                values_[attr.name] = value   

        return {'values': values_}

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

        # decode the attribute values
        mib = self._mib
        values = {}

        attr_names = mib.attr_names().split(", ")
        for attr_name in attr_names:
          attr_name = attr_name[attr_name.find("(")+1:attr_name.find(")")]
          attr = mib.attr(attr_name)
          value, offset = attr.decode(contents,offset)
          values[attr.name] = value
    
        return {'values': values}
        
        
    def process(self, server: object) -> 'CreateResponse':

        results=server.database.create(self.onu_id, self.me_class,
                                      self.me_inst,
                                      self.values, extended=self.extended)

        response = CreateResponse(cterm_name=self.cterm_name,
                                     onu_id=self.onu_id,
                                     extended=self.extended, tci=self.tci,
                                     reason=results.reason,
                                     me_class=self.me_class,
                                     me_inst=self.me_inst,
                                     attr_exec_mask=results.attr_exec_mask)
        return response


# XXX note that there's no 'reason' field
class CreateResponse(Message):
    """Create response message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(0)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.
        """
        # * If ``reason`` is ``0b0011`` (9):
        #      * ``opt_attr_mask``: optional-attribute mask; 0-65535

        offset = 0
        reason, offset = Number(1).decode(contents, offset)

        attr_exec_mask = None
        if reason == 0b0011:
            attr_exec_mask, offset = Number(2).decode(contents, offset)
        return {'reason': reason,'attr_exec_mask': attr_exec_mask}



create_action = Action(4, 'create', 'Create action', Create, CreateResponse)
"""Create `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
