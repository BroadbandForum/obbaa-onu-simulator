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

"""TR-451 ONU simulator.

Simulates one or more ONU instances on a single channel termination.

Examples:

    ONU channel termination name ``x`` with ONU ids 0 through 99 and with
    support for extended messages::

        onusim.py --ctermname x --onuidfirst 0 --onuidlast 99 --extended

    All defaults with logging level 2 (debug)::

        onusim.py -l 2

Messages addressed to an invalid channel termination name or ONU id are ignored
(no response will be generated). This might be a mistake.
"""

import argparse
import logging
import os
import sys

import obbaa_onusim.endpoint as endpoint
import obbaa_onusim.util as util

# XXX want just the name part; need some utilities / rules / conventions
prog_basename = os.path.basename(sys.argv[0])
(prog_root, _) = os.path.splitext(prog_basename)
logger = logging.getLogger(prog_root)


def argparser() -> argparse.ArgumentParser:
    # create the parser and adds common arguments
    parser = util.argparser(prog=prog_root, description=__doc__,
                            default_address='0.0.0.0')
    # could now add additional arguments
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

    server = endpoint.Endpoint((args.address, args.port), is_server=True,
                               cterm_name=args.ctermname,
                               onu_id_range=onu_id_range, dumpfd=dumpfd)
    logger.debug('server %r' % server)

    def process():
        message, address = server.recv()
        logger.info('received message %r from %r' % (message, address))

        response = server.process(message)
        if response:
            server.send(response, address)
            logger.info('sent response %r to %r' % (response, address))

    while True:
        # XXX need debug mode (?) to control whether to catch exceptions
        if True:
            process()
        else:
            try:
                process()
            except Exception as e:
                logger.error('%s: %s' % (e.__class__.__name__, e))
                # XXX need to make this conditional (support debugging)
                if isinstance(e, (
                        AssertionError, AttributeError, FileNotFoundError,
                        KeyError, NameError, RecursionError, TypeError,
                        ValueError)):
                    raise

    # XXX need a clean exit mechanism
    if dumpfd:
        dumpfd.close()


if __name__ == "__main__":
    sys.exit(main())
