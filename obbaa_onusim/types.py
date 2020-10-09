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

"""Various common data types.
"""

import logging
import re
import struct

from typing import Any, Dict, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__.replace('obbaa_', ''))

# these are used in type hints

# used for message fields
# XXX could constrain dict and list more tightly here?
FieldValue = Union[bool, bytes, int, str, dict, list]
FieldDict = Dict[str, FieldValue]

# used for attribute values (for this module's Attr class)
# XXX need to reconsider all the names!
# XXX need to distinguish raw and user values
AttrValue = Union[bool, bytearray, int, str]
AttrDict = Dict[str, AttrValue]

AttrValuesEnum = Tuple[str, ...]

AttrData = Union['Datum', Tuple['Datum', ...]]
AttrDataValues = Union[AttrValue, Tuple[AttrValue, ...]]


# within a given type (class), name must be a unique key
class Name:
    """Name (and description) mixin class.
    """

    def __init__(self, name: str, description: str = None, *,
                 names: Optional[Set[str]] = None):
        assert names is None or name in names
        self._name = name
        self._description = description or ''

    def info(self) -> str:
        description = ' %r' % self._description if self._description else ''
        return '%s%s' % (self._name, description)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        description = self._description and ', description=%r' % \
                      self._description or ''
        return '%s(name=%r%s)' % (self.__class__.__name__, self._name,
                                  description)


# within a given type (class), number be a unique key (and name via Name)
class NumberName(Name):
    """Number, name (and description) mixin class.
    """

    def __init__(self, number: int, name: str, description: str = None, *,
                 names: Optional[Set[str]] = None):
        super().__init__(name, description=description, names=names)
        self._number = number

    def info(self) -> str:
        description = ' %r' % self._description if self._description else ''
        return '%d (%s)%s' % (self._number, self._name, description)

    def __str__(self) -> str:
        return '%d(%s)' % (self._number, self._name)

    def __repr__(self) -> str:
        description = self._description and ', description=%r' % \
                      self._description or ''
        return '%s(number=%r, name=%r%s)' % (
            self.__class__.__name__, self._number, self._name, description)


class AutoGetter:
    """Auto-getter mixin class.

    Allows ``instance._attr`` to be accessed (only for read access) as
    ``instance.attr``.
    """

    def __getattr__(self, name: str) -> Any:
        _name = name.startswith('_') and name or '_' + name
        if _name in dir(self):
            return super().__getattribute__(_name)
        else:
            raise AttributeError('%r object has no attribute %r' % (
                self.__class__.__name__, name))


class Datum(AutoGetter):
    """Single data item class.

    Defines a single data item of a given type, with support for default and
    fixed values, for encoding and decoding values, and for converting
    between user and raw values.
    """

    def __init__(self, size: int, default: AttrValue = None,
                 fixed: AttrValue = None):
        """Data item constructor.

        Args:
            size: size of data item in bytes.

            default: default value of data item (used if no value is
                specified).

            fixed: fixed value of data item (takes precedence over the
                default; any attempt to define a data item instance with a
                different value is an error).

        Note:
            A default MUST currently be provided (it determines the type); this
            is wrong: the type should come from the subclass.
        """
        # XXX a default must currently be provided (it determines the type);
        #     this is wrong: the type should come from the subclass
        assert default is not None
        self._size = size
        self._default = default
        self._fixed = fixed

    def decode(self, buffer: bytearray, offset: int) -> Tuple[AttrValue, int]:
        """Decode data item value.

        Args:
            buffer: buffer from which to decode the value

            offset: byte offset within buffer at which to start decoding

        Returns:
            Decoded value and updated offset.

            * If there isn't sufficient data in the buffer, the default
              value is returned

            * The returned value is a user value (it's converted from the raw
              value)

            * The offset is ready to be passed to the next ``decode``
              invocation
        """
        size = self._size
        format_ = self._struct_format
        if offset + size > len(buffer):
            # XXX should this be a warning or error?
            value = self._default
        else:
            raw_value = struct.unpack_from(format_, buffer, offset)[0]
            value = self.value(raw_value)
        return value, offset + size

    def encode(self, value: AttrValue = None) -> bytearray:
        """Encode data item value.

        Args:
            value: the value to be encoded

        Returns:
            Encoded buffer.

            * If value is ``None``, the default value is encoded

            * The value is converted to a raw value before encoding
        """
        value = value if value is not None else self._default
        format_ = self._struct_format
        buffer = bytearray(self._size)
        raw_value = self.raw_value(value)
        struct.pack_into(format_, buffer, 0, raw_value)
        return buffer

    def raw_value(self, value: AttrValue) -> AttrValue:
        """Convert data item user value to raw value.
        """
        raise Exception('Unimplemented raw_value() method')

    def value(self, raw_value: AttrValue) -> AttrValue:
        """Convert data item raw value to user value.
        """
        raise Exception('Unimplemented value() method')

    @property
    def _struct_format(self) -> str:
        raise Exception('Unimplemented struct_format property')

    def __str__(self) -> str:
        extra = '==%r' % self._fixed if self._fixed is not None else \
            '=%r' % self._default if self._default is not None else ''
        return '%s(%d)%s' % (self.__class__.__name__, self._size, extra)

    def __repr__(self) -> str:
        default = self._default is not None and ', default=%r' % \
                  self._default or ''
        fixed = self._fixed is not None and ', fixed=%r' % self._fixed or ''
        return '%s(size=%r%s%s)' % (
            self.__class__.__name__, self._size, default, fixed)


