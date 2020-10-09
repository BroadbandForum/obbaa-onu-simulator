# Extensions

We'll consider these two use cases:

* Supporting a new MIB (for use with already-implemented actions)
* Supporting new actions (for use with already-implemented MIBs)

It's currently necessary to modify the main software tree in order to add new MIBs and actions. It would be relatively easy (if needed) to allow such things to be stored in external plugin directories.

Please try to follow existing coding and documentation conventions.

## Supporting a new MIB

Suppose we want to implement the G.988 9.1.4 Cardholder MIB. This involves the following steps (details such as names are of course up to the implementer):

* Create a new `obbaa_onusim/mibs/cardholder.py` module that defines a `cardholder_mib` [MIB] object. Think of this object as a Cardholder MIB schema that contains information allowing Cardholder MIB instances to be created

* Edit the [`obbaa_onusim/database.py`][database] module to import the new module; this will force it to be executed and will therefore create the new Cardholder MIB schema object

* Optionally update the same module's [`specs`][specs] variable to cause one or more Cardholder instances to be created

### obbaa_onusim/mibs/cardholder.py

It's probably easiest to edit one of the existing MIB definitions. The file will begin something like this (what exactly is imported depends on what's needed):

```
"""Cardholder MIB (G.988 9.1.5).
"""

from ..actions.get import get_action
from ..actions.set import set_action
from ..mib import MIB, Alarm, Attr, Change, M, O, R, RW, \
    test_result_notification
from ..types import Bits, Bool, Enum, Number, String
```

This is followed by the first part of the [MIB] definition. The number 5 comes from G.988 Table 11.2.4-1 (Managed entity identifiers) and the rest comes from G.988 9.1.5. The idea is to represent this data as exactly as possible.

```
cardholder_mib = MIB(5, 'Cardholder', 'Represents the fixed equipment slot'
                                      'configuration of the ONU', attrs=(
```

This is followed by the [attribute (Attr)][Attr] definitions. Attribute 0 is always `me_inst`. As for the MIB, the first three arguments are its number, name and description, followed by access (`R`, a.k.a `Read`, is a predefined [Access] instance), requirement (`M`, a.k.a `Mandatory`, is a predefined [Requirement] instance) and data specification.

```
    Attr(0, 'me_inst', 'Managed entity instance', R, M, Number(2)),
```

The data specification is usually a single [Datum] instance but it can also be a tuple of Datum instances (tuples are currently only needed for the [ONU-G] `serial_number` attribute but will also be needed for table attributes). `Number(2)` states that it's a 2-byte number.

The next two attributes might be defined as follows:

```
    Attr(1, 'actual_plug_in_unit_type', 'Actual plug-in unit type', R, M,
         Number(1)),
    Attr(2, 'expected_plug_in_unit_type', 'Expected plug-in unit type', R, M,
         Number(1)),
```

These could also have been defined as `Enum`s (using the names and values defined in G.988 Table 9.1.5-1) but this doesn't seem worth it in this case.

The final attribute might be defined as follows:

```
    Attr(9, 'arc_interval', 'ARC interval', RW, O, Number(1))
```

...and is then followed by the actions, notifications, changes and alarms.

```
), actions=(
    get_action, set_action,
), notifications=(
), changes=(
    Change(1, 'actual_plug_in_unit_type'),
    Change(5, 'actual_equipment_id'),
    Change(8, 'arc')
), alarms=(
    Alarm(0, 'plug_in_circuit_pack_missing', '...'),
    ...
))
```

### obbaa_onusim/database.py (import)

You can base the new import on one of the existing imports.

Before:

```
from ..mibs.onu_g import onu_g_mib
from ..mibs.onu2_g import onu2_g_mib
from ..mibs.onu_data import onu_data_mib
from ..mibs.software_image import software_image_mib
```

After:

```
from ..mibs.onu_g import onu_g_mib
from ..mibs.onu2_g import onu2_g_mib
from ..mibs.onu_data import onu_data_mib
from ..mibs.software_image import software_image_mib
from ..mibs.cardholder import cardholder_mib
```

### obbaa_onusim/database.py (specs)

You can base the new specs on the existing specs.

Before:

```
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
```

After (this is just an example):

```
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
    )),
    (cardholder_mib, (
        {'me_inst': 0x0000, 'actual_plug_in_unit_type': 42},
        {'me_inst': 0x0000, 'actual_plug_in_unit_type': 43}
    ))
)
```

## Supporting a new action

Suppose we want to implement some of the software download actions. These are already referenced from the [Software image] MIB but they're just dummies. This involves the following steps (details such as names are of course up to the implementer):

*  Create a new `obbaa_onusim/actions/software.py` module that defines `start_download_action`, `download_section_action` etc..

* Edit the `obbaa_onusim/actions/other.py` module to remove the dummy implementations of these actions

* Edit the `obbaa_onusim/mibs/software_image.py` module to import the new implementations of these actions

### obbaa_onusim/actions/software.py

It's probably worth first taking a look at an existing action implementation, e.g. [set_action]. This defines:

* [Set] message
* [SetResponse] message
* [set_action], which references the Set and SetResponse messages

The new file might begin something like this:

```
"""The software download actions' messages are defined in G.988 A.2.23-32 (extended) and A.3.23-43 (baseline).

The relevant classes and instances are:

Start software download:
* `StartSoftwareDownload`: Start software download message class
* `StartSoftwareDownloadResponse`: Start software download response message
   class
* `start_software_download_action`: Start software download action instance

...
"""

import logging
import re

from .. import util

from ..action import Action
from ..message import Message
from ..mib import RW
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))
```

The classes will have the same general layout as the existing classes. Outlines are not yet shown. Refer to the [Message] and [Action] classes for more information.

Also, a new [database] operation may have to be added.

### obbaa_onusim/actions/other.py

Simply delete the definitions of the newly-implemented actions:

```
start_download_action = Action(19, 'start-download')
download_section_action = Action(20, 'download-section')
end_download_action = Action(21, 'end-download')
activate_image_action = Action(22, 'activate-image')
commit_image_action = Action(23, 'commit-image')
```

### obbaa_onusim/mibs/software_image.py

This is straightforward. For example:

Before:

```
from ..actions.other import start_download_action, download_section_action, \
    end_download_action, activate_image_action, commit_image_action
```

After:

```
from ..actions.software import start_download_action, \
    download_section_action, end_download_action, activate_image_action, \
    commit_image_action
```



[MIB]: MIB
[Attr]: Attr
[Access]: Access
[Requirement]: Requirement
[Datum]: Datum

[ONU-G]: onu_g_mib
[ONU2-G]: onu2_g_mib
[ONU data]: onu_data_mib
[Software image]: software_image_mib

[Set]: actions.set.Set
[SetResponse]: actions.set.SetResponse
[set_action]: actions.set.set_action

[database]: obbaa_onusim.database
[specs]: obbaa_onusim.database.specs

[Message]: obbaa_onusim.message.Message
[Action]: obbaa_onusim.action.Action
