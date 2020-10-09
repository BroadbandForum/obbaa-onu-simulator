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

# this is needed to instantiate the MIBs
import obbaa_onusim.database

from obbaa_onusim.actions.set import Set
from obbaa_onusim.message import Message

values = {'battery_backup': True}
message = Set(cterm_name='foo', onu_id=42, tci=84, me_class=256, me_inst=0,
              values=values)
print(message)

tr451 = False
extended = True

message = Set(cterm_name='foo', onu_id=42, tci=84, extended=extended,
              attr_mask=0xffff, me_class=256, me_inst=0, values=values,
              invalid='should generate an error?')

print(message)
print('attr_mask was modified to match values: %#06x' % message.attr_mask)
print('invalid field: %r' % message.get('invalid'))

buffer = message.encode(tr451=tr451)
print('buffer length %d' % len(buffer))

# "send" and "recv"

message2 = Message.decode(buffer, tr451=tr451)

print(message2)
print('invalid field: %r' % message2.get('invalid'))
