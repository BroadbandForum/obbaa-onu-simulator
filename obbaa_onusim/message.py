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

"""OMCI messages are modeled by subclasses of the `Message` base class.

`!Message` instances can be created in two ways:

    * Directly via `Message.__init__`: this is how clients create requests and
      servers create responses and notifications
    * By calling `Message.decode` to decode a received message: this is how
      servers decode requests and clients decode responses and notifications

Examples::

    values = {'battery_backup': True}
    message = Set(cterm_name='foo', onu_id=42, tci=42, extended=False,
                  me_class=256, me_inst=0, values=values)

    # common fields can be put in a dictionary and used like this
    common = {'cterm_name': 'foo', 'onu_id': 42, 'tci': 42, 'extended': False}
    message = Set(me_class=256, me_inst=0, values=values, **common)

    buffer, address = sock.recvfrom(bufsize)
    message = Message.decode(buffer)

    # the __str__() method returns a user-friendly string representation
    print(message)
"""

import functools
import logging
import os, signal

from typing import Any, Optional, Tuple, Union

from .types import Bytes, Number, String, FieldDict, FieldValue

logger = logging.getLogger(__name__.replace('obbaa_', ''))

# XXX should treat the (cterm_name, onu_id) TR-451 header as a separate layer?

# XXX need to fix baseline/extended support; 'extended' means 'supports
#     extended', not 'use extended'; need to use ONU2-G 'omcc_version'

# XXX should allow me_class to be a MIB name; this would be more consistent
#     with use of display (rather than raw) values

# XXX should we encourage explicit subclass constructors, so we can see that
#     instance variables are definitely defined?

# XXX should assist response creation by allowing the incoming message to be
#     passed as a template

# XXX should split out common and MIB-specific attributes; it needs to be
#     easier for generic code to consume responses, e.g. to load a client-side
#     database


