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

"""An action is an operation, typically involving a command/response
message round-trip."""

import logging

from typing import Type

from .message import Message
from .types import AutoGetter, NumberName, Datum, Bytes, Number, AttrData

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class Action(NumberName, AutoGetter):
    """`!Action` class.
    """

    def __init__(self, number: int, name: str, description: str = None,
                 request: Type[Message] = None, response: Type[Message] =
                 None):
        """`!Action` constructor.

        Args:
            number: Action number. This is the OMCI message type (
                ``type_mt``) for the action's request and response messages.

            name: Action name. This is only used for documentation purposes.

            description: Action description. This is only used for
                documentation purposes.

            request: Request message class.

            response: Response message class. If ``None`` no response is
                expected.
        """
        super().__init__(number, name, description)
        self._request = request
        self._response = response

        # XXX request will never be None? shouldn't be a keyword argument?
        if request:
            request.register(type_mt=number, type_ar=True, type_ak=False)

        if response:
            response.register(type_mt=number, type_ar=False, type_ak=True)


class Arg(NumberName, AutoGetter):
    def __init__(self, number: int, name: str, description: str = None,
                 data: AttrData = None, cond: str = None):
        super().__init__(number, name, description)

        assert isinstance(data, Datum) or (isinstance(data, tuple) and all(
                isinstance(i, Datum) for i in data))
        self._data = isinstance(data, Datum) and (data,) or data
        self._cond = cond

# XXX this isn't used yet, and may never be (except by the CLI? and when
#     dumping buffers?)
message = (
    Arg(0, 'tci', 'Transaction correlation identifier', Number(2)),
    Arg(1, 'type', 'Message type', Number(1)),
    Arg(2, 'dev_id', 'Device identifier', Number(1, (0x0a, 0x0b)),),
    Arg(3, 'me_class', 'Managed entity identifier: Entity class', Number(2)),
    Arg(4, 'me_inst', 'Managed entity identifier: Entity instance', Number(
            2)),
    Arg(5, 'length', 'Message contents length', Number(2), 'dev_id==0x0b'),
    Arg(6, 'contents', 'Message contents', Bytes('length||32')),
    Arg(7, 'cpcs_uu', 'Common Part Convergence Sublayer: User-to-User',
        Number(1, fixed=0), 'dev_id==0x0a'),
    Arg(8, 'cpi', 'Common Part Convergence Sublayer: Common Part Indicator',
        Number(1, fixed=0), 'dev_id==0x0a'),
    Arg(9, 'cpcs_sdu', 'Common Part Convergence Sublayer: Service Data Unit',
        Number(2, fixed=0x0028), 'dev_id==0x0a')
)
