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

"""Various utility functions."""

import argparse
import inspect
import logging
import re

from typing import Any, IO, Optional, Tuple

logger = logging.getLogger(__name__.replace('obbaa_', ''))


def argparser(prog: str, description: str, **kwargs) -> \
        argparse.ArgumentParser:
    """Argument parser helper.

    Args:
        prog: program name, typically from ``sys.argv[0]``.

        description: program description, typically from ``__doc__``.

        **kwargs: additional arguments; currently supported keys are
            ``default_xxx`` for argument ``xxx``, e.g. ``default_address``.

    Returns:
        Argument parser, with common options added.
    """
    default_address = kwargs.get('default_address', '127.0.0.1')
    default_port = kwargs.get('default_port', 12345)
    default_ctermname = kwargs.get('default_ctermname', 'cterm')
    default_onuidfirst = kwargs.get('default_onuid', 42)
    default_onuidlast = kwargs.get('default_onuidlast', None)
    default_dumpfile = kwargs.get('default_dumpfile', 'dump.txt')
    default_loglevel = kwargs.get('default_loglevel', 0)

    formatter_class = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(prog=prog, description=description,
                                     fromfile_prefix_chars='@',
                                     formatter_class=formatter_class)

    parser.add_argument("-a", "--address", type=str, default=default_address,
                        help="server DNS name or IP address; default: %r" %
                             default_address)
    parser.add_argument("-p", "--port", type=int, default=default_port,
                        help="server UDP port number; default: %r" %
                             default_port)

    parser.add_argument("-n", "--ctermname", type=str,
                        default=default_ctermname,
                        help="channel termination name; default: %r" %
                             default_ctermname)
    parser.add_argument("-i", "--onuidfirst", type=int,
                        default=default_onuidfirst,
                        help="first ONU id; default: %r" % default_onuidfirst)
    parser.add_argument("-I", "--onuidlast", type=int,
                        default=default_onuidlast,
                        help="last ONU id; default: %s" % (
                            "same as first" if default_onuidlast is None
                            else str(
                                    default_onuidlast)))

    parser.add_argument("-e", "--extended", action="store_true",
                        help="whether to use/support extended messages")

    parser.add_argument("-d", "--dumpfile", nargs="?", const=default_dumpfile,
                        default=None,
                        help="file to which to dump hex messages; default ("
                             "if value omitted): %r" % default_dumpfile)

    parser.add_argument("-l", "--loglevel", type=int, default=default_loglevel,
                        help="logging level (0=errors+warnings, "
                             "1=info, 2=debug); default: %r" %
                             default_loglevel)

    return parser


def cleandoc(docstring):
    """Clean documentation string (docstring) per PEP 257 rules.

    Args:
        docstring: supplied docstring.

    Returns:
        Clean docstring.

    Note:
        This is just a wrapper around ``inspect.cleandoc``.
    """
    return inspect.cleandoc(docstring)

# XXX should move this to mib.py and integrate with Attr.mask etc.
def indices(mask: int) -> Tuple[Tuple[int, int], ...]:
    """Attribute indices helper.

    Args:
        mask: the attribute mask for which to return the indices.

    Returns:
        Tuple of (``index``, ``index_mask``) tuples, where ``index`` is in the
        range 1 through 16 (inclusive).
    """
    indices_ = []
    for index in range(1, 17):
        index_shift = 16 - index  # 15, 14, ..., 0
        index_mask = 1 << index_shift
        if index_mask & mask:
            indices_ += [(index, index_mask)]
    return tuple(indices_)


def openfile(spec: Optional[str]) -> Optional[IO[str]]:
    """Open file helper.

    Args:
        spec: file/mode spec; for example:

            * ``file`` uses mode ``w``
            * ``file+`` uses mode ``a``
            *  ``file+r`` uses mode ``r``

    Returns:
        File object, or ``None`` if spec is ``None``.
    """
    if spec is None:
        return None
    else:
        parts = spec.split('+', 1)
        name = parts[0]
        mode = parts[1] if len(parts) > 1 else 'w'
        mode = mode or 'a'
        return open(name, mode=mode, buffering=1)


# helper to convert string to int (supports bases 2, 8, 10 and 16)
def toint(x: Any):
    """String to integer conversion helper.

    Supports bases 2, 8, 10 and 16.

    Args:
        x: value to convert

    Returns:
        Integer.

    Note:
        It'll throw an exception if given an invalid string.
    """
    if not isinstance(x, (str, bytes, bytearray)):
        return int(x)
    else:
        match = re.match('^0([box])', x.lower().decode('ascii','ignore'))
        base = {'b': 2, 'o': 8, 'x': 16}[match.group(1)] if match else 10

        if not isinstance(x,int):
            x=0
            return int(x)
        else:
            return int(x, base)