class Bool(Datum):
    """Boolean data item class.
    """
    def __init__(self, size: int, default: bool = None, fixed: bool = None):
        """The default defaults to false.
        """
        default = default or False
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value: bool) -> int:
        return int(value)

    def value(self, raw_value: int) -> bool:
        return bool(raw_value)

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]


class Enum(Datum):
    """Enumeration data item class.
    """
    def __init__(self, size: int, values: AttrValuesEnum = None,
                 default: str = None, fixed: str = None):
        default = default or (values[0] if values else None)
        super().__init__(size, default=default, fixed=fixed)
        self._values = values and tuple(values) or ()

    # XXX this throws ValueError if the value isn't found
    def raw_value(self, value: str) -> int:
        return self._values.index(value)

    # XXX this throws IndexError if the raw_value is invalid
    def value(self, raw_value: int) -> str:
        return self._values[raw_value]

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]

    def __str__(self) -> str:
        return '%s %s' % (super().__str__(), self._values)


# XXX Bits is currently the same as Enum; it needs different logic
class Bits(Enum):
    """Bits data item class.
    """
    pass


class Number(Datum):
    """Number data item class.
    """
    def __init__(self, size: int, default: int = None, fixed: int = None,
                 units: str = None):
        default = default or 0
        super().__init__(size, default=default, fixed=fixed)
        # XXX units are currently ignored
        self._units = units

    def raw_value(self, value: int) -> int:
        return value

    def value(self, raw_value: int) -> int:
        return raw_value

    @property
    def _struct_format(self) -> str:
        assert self._size in {1, 2, 4, 8}
        return '!%s' % {1: 'B', 2: 'H', 4: 'I', 8: 'Q'}[self._size]


class String(Datum):
    """String data item class.
    """
    def __init__(self, size: int, default: str = None, fixed: str = None):
        default = default or ''
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value: str) -> bytes:
        return bytes(value, 'utf-8')

    def value(self, raw_value: bytes) -> str:
        return re.sub(br'\x00*$', b'', raw_value).decode('utf-8')

    @property
    def _struct_format(self) -> str:
        return '!%ds' % self._size


class Bytes(Datum):
    """Bytes data item class.
    """
    def __init__(self, size: int, default: bytes = None, fixed: bytes = None):
        default = default or b''
        super().__init__(size, default=default, fixed=fixed)

    def raw_value(self, value: bytes) -> bytes:
        return value

    def value(self, raw_value: bytes) -> bytes:
        return raw_value

    @property
    def _struct_format(self) -> str:
        # not 'p' because only for 's' is the count the item size
        return '!%ds' % self._size
