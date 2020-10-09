#!/usr/bin/env python3

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

"""TR-451 ONU command-line client.

Sends OMCI commands to an ONU simulator instance on a single channel
termination.

Examples:

    These examples assume that an ONU simulator instance is listening on the
    default address and port. If not, commands will time out after 10 seconds.

    Get (using all defaults)::

        % ./onucli.py get
        <TBD; ADD LATER>

    Get (using extended messages)::

        % ./onucli.py --extended get
        <TBD; ADD LATER>

    The returned attribute mask is ``0xf600``, indicating that the
    response includes ONU-G attributes 1-4, 6 and 7 (these are the mandatory
    ones). The optional-attribute mask is ``0x0807``, indicating that
    attributes 5 and 14-16 are unsupported (these are the deprecated and
    undefined ones). The remaining (optional) attributes are implemented but
    not present in ONU-G instance 0.

    Get (help text)::

        % ./onucli.py get --help
        usage: onucli get [-h] [me_class] [me_inst] [attr_mask]

        positional arguments:
            me_class    ME class; default: 256
            me_inst     ME instance; default: 0
            attr_mask   ME instance; default: 65535

        optional arguments:
            -h, --help  show this help message and exit

"""

import argparse
import logging
import os
import sys

import obbaa_onusim.actions as actions
import obbaa_onusim.endpoint as endpoint
import obbaa_onusim.util as util

from obbaa_onusim.mibs.onu_g import onu_g_mib
from obbaa_onusim.mibs.onu_data import onu_data_mib

# XXX want just the name part; need some utilities / rules / conventions
prog_basename = os.path.basename(sys.argv[0])
(prog_root, _) = os.path.splitext(prog_basename)
logger = logging.getLogger(prog_root)