class Message:
    """`!Message` base class.

    The methods are documented in a logical order corresponding to a
    message's life-cycle:

    * `__init__` constructs the message from its field values
    * `encode` converts the message to an OMCI buffer
    * (the buffer is now presumably sent over the network)
    * `decode` converts an OMCI buffer back to a message
    * `process` processes the message, maybe constructing a response message
    """
    # XXX should define more such constants
    _dev_id_baseline = 0x0a
    _dev_id_extended = 0x0b
    _cpcs_sdu_fixed = 0x0028

    # default fields
    # XXX all the non-key common fields should be defaulted here
    # XXX the user should never modify the CPCS and CPI fields
    _default_fields = {'cpcs_uu': 0, 'cpcs_sdu': _cpcs_sdu_fixed, 'cpi': 0,
                       'tci': 0, 'extended': False}

    # map class to key (message type) and vice versa
    _fields_for_class = {}
    _class_for_type = {}

    @classmethod
    def _key(cls, fields: dict) -> Tuple[Any]:
        # XXX key doesn't need to include 'type_ar'?
        names = ('type_ar', 'type_ak', 'type_mt')
        assert all({k in fields for k in names})
        return tuple(fields[k] for k in names)

    @classmethod
    def register(cls, **fields) -> None:
        cls._fields_for_class[cls] = fields
        cls._class_for_type[cls._key(fields)] = cls

    def __init__(self, _no_validate: bool = False, **fields):
        """`!Message` base class constructor.

        Subclasses will not usually need to provide their own constructors
        because they can supply their own fields via the base class
        constructor.

        Args:
            _no_validate: This is for internal use only.

            **fields: Keyword arguments. There are several categories of
                field:

                1. The TR-451 header fields (``cterm_name``, ``onu_id=42``)
                   must always be supplied

                2. The OMCI message type fields (``type_ar``, ``type_ak``,
                   ``type_mt``) are handled automatically and so must not be
                   supplied

                3. These OMCI header fields have defaults but can be
                   overridden:

                   * ``tci`` (Transaction Correlation Identifier); 0-65535;
                     default 0
                   * ``extended`` (whether to use extended messages);
                     default False

                4. These OMCI header fields do not have defaults and therefore
                   must be supplied:

                   * ``me_class`` (Managed Entity Class); 0-65535
                   * ``me_inst`` (Managed Entity Instance); 0-65535

                5. Any additional fields are message type specific

        Note:
            `!Message` base class instances can't be instantiated. Only
            instances of subclasses, e.g. `Set` and `Get`, can be
            instantiated.
        """
        cls = self.__class__
        assert cls in self._fields_for_class, "class %r hasn't been " \
                                              "registered and therefore " \
                                              "can't " \
                                              "be instantiated" % cls.__name__
        assert all(f in fields for f in {'me_class', 'me_inst'})
        self._fields = {}
        self._fields.update(cls._default_fields)
        self._fields.update(cls._fields_for_class[cls])
        self._fields.update(fields)

        from .mib import mibs
        self._mib = mibs.get(self.me_class, None)
        if self._mib is None:
            logger.error('UNKNOWN INSTANCE')

        if not _no_validate:
            fields = self.validate()
            self._fields.update(fields)

    def validate(self) -> FieldDict:
        """Validate a message, returning a dictionary of modified fields.

        This is primarily intended for when an application calls the
        constructor directly and therefore have supplied some invalid fields.

        If this method detects an unrecoverable error, it should raise an
        exception.

        The base class implementation just returns an empty dictionary.
        Subclasses should override this method.

        Returns:
            Dictionary mapping field names to field values. The instance
            will be updated with these fields.
        """
        return {}

    def encode(self, *, tr451: bool = True) -> bytearray:
        """Encode this message into a buffer.

        Args:
            tr451: Whether to add a TR-451 header to the buffer.

        Returns:
            The encoded buffer.
        """
        buffer = bytearray()

        # encode TR-451 message header, if present
        # - char cterm_name[30] // C zero-terminated if shorter than 30
        # - uint16_t onu_id;    // in network order
        if tr451:
            buffer += String(30).encode(self.cterm_name)
            buffer += Number(2).encode(self.onu_id)

        # encode OMCI header: tci
        buffer += Number(2).encode(self.tci)

        # encode OMCI header: type
        type_ar = self.type_ar and 0x40 or 0x00
        type_ak = self.type_ak and 0x20 or 0x00
        type_mt = self.type_mt & 0x1f
        type_ = type_ar | type_ak | type_mt
        buffer += Number(1).encode(type_)

        # encode OMCI header: dev_id
        extended = self.extended
        dev_id = extended and self._dev_id_extended or self._dev_id_baseline
        buffer += Number(1).encode(dev_id)

        # encode OMCI header: me_class, me_inst
        buffer += Number(2).encode(self.me_class)
        buffer += Number(2).encode(self.me_inst)

        # allow subclass to encode contents from subclass-specific fields
        contents = self.encode_contents()

        # encode contents
        length = len(contents)
        if not extended:
            assert length <= 32
            buffer += Bytes(32).encode(contents)
            buffer += Number(1).encode(self.cpcs_uu)
            buffer += Number(1).encode(self.cpi)
            buffer += Number(2).encode(self.cpcs_sdu)
        else:
            buffer += Number(2).encode(length)
            buffer += Bytes(length).encode(contents)

        return buffer

    # encode contents from subclass-specific fields
    # XXX should also return a dict with any additional fields to be added
    #     to the object, e.g. individual attributes?
    def encode_contents(self) -> bytearray:
        """Encode this message's contents, i.e. its type-specific payload.

        The base class implementation just returns an empty buffer.
        Subclasses should override this method.

        Returns:
            Encoded buffer.
        """
        return bytearray()

    @classmethod
    def decode(cls, buffer: Union[bytes, bytearray], *, tr451: bool = True) \
            -> 'Message':
        """Decode a buffer, returning a `Message` instance of the
        appropriate type.

        Args:
            buffer: Buffer, e.g. just received from a socket.
            tr451: Whether the buffer has a TR-451 header.

        Returns:
            `Message` instance of the appropriate type.
        """
        offset = 0

        # decode TR-451 message header, if present
        # - char cterm_name[30] // C zero-terminated if shorter than 30
        # - uint16_t onu_id;    // in network order
        cterm_name = None
        onu_id = None
        if tr451:
            cterm_name, offset = String(30).decode(buffer, offset)
            onu_id, offset = Number(2).decode(buffer, offset)

        # decode OMCI header: tci, type, dev_id
        tci, offset = Number(2).decode(buffer, offset)
        type_, offset = Number(1).decode(buffer, offset)
        dev_id, offset = Number(1).decode(buffer, offset)

        # split type into its components
        type_msb = type_ & 0x80 != 0  # MSB is reserved and must be 0
        if type_msb:
            logger.error('OMCI message type (%#04x) has MSB set' % type_)
        type_ar = type_ & 0x40 != 0   # Acknowledge Request
        type_ak = type_ & 0x20 != 0   # AcKnowledgment
        type_mt = type_ & 0x1f        # Message Type

        # dev_id must be 0x0a (baseline) or 0x0b (extended)
        if dev_id not in {cls._dev_id_baseline, cls._dev_id_extended}:
            logger.error('OMCI device identifier (%#04x) is invalid; %#04x '
                         '(baseline) assumed' % (dev_id, cls._dev_id_baseline))
            dev_id = cls._dev_id_baseline

        # decode OMCI header: me_class, me_inst
        me_class, offset = Number(2).decode(buffer, offset)
        me_inst, offset = Number(2).decode(buffer, offset)

        # decode contents
        extended = dev_id == cls._dev_id_extended
        if not extended:
            contents, offset = Bytes(32).decode(buffer, offset)
            cpcs_uu, offset = Number(1).decode(buffer, offset)
            cpi, offset = Number(1).decode(buffer, offset)
            cpcs_sdu, offset = Number(2).decode(buffer, offset)
            if cpcs_sdu != cls._cpcs_sdu_fixed:
                logger.error('OMCI CPCS-SDU (%#06x) is invalid; should be '
                             '%#06x (%d)' % (cpcs_sdu, cls._cpcs_sdu_fixed,
                                             cls._cpcs_sdu_fixed))
        else:
            length, offset = Number(2).decode(buffer, offset)
            contents, offset = Bytes(length).decode(buffer, offset)
            cpcs_uu, cpi, cpcs_sdu = None, None, None

        # all bytes should have been consumed
        # XXX note that decode() increments offset regardless, so this will
        #     fail if the buffer was short
        if offset != len(buffer):
            logger.error("OMCI message length (%r) doesn't match "
                         "expected length (%r)" % (len(buffer), offset))

        # create message of the appropriate type
        message = cls._create(cterm_name=cterm_name, onu_id=onu_id, tci=tci,
                              type_ar=type_ar, type_ak=type_ak,
                              type_mt=type_mt, extended=extended,
                              me_class=me_class, me_inst=me_inst,
                              cpcs_uu=cpcs_uu, cpi=cpi, cpcs_sdu=cpcs_sdu)

        # allow subclass to decode contents into subclass-specific fields
        fields = message.decode_contents(contents)
        message._fields.update(fields)

        # allow subclass to perform further initialization
        fields = message.validate()
        message._fields.update(fields)
        # return message
        return message

    @classmethod
    def _create(cls, **fields) -> 'Message':
        key = cls._key(fields)
        if(key not in cls._class_for_type):
            logger.error('UNKNOWN ENTITY: %s' % (key,))
            os.kill(os.getpid(),signal.SIGTERM)
        
        cls_ = cls._class_for_type[key]
        message = cls_(_no_validate=True, **fields)
        return message

    # decode contents into subclass-specific fields
    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Args:
            contents: The contents part of the buffer.

        Returns:
            Dictionary mapping field names to field values. The instance
            will be updated with these fields.
        """
        return {}

    # this returns the response message (if requested)
    # XXX can't import Endpoint; would create circular dependency
    def process(self, endpoint: object) -> Optional['Message']:
        """Pass this message to the endpoint for processing, and return the
        response (if any).

        Args:
            endpoint: Endpoint to which to pass the message for processing.

        Returns:
            The response, or ``None`` if there is no response.
        """
        return None

    def get(self, name: str, default: FieldValue = None) -> FieldValue:
        """Get the value of the named field.

        Args:
            name: Field name.
            default: Value to return if the field doesn't exist.

        Returns:
            Field value.

        Note:
            It will usually be more convenient to rely on the fact that
            ``__getattr__`` has been defined to return field values directly.
            Assuming that field ``foo`` exists, these are the same::

                self.get('foo')
                self.foo

            As with dictionaries, if you're not sure whether the field
            exists, it's safer to use `!get()`.

        """
        return self._fields.get(name, default)

    # XXX this might be a bad idea?
    def __getattr__(self, name: str) -> FieldValue:
        if name in self._fields:
            return self.get(name)
        else:
            raise AttributeError('%r object has no attribute %r' % (
                self.__class__.__name__, name))

    def set(self, name: str, value: FieldValue) -> None:
        """Set the value of the named field.

        Args:
            name: Field name.
            value: Field value.

        Note:
            The field name isn't checked, so it's possible to inadvertently
            create new fields using this method.
        """
        self._fields[name] = value

    # XXX this is definitely a bad idea!
    if False:
        def __setattr__(self, name, value):
            if name == '_fields' or name in dir(self):
                super().__setattr__(name, value)
            else:
                self.set(name, value)

    # XXX should break out the loop and use str() for individual elements
    # XXX could allow sub-classes to add to excluded
    def __str__(self) -> str:
        """Return a user-friendly representation of a message.

        Example::

            values = {'battery_backup': True}
            message = Set(cterm_name='foo', onu_id=42, tci=84, me_class=256,
                          me_inst=0, values=values)
            print(message)

            ->

            Set(attr_mask=0x400, cterm_name='foo', extended=False,
                me_class=256, me_inst=0, onu_id=42, tci=84,
                values={'battery_backup': 1})

        Note:

            Oops. This example shows that value conversion between user and
            raw units isn't yet complete.
        """
        excluded = {'cpcs_sdu', 'cpcs_uu', 'cpi', 'type_ak', 'type_ar',
                    'type_mt'}
        fields = ', '.join(['%%s=%%%s' % (
            '#x' if k.endswith('_mask') and v is not None else 'r') % (k, v)
                            for k, v in
                            sorted(self._fields.items(), key=lambda i: i[0]) if
                            not k.startswith('_') and k not in excluded])
        return '%s(%s)' % (self.__class__.__name__, fields)

    __repr__ = __str__


# based on https://realpython.com/primer-on-python-decorators/#decorators
# -with-arguments
# XXX this is no longer used; action constructors now register their messages
if False:
    def register(**fields):
        def decorator(cls):
            @functools.wraps(cls)
            def wrapper(*args, **kwargs):
                cls.register(**fields)
                return cls(*args, **kwargs)
            return wrapper
        return decorator
