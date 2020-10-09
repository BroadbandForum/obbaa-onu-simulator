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

"""TBD."""

import sys

# this is needed to instantiate the MIBs
import obbaa_onusim.database

from obbaa_onusim.mib import mibs


def main(argv=None):
    """Main program."""

    if argv is None:
        # noinspection PyUnusedLocal
        argv = sys.argv

    for _, mib in sorted(mibs.items(), key=lambda i: i[1].number):
        print(mib.info())
        print('  attrs')
        for attr in mib.attrs:
            data = ', '.join(str(d) for d in attr.data)
            print('    %s (%s, %s) %s' % (attr.info(), attr.access,
                                          attr.requirement, data))
        print('  actions')
        for action in mib.actions:
            print('    %s' % action.info())
        if mib.notifications:
            print('  notifications')
            for notification in mib.notifications:
                print('    %s' % notification.info())
        if mib.changes:
            print('  changes')
            for change in mib.changes:
                print('    %s' % change.info())
        if mib.alarms:
            print('  alarms')
            for alarm in mib.alarms:
                print('    %s' % alarm.info())


if __name__ == "__main__":
    sys.exit(main())
