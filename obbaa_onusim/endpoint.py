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

"""An endpoint is an OMCI client or server.

Endpoints are modeled by instances of the `Endpoint` class. Examples::

  client = Endpoint((address, port), is_server=False, cterm_name='foo',
                    onu_id_range=range(100))
  message = ...
  client.send(message)
  response, address = client.recv()
  client.process(response)

::

  server = Endpoint((address, port), is_server=True, cterm_name='foo',
                    onu_id_range=range(100))
  message, address = server.recv()
  response = server.process(message)
  if response:
      server.send(response, address)
"""

import logging
import socket

from typing import IO, Tuple, Union

from .database import Database
from .message import Message

logger = logging.getLogger(__name__.replace('obbaa_', ''))

Address = Tuple[str, int]


# XXX should have separate Client and Server Endpoint classes
class Endpoint:
    """Models an OMCI client or server instance.

    Note:
       There should probably be an ``Endpoint`` base class with ``Client``
       and ``Server`` subclasses.
    """

    def __init__(self, server_address: Address, *, is_server: bool = True,
                 cterm_name: str = None, onu_id_range: range = None,
                 tr451: bool = True, timeout: int = 10,
                 dumpfd: IO[str] = None):
        """Create an OMCI endpoint instance.

        Args:
            server_address: Server address (and port). Clients send to this
                address; servers listen on it.

            is_server: Whether or not this endpoint is a server.

            cterm_name: Channel termination name. Clients include this name
                in all messages. Servers will process only messages that
                contain it.

            onu_id_range: ONU id range, e.g. ``range(10)`` means ONU ids 0, 1,
                ...9. Ignored by clients. Servers will process only messages
                that contain one of these ONU ids.

            tr451: Whether to process TR-451 (``cterm_name``, ``onu_id``)
                headers.

            timeout: Clients will time out after this number of seconds.
                Ignored by servers.

            dumpfd: File to which to send hex dumps of all sent and received
                messages (ignoring the TR-451 header).
        """
        assert isinstance(server_address, tuple) and len(server_address) == 2
        assert not is_server or cterm_name is not None
        assert not is_server or onu_id_range is not None
        self._server_address = server_address
        self._is_server = is_server
        self._cterm_name = cterm_name
        self._onu_id_range = onu_id_range
        self._tr451 = tr451
        self._dumpfd = dumpfd
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if self._is_server:
            self._sock.bind(self._server_address)
        else:
            self._sock.settimeout(timeout)
        self._database = Database(self._onu_id_range)

    def recv(self, *, bufsize: int = 2048) -> Tuple[Message, Address]:
        """Receive a buffer from the server socket and decode it as a
        message.

        Args:
            bufsize: Buffer size in bytes.

        Returns:
            Decoded message and the address from which it was received.
        """
        buffer, address = self._sock.recvfrom(bufsize)
        logger.debug('received %r/%r bytes from %r' % (len(buffer), bufsize,
                                                       address))
        message = Message.decode(buffer, tr451=self._tr451)
        self._dump_buffer(buffer)
        return message, address

    # XXX is it correct to ignore messages that we don't handle, or should we
    #     return an error, e.g. reason=0b0001 (command processing error)?
    def process(self, message: Message) -> Union[None, Message]:
        """Process a received message.

        Args:
            message: Message to process.

        Returns:
            None (if no response is requested) or the response.

        Note:
            Messages that don't have an expected ``cterm_name`` or
            ``onu_id`` will be ignored and no response will be sent. This is
            probably wrong.
        """
        # XXX this assumes TR-451!
        if message.cterm_name != self._cterm_name:
            logging.error('message is for channel termination %r, not for %r; '
                          'ignored' % (message.cterm_name, self._cterm_name))
            response = None
        elif message.onu_id not in self._onu_id_range:
            logging.error('message is for ONU id %d, not for %d:%d; '
                          'ignored' % (message.onu_id,
                                       self._onu_id_range.start,
                                       self._onu_id_range.stop - 1))
            response = None
        else:
            response = message.process(self)
        return response

    def send(self, message: Message, address: Address = None) -> None:
        """Send a message to the server or the specified address.

        Args:
            message: Message to send.
            address: Address to send the message to. Defaults to the server
                address.
        """
        address = address or self._server_address
        buffer = message.encode(tr451=self._tr451)
        self._sock.sendto(buffer, address)
        logger.debug('sent %r bytes to %r' % (len(buffer), address))
        self._dump_buffer(buffer)

    # XXX should add some buffer length checks
    def _dump_buffer(self, buffer):
        logger.debug(buffer.hex())
        if self._dumpfd:
            offset = self._tr451 and 32 or 0
            packet = buffer[offset:]
            extended = packet[3] == 0x0b
            if not extended:
                self._dumpfd.write('# TCI  MT DI CLS  INST CONTENTS'
                                   '                               '
                                   '                          TRAILER\n')
                self._dumpfd.write('  %s %s %s %s %s %s %s\n' % (
                    packet[0:2].hex(), packet[2:3].hex(), packet[3:4].hex(),
                    packet[4:6].hex(), packet[6:8].hex(), packet[8:40].hex(),
                    packet[40:].hex()))
            else:
                self._dumpfd.write('# TCI  MT DI CLS  INST LEN  CONTENTS\n')
                self._dumpfd.write('  %s %s %s %s %s %s %s\n' % (
                    packet[0:2].hex(), packet[2:3].hex(), packet[3:4].hex(),
                    packet[4:6].hex(), packet[6:8].hex(), packet[8:10].hex(),
                    packet[10:].hex()))

    @property
    def server_address(self) -> Address:
        """Server address."""
        return self._server_address[0], self._server_address[1]

    @property
    def database(self) -> Database:
        """Database object."""
        return self._database

    def __str__(self):
        return '%s(address=%r, is_server=%r, cterm_name=%r, onu_id_range=%s, '\
               'tr451=%r, dumpfd=%r)' % (self.__class__.__name__,
                                         self._server_address, self._is_server,
                                         self._cterm_name, self._onu_id_range,
                                         self._tr451, self._dumpfd)

    __repr__ = __str__
