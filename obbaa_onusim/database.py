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

"""MIB database access.

This will currently only really work on the server side, but it makes sense
also to have a client-side database, populated via `get <get_action>` and
`MIB upload <mib_upload_action>` actions.
"""

import logging
import time

from typing import Dict, List, Optional, Tuple

from . import util

from .mib import Attr, MIB, M, RW
from .mibs.onu_g import onu_g_mib
from .mibs.onu2_g import onu2_g_mib
from .mibs.onu_data import onu_data_mib
from .mibs.software_image import software_image_mib
from .types import AttrDataValues

logger = logging.getLogger(__name__.replace('obbaa_', ''))

# XXX should these, esp. snapshot, more explicitly, maybe via class(es)
Instance = Dict[str, AttrDataValues]
Snapshot = Tuple[bool, int, list]

# note the startup time
startup_time = time.time()

# this determines whether the server supports extended messages
# XXX this currently only affects the omcc_version attribute
extended_supported = True
omcc_version_baseline = 0xa3
omcc_version_extended = 0xb4
omcc_version = extended_supported and omcc_version_extended or \
               omcc_version_baseline

# XXX could read these from JSON/YAML files
# XXX should define classes similar to the MIB classes
#: MIB instance specs (these are instantiated on all ONUs).
#:
#: Note:
#:   These specs should be read from JSON/YAML files.
specs = (
    (onu_g_mib, (
        {'me_inst': 0, 'vendor_id': 1234, 'version': 'v2',
         'serial_number': ('abcdefgh', 5678)},
    )),
    (onu2_g_mib, (
        {'me_inst': 0, 'omcc_version': omcc_version,
         'sys_up_time': lambda: int(100.0 * (time.time() - startup_time))},
    )),
    (onu_data_mib, (
        {'me_inst': 0, 'mib_data_sync': 0},
    )),
    (software_image_mib, (
        {'me_inst': 0x0000},
        {'me_inst': 0x0001},
        {'me_inst': 0x0100},
        {'me_inst': 0x0101}
    ))
)

#: Implemented MIBs, i.e. the MIBs referenced by the MIB instance specs.
mibs = {s[0].number: s[0] for s in specs}

# this controls whether optional attributes are implemented (explicitly
# defined optional attributes are always implemented)
optional = False


class Results:
    """Database results class (used for all database operations).
    """

    def __init__(self):
        """Database results constructor.
        """

        #: Reason, result (used by all operations).
        self.reason: int = 0b0000

        #: Attribute mask (used by most operations).
        self.attr_mask: int = 0x0000

        #: Optional-attribute mask (used with reason 0b1001).
        self.opt_attr_mask: int = 0x0000

        #: Attribute-execution mask (used with reason 0b1001).
        self.attr_exec_mask: int = 0x0000

        #: Attributes and their values (used by `Database.get`).
        self.attrs: List[Tuple[Attr, AttrDataValues]] = []

        #: Number of upload-nexts (used by `Database.upload`).
        self.num_upload_nexts: int = 0

        #: Next message body (used by `Database.upload_next`).
        self.body: List[int, List[Snapshot]] = [0, []]

    def __str__(self):
        return '%s(reason=%#03x, attr_mask=%#06x, ' \
               'opt_attr_mask=%#06x, attr_exec_mask=%#06x, ' \
               'attrs=%r, num_upload_nexts=%d, body=%r)' % (
                   self.__class__.__name__, self.reason, self.attr_mask,
                   self.opt_attr_mask, self.attr_exec_mask, self.attrs,
                   self.num_upload_nexts, self.body)

    __repr__ = __str__