def argparser() -> argparse.ArgumentParser:
    # create the parser and add common arguments
    parser = util.argparser(prog=prog_root, description=__doc__,
                            default_loglevel=1)

    # add additional arguments
    default_tci = 0
    parser.add_argument("-t", "--tci", type=int, default=default_tci,
                        help="first TCI (Transaction Correlation Identifier); "
                             "default: %r" % default_tci)

    # add sub-parsers, one for each supported action
    # XXX should add description and/or epilog subparser help strings
    subparsers = parser.add_subparsers(dest='cmd')

    def add_me_arguments(parser_):
        default_me_class = onu_g_mib.number
        default_me_inst = 0

        parser_.add_argument("me_class", type=int, default=default_me_class,
                             nargs="?",
                             help="ME class; default: %r" % default_me_class)
        parser_.add_argument("me_inst", type=int, default=default_me_inst,
                             nargs="?",
                             help="ME instance; default: %r" % default_me_inst)

    def default_me_arguments(parser_):
        parser_.set_defaults(me_class=onu_data_mib.number, me_inst=0)

    # Set
    set_help = """Set MIB instance attribute values.

    Supply the values as one or more name=value pairs, where name is the
    attribute name or number.
    """
    set_parser = subparsers.add_parser("set", aliases=["s"],
                                       help=util.cleandoc(set_help))
    add_me_arguments(set_parser)
    set_parser.add_argument("attrs", type=lambda a: a.split('=', 1), nargs="+",
                            help = "attributes to set; each is of "
                                   "the form name=value")

    # Get
    default_attr_mask = 0xffff

    get_help = """Get MIB instance attribute values.
    """
    get_parser = subparsers.add_parser("get", aliases=["g"],
                                       help=util.cleandoc(get_help))
    add_me_arguments(get_parser)
    get_parser.add_argument("attr_mask", type=lambda m: util.toint(m),
                            default=default_attr_mask, nargs="?",
                            help="Attribute mask (0b, 0o and 0x prefixes "
                                 "are OK); "
                                 "default: %r" % default_attr_mask)

    # Reset
    reset_help = """Reset MIB instance values.
    """
    reset_parser = subparsers.add_parser("reset", aliases=["r"],
                                         help=util.cleandoc(reset_help))
    default_me_arguments(reset_parser)

    # Upload
    upload_help = """Prepare for upload of MIB instance values.

    The MIB instance values are latched and will remain valid for 60
    seconds. The returned num_upload_nexts value is the number of
    upload-next invocations needed to return them
    """
    upload_parser = subparsers.add_parser("upload", aliases=["u"],
                                          help=util.cleandoc(upload_help))
    default_me_arguments(upload_parser)

    # Upload next
    default_seq_num = 0

    upload_next_help = """Upload the next set of MIB instance values.

    The supplied sequence number must be in the range 0 to num_upload_nexts
    - 1.

    If upload hasn't been called, or was called more than 60 seconds ago,
    no data will be returned.
    """
    upload_next_parser = subparsers.add_parser("upload-next", aliases=["un"],
                                               help=util.cleandoc(
                                                       upload_next_help))
    default_me_arguments(upload_next_parser)
    upload_next_parser.add_argument("seq_num", type=int,
                                    default=default_seq_num, nargs="?",
                                    help="Sequence number; default: %r" %
                                         default_seq_num)

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv

    args = argparser().parse_args(argv[1:])

    loglevel_map = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}
    logging.basicConfig(level=loglevel_map[args.loglevel])

    logger.debug('args %r' % args)

    dumpfd = util.openfile(args.dumpfile)

    # XXX should validate [first, last]
    if args.onuidlast is None:
        args.onuidlast = args.onuidfirst
    onu_id_range = range(args.onuidfirst, args.onuidlast + 1)

    client = endpoint.Endpoint((args.address, args.port), is_server=False,
                               cterm_name=args.ctermname,
                               onu_id_range=onu_id_range, dumpfd=dumpfd)
    logger.debug('client %r' % client)

    # just send to all ONUs with ids in the range
    def process():
        tci = args.tci
        cmd = args.cmd
        for onu_id in onu_id_range:
            fields = {'cterm_name': args.ctermname, 'tci': tci,
                      'extended': args.extended, 'onu_id': onu_id}
            tci = (tci + 1) & 0xffff

            # XXX there's a better way of doing this: use set_defaults()
            if cmd in {'get', 'g'}:
                message = actions.get.Get(me_class=args.me_class,
                                          me_inst=args.me_inst,
                                          attr_mask=args.attr_mask, **fields)
            elif cmd in {'set', 's'}:
                values = {a[0]: (a[1] if len(a) > 1 else True) for a in
                          args.attrs}
                message = actions.set.Set(me_class=args.me_class,
                                          me_inst=args.me_inst,
                                          values=values, **fields)
            elif cmd in {'reset', 'r'}:
                message = actions.reset.MibReset(me_class=args.me_class,
                                                 me_inst=args.me_inst,
                                                 **fields)
            elif cmd in {'upload', 'u'}:
                message = actions.upload.MibUpload(me_class=args.me_class,
                                                   me_inst=args.me_inst,
                                                   **fields)
            elif cmd in {'upload-next', 'un'}:
                message = actions.upload.MibUploadNext(me_class=args.me_class,
                                                       me_inst=args.me_inst,
                                                       seq_num=args.seq_num,
                                                       **fields)
            else:
                raise Exception('unrecognised command %r' % args.cmd)

            client.send(message)
            logger.info(
                    'sent message %r to %r' % (message, client.server_address))

            response, address = client.recv()
            if response:
                logger.info(
                        'received response %r from %r' % (response, address))
                response2 = client.process(response)
                if response2:
                    logger.error('unexpected response response %r' % response2)

    # XXX need debug mode (?) to control whether to catch exceptions
    if args.cmd is None:
        # XXX this could enter an interactive mode
        logger.warning('no command given; nothing to do!')
    elif False:
        process()
    else:
        try:
            process()
        except Exception as e:
            logger.error('%s: %s' % (e.__class__.__name__, e))
            if isinstance(e, (
                    AssertionError, AttributeError, FileNotFoundError,
                    KeyError, NameError, RecursionError, TypeError,
                    ValueError)):
                raise

    if dumpfd:
        dumpfd.close()


if __name__ == "__main__":
    sys.exit(main())