# XXX should extract common logic, e.g. finding the instance and common results
# XXX should consider whether any of these logic can be in messages; maybe not,
#     because only this module should know about instances
class Database:
    """MIB database class.
    """

    def __init__(self, onu_id_range: range):
        """MIB database constructor.

        Args:
            onu_id_range: ONU id range, e.g. ``range(10)`` means ONU ids 0, 1,
                ...9. An identical database is instantiated for each of these
                ONU ids.
        """
        self._instances: Dict[int, Dict[Tuple[int, int], Instance]] = {}
        self._snapshots: Dict[int, Snapshot] = {}
        self._instantiate(onu_id_range)

    def _instantiate(self, onu_id_range: range) -> None:
        self._instances = {}
        self._snapshots = {}
        for onu_id in onu_id_range:
            self._reload(onu_id)

    def _reload(self, onu_id: int) -> None:
        self._instances[onu_id] = self.__reload()
        self._snapshots[onu_id] = (False, 0, [])

    @classmethod
    def _mib(cls, me_class: int) -> MIB:
        return mibs.get(me_class, None)

    @classmethod
    def _mib_names(cls) -> str:
        return ', '.join(
                str(m) for _, m in sorted(mibs.items(), key=lambda i: i[0]))

    def _instance(self, onu_id: int, me_class: int, me_inst: int) -> \
            Tuple[MIB, Optional[Instance], int]:
        mib = self._mib(me_class)
        instance = None
        reason = 0b0000
        if not mib:
            logger.error('MIB %d not implemented; MIBs: %s' % (
                me_class, self._mib_names()))
            reason = 0b0100
        else:
            instances_for_onu_id = self._instances.get(onu_id, {})
            instance = instances_for_onu_id.get((me_class, me_inst), None)
            if not instance:
                logger.error('ONU %d MIB %s #%d not instantiated; instances: '
                             '%s' % (onu_id, mib, me_inst,
                                     self._instance_names(onu_id, mib.number)))
                reason = 0b0101
            else:
                logger.debug('instance %r' % instance)
        return mib, instance, reason

    def _instance_names(self, onu_id: int, me_class: int) -> str:
        instances = self._instances.get(onu_id, {})
        return ', '.join([str(i) for n, i in
                          sorted(instances.keys(), key=lambda k: k[0]) if
                          n == me_class])

    def set(self, onu_id, me_class, me_inst, attr_mask, values, *,
            extended=False) -> Results:
        """Set the specified attribute values.

        Args:
            onu_id: ONU id.
            me_class: MIB class.
            me_inst: MIB instance.
            attr_mask: attributes to set.
            values: values to which attributes will be set.
            extended: whether an extended message has been requested.

        Returns:
            Results object, including `reason` and `opt_attr_mask`.
        """
        logger.debug('set onu_id=%d, me_class=%d, me_inst=%d, '
                     'attr_mask=%#06x values=%r, extended=%r' % (
                         onu_id, me_class, me_inst, attr_mask, values,
                         extended))
        updated = False
        results = Results()
        mib, instance, results.reason = self._instance(onu_id, me_class,
                                                       me_inst)
        if mib and instance:
            for index, index_mask in util.indices(attr_mask):
                attr = mib.attr(index)
                if not attr:
                    # XXX this isn't really of interest
                    logger.debug('MIB %s #%d %d not found' % (mib, me_inst,
                                                              index))
                    if results.reason in {0b0000, 0b1001}:
                        results.reason = 0b1001
                        results.opt_attr_mask |= index_mask
                elif attr.access != RW:
                    logger.warning('MIB %s #%d %s ignored (not writable)' % (
                        mib, me_inst, attr))
                    results.reason = 0b0011
                elif attr.name not in instance:
                    logger.warning(
                            'MIB %s #%d %s ignored (not implemented)' % (
                                mib, me_inst, attr))
                else:
                    # XXX also check value is valid for type
                    name = attr.name
                    assert name in values
                    value = values[name]
                    # XXX there should be utilities for going to and from
                    #     tuples
                    value = value if isinstance(value, tuple) else (
                        value,) if value is not None else None
                    if instance[name] != value:
                        instance[name] = value
                        updated = True
                        logger.info(
                            'MIB %s #%d %s = %r' % (mib, me_inst, attr, value))

        # if the MIB instance was updated, increment the MIB data sync counter
        # XXX we need utility functions for doing this sort of thing
        if updated:
            _, instance, _ = self._instance(onu_id, onu_data_mib.number, 0)
            assert instance is not None
            assert 'mib_data_sync' in instance
            # XXX sadly this is a tuple; the external interface should convert
            #     scalar data to/from tuples
            mib_data_sync = instance['mib_data_sync'][0]
            # values skip 0, i.e. 1 -> 2, ..., 254 -> 255, 255 -> 1, ...
            mib_data_sync = 1 if mib_data_sync >= 255 else mib_data_sync + 1
            instance['mib_data_sync'] = (mib_data_sync,)
            logger.info('updated: MIB %s = %r' % (onu_data_mib, instance))

        return results

    def get(self, onu_id: int, me_class: int, me_inst: int, attr_mask: int, *,
            extended: bool = False) -> Results:
        """Get the specified attribute values.

        Args:
            onu_id: ONU id.
            me_class: MIB class.
            me_inst: MIB instance.
            attr_mask: requested attributes.
            extended: whether an extended message has been requested.

        Returns:
            Results object, including `reason`, `attr_mask` and
            `opt_attr_mask` and `attrs`.
        """
        logger.debug('get onu_id=%d, me_class=%d, me_inst=%d, '
                     'attr_mask=%#06x, extended=%r' % (
                         onu_id, me_class, me_inst, attr_mask, extended))
        results = Results()
        mib, instance, results.reason = self._instance(onu_id, me_class,
                                                       me_inst)
        if mib and instance:
            size = 0
            for index, index_mask in util.indices(attr_mask):
                attr = mib.attr(index)
                if not attr:
                    # XXX this isn't really of interest
                    logger.debug('MIB %s #%d %d not found' % (mib, me_inst,
                                                              index))
                    if results.reason in {0b0000, 0b1001}:
                        results.reason = 0b1001
                        results.opt_attr_mask |= index_mask
                elif attr.name not in instance:
                    logger.debug('MIB %s #%d %s ignored (not implemented)' % (
                        mib, me_inst, attr))
                elif not extended and size + attr.size > 25:
                    # XXX this isn't really of interest
                    logger.debug('MIB %s #%d %s ignored (too long for '
                                 'baseline message)' % (mib, me_inst,
                                                        attr))
                    # ref G.988 section 11.2.9; returning a parameter error
                    # was recommended (see Jira OBBAA-237)
                    # XXX we allow future smaller attributes to be
                    #     included; should we?
                    results.reason = 0b0011
                else:
                    value = attr.resolve(instance[attr.name])
                    logger.debug('MIB %s #%d %s = %r' % (mib, me_inst, attr,
                                                         value))
                    results.attr_mask |= index_mask
                    results.attrs += [(attr, value)]
                    size += attr.size
        return results

    def upload(self, onu_id, me_class, me_inst, *, extended=False) -> Results:
        """Prepare for uploading MIBs.

        This involves taking a snapshot and calculating how many subsequent
        `Database.upload_next` operations will be needed.

        Args:
            onu_id: ONU id.

            me_class: MIB class (MUST be the ONU Data MIB class, i.e. 2).

            me_inst: MIB instance (MUST be the ONU Data MIB instance, i.e. 0).

            extended: whether an extended message has been requested (if so,
                the subsequent `Database.upload_next` operations MUST
                also request extended messages).

        Returns:
            Results object, including `reason` and `num_upload_nexts`.
        """
        logger.debug('upload onu_id=%d, me_class=%d, me_inst=%d, extended=%r'
                     % (onu_id, me_class, me_inst, extended))
        results = Results()
        mib, instance, results.reason = self._instance(onu_id, me_class,
                                                       me_inst)
        if mib and instance:
            if mib != onu_data_mib:
                logger.error('MIB %s invalid for upload; must be %s' % (
                    mib, onu_data_mib))
                results.reason = 0b0100
            else:
                # XXX some MIBs and attributes should potentially be excluded
                max_contents_length = 1966 if extended else 32
                chunk_header_length = 8 if extended else 6
                bodies = []
                body = [0, []]
                for key, instance in sorted(self._instances[onu_id].items(),
                                            key=lambda i_: i_[0]):
                    logger.info('key %r instance %r' % (key, instance))
                    me_class, me_inst = key
                    mib = self._mib(me_class)
                    assert mib is not None
                    chunk = [chunk_header_length, [], me_class, me_inst]
                    for attr in (a for a in mib.attrs if
                                 a.number > 0 and a.name in instance):
                        if body[0] + chunk[0] + attr.size > \
                                max_contents_length:
                            if chunk[0] > chunk_header_length:
                                body[0] += chunk[0]
                                body[1] += [chunk]
                            bodies += [body]
                            body = [0, []]
                            chunk = [chunk_header_length, [], me_class,
                                     me_inst]
                        chunk[0] += attr.size
                        # noinspection PyUnresolvedReferences
                        value = attr.resolve(instance[attr.name])
                        # shallow copy (tuple) values
                        # XXX this assumes it's already a tuple
                        chunk[1] += [(attr, value[:])]
                    if chunk[1]:
                        body[0] += chunk[0]
                        body[1] += [chunk]
                if body:
                    bodies += [body]

                # report
                for i, body in enumerate(bodies):
                    logger.info('body %d (%d)' % (i, body[0]))
                    for j, chunk in enumerate(body[1]):
                        logger.info('  chunk %d (%d) %s #%d' % (
                            j, chunk[0], self._mib(chunk[2]), chunk[3]))
                        for attr_value in chunk[1]:
                            attr, value = attr_value
                            logger.info('    attr %s %r (%d)' % (
                                attr, value, attr.size))

                # latch (OK to do after sampling because we're single-threaded)
                # XXX do we latch unconditionally? I think so
                latch_time = int(time.time())
                self._snapshots[onu_id] = (extended, latch_time, bodies)
                results.num_upload_nexts = len(bodies)
        return results

    def upload_next(self, onu_id, me_class, me_inst, seq_num, *,
                    extended=False) -> Results:
        """Upload the next part of a snapshot that was previously saved via
        `Database.upload`.

        Args:
            onu_id: ONU id.

            me_class: MIB class (MUST be the ONU Data MIB class, i.e. 2).

            me_inst: MIB instance (MUST be the ONU Data MIB instance, i.e. 0).

            extended: whether an extended message has been requested (if so,
                the earlier `Database.upload` operation MUST have also
                requested extended messages).

        Returns:
            Results object, including `reason` and `body`.
        """
        logger.debug('upload_next onu_id=%d, me_class=%d, me_inst=%d, '
                     'seq_num=%r, extended=%r' % (
                         onu_id, me_class, me_inst, seq_num, extended))
        results = Results()
        mib, instance, results.reason = self._instance(onu_id, me_class,
                                                       me_inst)
        if mib and instance:
            if mib != onu_data_mib:
                logger.error('MIB %s invalid for upload; must be %s' % (
                    mib, onu_data_mib))
                results.reason = 0b0100
            else:
                now = int(time.time())
                snapshot_extended, latch_time, bodies = self._snapshots[onu_id]
                if now - latch_time > 60:
                    logger.warning('snapshot was never taken or has timed out')
                    results.reason = 0b0001
                elif extended != snapshot_extended:
                    def eb(e): return e and 'extended' or 'baseline'
                    logger.error("snapshot calculated for %s, so can't get "
                                 "using %s message" % (
                                     eb(snapshot_extended), eb(extended)))
                elif seq_num not in range(len(bodies)):
                    logger.error('invalid seq_num %d; should be in range '
                                 '0:%d' % (seq_num, len(bodies) - 1))
                    results.reason = 0b0001
                else:
                    results.body = bodies[seq_num]
        return results

    def reset(self, onu_id, me_class, me_inst, *, extended=False) -> Results:
        """Reset the specified MIB instance.

        Args:
            onu_id: ONU id.
            me_class: MIB class.
            me_inst: MIB instance.
            extended: whether an extended message has been requested.

        Returns:
            Results object, including `reason`.
        """
        logger.debug('reset onu_id=%d, me_class=%d, me_inst=%d, '
                     'extended=%r' % (onu_id, me_class, me_inst, extended))
        results = Results()
        mib, instance, results.reason = self._instance(onu_id, me_class,
                                                       me_inst)
        if mib and instance:
            if mib != onu_data_mib:
                logger.error('MIB %s invalid for reset; must be %s' % (
                    mib, onu_data_mib))
                results.reason = 0b0100
            else:
                self._reload(onu_id)
        return results

    @classmethod
    def __reload(cls) -> Dict[Tuple[int, int], Instance]:
        """Reload all MIB instances from the specs.
        """
        insts = {}
        for mib, insts_spec in specs:
            mib_insts = insts.get(mib.number, {})
            for inst_spec in insts_spec:
                inst = {}
                assert 'me_inst' in inst_spec, "instance spec %r must " \
                                               "contain an 'me_inst' item" % \
                                               inst_spec
                me_inst = inst_spec['me_inst']
                assert me_inst not in mib_insts, "'me_inst' %r is already " \
                                                 "defined" % me_inst
                names = {a.name for a in mib.attrs}
                assert all(k in names for k in inst_spec), \
                    "one or more instance spec keys %r is invalid" % \
                    list(inst_spec.keys())
                for attr in mib.attrs:
                    name = attr.name
                    data = attr.data
                    values = []
                    if name in inst_spec:
                        spec_values = inst_spec[name]
                        if not isinstance(spec_values, tuple):
                            spec_values = (spec_values,)
                        assert len(spec_values) == len(data), "number of " \
                                                              "values mismatch"
                        for i, value in enumerate(spec_values):
                            datum = data[i]
                            assert isinstance(value, type(
                                    datum.default)) or callable(
                                    value), 'value %r is not of type %s' % (
                                value, type(datum.default).__name__)
                            # noinspection PyPep8
                            assert datum.fixed is None or value == \
                                datum.fixed, 'value %r differs from the ' \
                                             'required fixed value %r' % (
                                value, datum.fixed)
                            # XXX use a helper to check value is within range
                            values += [value]
                    elif optional or attr.requirement == M:
                        for datum in data:
                            values += [
                                datum.fixed if datum.fixed is not None else
                                datum.default if datum.default is not None
                                else None]
                    if values:
                        inst[name] = tuple(values)
                key = (mib.number, me_inst)
                assert key not in insts, "MIB %s 'me_inst' %r already " \
                                         "defined" % (mib, me_inst)
                insts[key] = inst
        return insts
