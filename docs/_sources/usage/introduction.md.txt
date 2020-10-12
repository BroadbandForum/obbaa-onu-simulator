# Introduction

## Installation

The ONU simulator currently lives in the [obbaa-polt-simulator] Bitbucket repository (it will be in the `develop` branch, but at the time of writing is only in the `feature/OBBAA-237-william-onu-simulator-toplevel` branch). It lives in the `tr451_vomci_onu` subdirectory.

Having checked out the repository and gone to `tr451_vomci_onu`, you have two options:

1. Set `PYTHONPATH` and `PATH` manually. For example:

```
% export PYTHONPATH=$PWD
% export PATH=$PATH:$PWD/bin
```

2. Install the `obbaa-onusim` python package (this assumes that the necessary python tools are installed; note that you need python3, and that I've been using python3.6):

```
% pip3 install --upgrade .
```

Or you can run in Docker. See [Docker](#docker) below.

## ONU simulation server

The [ONU simulation server](bin.onusim) is an OMCI server that simulates one or
more ONUs on a single channel termination. It currently supports the following
[MIB]s and [action]s:

* [ONU-G] : [Get], [Set]
* [ONU2-G] : [Get], [Set]
* [ONU data] : [Get], [Set], [MIB reset], [MIB upload], [MIB upload next]
* [Software image] : [Get], [Set]

The server doesn't yet support events (notifications).

When the server starts up, it populates its [database] with (currently) the following [MIB] instances:

```
(
    (ONU_G_mib, (
        {'me_inst': 0, 'vendor_id': 1234, 'version': 'v2',
         'serial_number': ('abcdefgh', 5678)},
    )),
    (ONU2_G_mib, (
        {'me_inst': 0, 'omcc_version': omcc_version,
         'sys_up_time': lambda: int(100.0 * (time.time() - startup_time))},
    )),
    (ONU_DATA_mib, (
        {'me_inst': 0, 'mib_data_sync': 0},
    )),
    (SW_IMAGE_mib, (
        {'me_inst': 0x0000},
        {'me_inst': 0x0001},
        {'me_inst': 0x0100},
        {'me_inst': 0x0101}
    ))
)
```

By default, only mandatory attributes are implemented. Attributes that aren't explicitly defined in the above data structure will have the default values from the MIB definitions. For example, this (from [here][ONU-G]) specifies that the ONU-G MIB's `version` attribute (attribute #2) is a 14-byte string with a default of `v1`.

```
Attr(2, 'version', 'Version', R, M, String(14, default='v1')),
```

By default, the server will report only warnings and errors. In this example, the logging level is set to 2 (debug) but you are more likely to want to use level 1 (info).

```
% onusim.py -l 2
DEBUG:onusim:args Namespace(address='127.0.0.1', ctermname='cterm',
dumpfile=None, extended=False, loglevel=2, onuidfirst=42, onuidlast=None,
port=12345)
DEBUG:onusim:server Endpoint(address=('127.0.0.1', 12345), is_server=True,
cterm_name='cterm', onu_id_range=range(42, 43), tr451=True, dumpfd=None)
```

```
% onusim.py -l 1
<there's no level 1 output on startup>
```

## ONU test client

The [ONU test client](bin.onucli) is a simple command-line utility that (currently) just sends commands to a server and waits for a response.

For example (assuming that the server is running) this is what a baseline get looks like on the client (which defaults to logging level 1):

```
% onucli.py -h
usage: onucli [-h] [-a ADDRESS] [-p PORT] [-n CTERMNAME] [-i ONUIDFIRST]
              [-I ONUIDLAST] [-e] [-d [DUMPFILE]] [-l LOGLEVEL] [-t TCI]
              {set,get,reset,upload,upload-next} ...

[...]

positional arguments:
  {set,get,reset,upload,upload-next}
    set                 Set MIB instance attribute values. Supply the values
                        as one or more name=value pairs, where name is the
                        attribute name or number.
    get                 Get MIB instance attribute values.
    reset               Reset MIB instance values.
    upload              Prepare for upload of MIB instance values. The MIB
                        instance values are latched and will remain valid for
                        60 seconds. The returned num_upload_nexts value is
                        the number of upload-next invocations needed to
                        return them
    upload-next         Upload the next set of MIB instance values. The
                        supplied sequence number must be in the range 0 to
                        num_upload_nexts - 1. If upload hasn't been called,
                        or was called more than 60 seconds ago, no data will
                        be returned.

optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        server DNS name or IP address; default: '127.0.0.1'
  -p PORT, --port PORT  server UDP port number; default: 12345
  -n CTERMNAME, --ctermname CTERMNAME
                        channel termination name; default: 'cterm'
  -i ONUIDFIRST, --onuidfirst ONUIDFIRST
                        first ONU id; default: 42
  -I ONUIDLAST, --onuidlast ONUIDLAST
                        last ONU id; default: same as first
  -e, --extended        whether to use/support extended messages
  -d [DUMPFILE], --dumpfile [DUMPFILE]
                        file to which to dump hex messages; default (if value
                        omitted): 'dump.txt'
  -l LOGLEVEL, --loglevel LOGLEVEL
                        logging level (0=errors+warnings, 1=info, 2=debug);
                        default: 1
  -t TCI, --tci TCI     first TCI (Transaction Correlation Identifier);
                        default: 0
```

## Examples

### Get

```
% onucli.py get -h
usage: onucli get [-h] [me_class] [me_inst] [attr_mask]

positional arguments:
  me_class    ME class; default: 256
  me_inst     ME instance; default: 0
  attr_mask   ME instance; default: 65535

optional arguments:
-h, --help  show this help message and exit
```

```
% onucli.py get
INFO:onucli:sent message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) to ('127.0.0.1',
12345)
INFO:onucli:received response GetResponse(admin_state='unlock',
attr_mask=0xd600, battery_backup=False, cterm_name='cterm', extended=False,
me_class=256, me_inst=0, onu_id=42, opt_attr_mask=0x0, opt_exec_mask=0x0,
reason=3, tci=0, traffic_management='priority-controlled', vendor_id=1234,
version='v2') from ('127.0.0.1', 50654)
```

The server output is very similar (assuming that it's running at logging level
1) but is of course from its point of view:

```
INFO:onusim:received message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) from ('127.0.0.1',
52959)
INFO:onusim:sent response GetResponse(attr_exec_mask=0x0, attr_mask=0xd600,
cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42,
opt_attr_mask=0x0, reason=3, tci=0) to ('127.0.0.1', 52959)
```

What's going on here? Note that ``reason=3`` (Parameter error). Why? Ah, it must be because we're using baseline messages and there isn't room for all the requested attributes! Try running the server with logging level 2:

```
% onusim.py -l 2
DEBUG:onusim:args Namespace(address='127.0.0.1', ctermname='cterm', dumpfile=None, extended=False,
loglevel=2, onuidfirst=42, onuidlast=None, port=12345)
DEBUG:onusim:server Endpoint(address=('127.0.0.1', 12345), is_server=True, cterm_name='cterm',
onu_id_range=range(42, 43), tr451=True, dumpfd=None)
DEBUG:onusim.endpoint:received 76/2048 bytes from ('127.0.0.1', 55688)
DEBUG:onusim.endpoint:637465726d0000000000000000000000000000000000000000000000
0000002a0000490a01000000ffff00000000000000000000000000000000000000000000000000
000000000000000028
INFO:onusim:received message Get(attr_mask=0xffff, cterm_name='cterm', extended=False,
me_class=256, me_inst=0, onu_id=42, tci=0) from ('127.0.0.1', 60241)
DEBUG:onusim.database:get onu_id=42, me_class=256, me_inst=0, attr_mask=0xffff, extended=False
DEBUG:onusim.database:instance {'me_inst': (0,), 'vendor_id': (1234,), 'version': ('v2',),
'serial_number': ('abcdefgh', 5678), 'traffic_management': ('priority-controlled',),
'battery_backup': (False,), 'admin_state': ('unlock',)}
DEBUG:onusim.database:MIB 256(ONU-G) #0 1(vendor_id) = (1234,)
DEBUG:onusim.database:MIB 256(ONU-G) #0 2(version) = ('v2',)
DEBUG:onusim.database:MIB 256(ONU-G) #0 3(serial_number) ignored (too long for baseline message)
DEBUG:onusim.database:MIB 256(ONU-G) #0 4(traffic_management) = ('priority-controlled',)
DEBUG:onusim.database:MIB 256(ONU-G) #0 5 not found
DEBUG:onusim.database:MIB 256(ONU-G) #0 6(battery_backup) = (False,)
DEBUG:onusim.database:MIB 256(ONU-G) #0 7(admin_state) = ('unlock',)
DEBUG:onusim.database:MIB 256(ONU-G) #0 8(oper_state) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 9(survival_time) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 10(logical_onu_id) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 11(logical_password) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 12(credentials_status) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 13(extended_tc_options) ignored (not implemented)
DEBUG:onusim.database:MIB 256(ONU-G) #0 14 not found
DEBUG:onusim.database:MIB 256(ONU-G) #0 15 not found
DEBUG:onusim.database:MIB 256(ONU-G) #0 16 not found
DEBUG:onusim.endpoint:sent 76 bytes to ('127.0.0.1', 60241)
DEBUG:onusim.endpoint:637465726d0000000000000000000000000000000000000000000000
0000002a0000290a0100000003d600000004d27632000000000000000000000000000000000000
000000000000000028
INFO:onusim:sent response GetResponse(attr_exec_mask=0x0, attr_mask=0xd600,
cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42,
opt_attr_mask=0x0, reason=3, tci=0) to ('127.0.0.1', 55688)
```

You can see that options 1, 2, 4, 6 and 7 were included, but option 3 is too long and was ignored.

### omci_dump_decoder

The Broadcom `omci_dump_decoder` utility is attached to [OBBAA-237] and is included in the Docker image.

You can use the client or server `-d` or `--dumpfile` option to save a Hex dump of all the messages (the TR-451 `(cterm_name, onu_id)` header is not included). This can then be passed to `omci_dump_decoder`.

```
root@24ae9dfa1989:/# onucli.py -d dump.txt get
INFO:onucli:sent message Get(attr_mask=0xffff, cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) to ('127.0.0.1', 12345)
INFO:onucli:received response GetResponse(admin_state='unlock', attr_mask=0xd600, battery_backup=False, cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42, opt_attr_mask=0x0, opt_exec_mask=0x0, reason=3, tci=0, traffic_management='priority-controlled', vendor_id=1234, version='v2') from ('127.0.0.1', 12345)

root@24ae9dfa1989:/# cat dump.txt
# TCI  MT DI CLS  INST CONTENTS                                                         TRAILER
  0000 49 0a 0100 0000 ffff000000000000000000000000000000000000000000000000000000000000 00000028
# TCI  MT DI CLS  INST CONTENTS                                                         TRAILER
  0000 29 0a 0100 0000 03d600000004d276320000000000000000000000000000000000000000000000 00000028

root@24ae9dfa1989:/# omci_dump_decoder dump.txt
[2541645: I default             ] bcm_dev_log_task.c 1458| Logging started
[2541645: I OMCI_ME_LAYER       ] omci_stack_api.c 121| Using Broadcom OMCI Stack
[2541646: I OMCI_ME_LAYER       ] omci_dump_decoder.c 210| 1      # TCI  MT DI CLS  INST CONTENTS                                                         TRAILER
[2541646: I OMCI_ME_LAYER       ] omci_dump_decoder.c 210| 2        0000 49 0a 0100 0000 ffff000000000000000000000000000000000000000000000000000000000000 00000028
[2541646: I OMCI_ME_LAYER       ] omci_dump_decoder.c 273| >>> AR=1 AK=0 TCI=0 class=256(0x100) entity_id=0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8829| {olt=0 pon_if=0, onu_id=0, cookie=0}: Dump ME: onu_g (256), Entity: 0, Action: GET [
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8835| 	vendor_id:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8837| 	version:	00 00 00 00 00 00 00 00 00 00 00 00 00 00
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8839| 	serial_number:	00 00 00 00 00 00 00 00
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8841| 	traffic_management:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8843| 	deprecated0:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8845| 	battery_backup:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8847| 	admin_state:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8849| 	oper_state:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8851| 	survival_time:	0
[2541646: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8853| 	logical_onu_id:	00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8855| 	logical_password:	00 00 00 00 00 00 00 00 00 00 00 00
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8857| 	credentials_status:	0
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8859| 	extended_tc_options:	0x0
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8862| ]
[2541647: I OMCI_ME_LAYER       ] omci_dump_decoder.c 210| 3      # TCI  MT DI CLS  INST CONTENTS                                                         TRAILER
[2541647: I OMCI_ME_LAYER       ] omci_dump_decoder.c 210| 4        0000 29 0a 0100 0000 03d600000004d276320000000000000000000000000000000000000000000000 00000028
[2541647: I OMCI_ME_LAYER       ] omci_dump_decoder.c 251| <<< AR=0 AK=1 TCI=0 class=256(0x100) entity_id=0 result=3
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8829| {olt=0 pon_if=0, onu_id=0, cookie=0}: Dump ME: onu_g (256), Entity: 0, Action: GET [
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8835| 	vendor_id:	1234
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8837| 	version:	76 32 00 00 00 00 00 00 00 00 00 00 00 00
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8841| 	traffic_management:	0
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8845| 	battery_backup:	0
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8847| 	admin_state:	0
[2541647: D OMCI_ME_LAYER       ] omci_stack_enc_dec.c 8862| ]
```

## Docker

I've created an `obbaa-onu-simulator` Docker image. The image includes the ONU simulation servertest client and documentation.

**Note: The image is no longer based on the `obbaa-polt-simulator` image. It's
  therefore necessary to run the pOLT simulator in a different container.**

The scripts are installed using the usual python mechanisms, so it's not necessary to set `PYTHONPATH` or `PATH`. The documentation is in `/opt/obbaa-onu-simulator/docs/html`.

Docker networking features are host-dependent, and I've only tested this on a Mac ([Networking features in Docker Desktop for Mac](https://docs.docker.com/docker-for-mac/networking)).

### Docker server, host client

**Docker server**

For incoming traffic, the Docker container has to expose a port. This could be configured in the image.

With this command, on a Mac UDP traffic to `127.0.0.1:12345` will be sent to the Docker container and will be received by a server listening on `0.0.0.0:12345`.

```
% docker container run -it --name obbaa-onu-simulator --rm \
         -p 12345:12345/udp broadbandforum/obbaa-onu-simulator:latest bash

root@c1c6d167bee2:/# onusim.py -l 1
INFO:onusim:received message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) from ('172.17.0.1',
46917)
INFO:onusim:sent response GetResponse(attr_exec_mask=0x0, attr_mask=0xd600,
cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42,
opt_attr_mask=0x0, reason=3, tci=0) to ('172.17.0.1', 46917)
```

**Host client**

Default options work fine on the host.

```
% onucli.py get
INFO:onucli:sent message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) to ('127.0.0.1',
12345)
INFO:onucli:received response GetResponse(admin_state='unlock',
attr_mask=0xd600, battery_backup=False, cterm_name='cterm', extended=False,
me_class=256, me_inst=0, onu_id=42, opt_attr_mask=0x0, opt_exec_mask=0x0,
reason=3, tci=0, traffic_management='priority-controlled', vendor_id=1234,
version='v2') from ('127.0.0.1', 12345)
```

### Host server, Docker client

**Host server**

Default options work fine on the host.

```
% onusim.py -l 1
INFO:onusim:received message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) from ('127.0.0.1',
58054)
INFO:onusim:sent response GetResponse(attr_exec_mask=0x0, attr_mask=0xd600,
cterm_name='cterm', extended=False, me_class=256, me_inst=0, onu_id=42,
opt_attr_mask=0x0, reason=3, tci=0) to ('127.0.0.1', 58054)
```

**Docker client**

For outgoing traffic, no port needs to be exposed. The Docker container uses a special `host.docker.internal` DNS name to connect to a Mac host.

```
% docker container run -it --name obbaa-onu-simulator --rm \
         broadbandforum/obbaa-onu-simulator:latest bash

root@da41e01238b0:/# onucli.py -a host.docker.internal get
INFO:onucli:sent message Get(attr_mask=0xffff, cterm_name='cterm',
extended=False, me_class=256, me_inst=0, onu_id=42, tci=0) to
('host.docker.internal', 12345)
INFO:onucli:received response GetResponse(admin_state='unlock',
attr_mask=0xd600, battery_backup=False, cterm_name='cterm', extended=False,
me_class=256, me_inst=0, onu_id=42, opt_attr_mask=0x0, opt_exec_mask=0x0,
reason=3, tci=0, traffic_management='priority-controlled', vendor_id=1234,
version='v2') from ('192.168.65.2', 12345)
```

### Docker server, Docker client

Running the server and client in the same Docker container just works (even if the same port is exposed externally).

I haven't experimented with running the server and client in different Docker containers but I don't think it will be difficult.

### With tr451_polt_simulator: new (using docker-compose)

With this `.env` file:

```
COMPOSE_PROJECT_NAME=onusim
```

And this `docker-compose.yaml` file:

```
version: '3'

services:
  # can use this with default options from the host
  cterm:
    image: 'broadbandforum/obbaa-onu-simulator:latest'
    ports:
      - '12345:12345/udp'
    command: onusim.py -l 1 -n cterm -i 1 -I 100

  # can use this with the options in Igor's example
  cterm1:
    image: 'broadbandforum/obbaa-onu-simulator:latest'
    ports:
      - '50001:50000/udp'
    command: onusim.py -l 2 -p 50000 -n channeltermination.1 -i 1 -I 100

  # can use this with the options in Igor's example (but different chan term)
  # XXX temporarily use the same channel termination name
  cterm2:
    image: 'broadbandforum/obbaa-onu-simulator:latest'
    ports:
      - '50002:50000/udp'
    command: onusim.py -l 2 -p 50000 -n channeltermination.1 -i 1 -I 100

  polt:
    depends_on:
      - cterm1
    image: 'broadbandforum/obbaa-polt-simulator:latest'
    volumes:
      - '$APPROOT:/app'
    ports:
      - '8433:8433/tcp'
    stdin_open: true
    tty: true
    working_dir: /opt/obbaa-polt-simulator/build/fs
    # XXX with gdb doesn't run; should use gdb -ex run option?
    # XXX can't set onu_sim_ip = cterm1; have to use IP address but what is it?
    #     (for now, hard-coded in /app/share/polt.cli)
    command: >
      bash -c "apt-get update
      && apt-get --yes install valgrind
      && ./start_tr451_polt.sh valgrind -log debug -f /app/share/polt.cli -d"

  vomci:
    depends_on:
      - polt
    image: 'broadbandforum/obbaa-polt-simulator:latest'
    volumes:
      - '$APPROOT:/app'
    stdin_open: true
    tty: true
    working_dir: /opt/obbaa-polt-simulator/build/fs
    command: ./start_tr451_polt.sh -log debug -f /app/share/vomci.cli -d

  # after docker-compose up, do docker-compose ps to determine the vomci
  # container name (probably onusim_vomci_1) and then do docker attach <name>;
  # can then enter interactive commands
  # beware that ^C will terminate the container so do ^P^Q to detach
```

**Start up services:**

```
% docker-compose up
Starting onusim_cterm2_1 ... done
Starting onusim_cterm1_1 ... done
Starting onusim_cterm_1  ... done
Starting onusim_polt_1   ... done
Starting onusim_vomci_1  ... done
Attaching to onusim_cterm1_1, onusim_cterm_1, onusim_cterm2_1, onusim_polt_1, onusim_vomci_1
cterm1_1  | DEBUG:onusim:args Namespace(address='0.0.0.0', ctermname='channeltermination.1', dumpfile=None, extended=False, loglevel=2, onuidfirst=1, onuidlast=100, port=50000)
...
...
polt_1    | [1008214: I POLT                ] bcm_tr451_polt_common.cc 458| ONU channeltermination.1:1 is assigned to remote endpoint vomci1
```

**Attach to vomci and inject commands:**

Determine container name:

```
% docker-compose ps
     Name                    Command               State            Ports
-----------------------------------------------------------------------------------
onusim_cterm1_1   onusim.py -l 2 -p 50000 -n ...   Up      0.0.0.0:50001->50000/udp
onusim_cterm2_1   onusim.py -l 2 -p 50000 -n ...   Up      0.0.0.0:50002->50000/udp
onusim_cterm_1    onusim.py -l 1 -n cterm -i ...   Up      0.0.0.0:12345->12345/udp
onusim_polt_1     bash -c apt-get update &&  ...   Up      0.0.0.0:8433->8433/tcp
onusim_vomci_1    ./start_tr451_polt.sh -log ...   Up
```

Attach:

```
% docker attach onusim_vomci_1
```

Inject:

```
/po/inject channeltermination.1 1 0054480a01000000040001000000000000000000000000000000000000000000000000000000000000000028
```

Detach:

```
^P^Q
read escape sequence
%
```

**Output (in services window):**

```
vomci_1   | /po/inject channeltermination.1 1 0054480a01000000040001000000000000000000000000000000000000000000000000000000000000000028
vomci_1   | [1390503: D POLT                ] sim_tr451_polt_vendor.cc 117| RX from ONU: cterm=channeltermination.1 onu_id=1 length=48 OMCI_HDR=0054480a 01000000
polt_1    | [1390559: D POLT                ] sim_tr451_polt_vendor.cc 191| TX to ONU: cterm=channeltermination.1 onu_id=1 length=48 OMCI_HDR=0054480a 01000000
cterm2_1  | DEBUG:onusim.endpoint:received 80/2048 bytes from ('172.20.0.5', 50100)
cterm2_1  | ERROR:onusim.message:OMCI message length (80) doesn't match expected length (76)
cterm2_1  | DEBUG:onusim.endpoint:6368616e6e656c7465726d696e6174696f6e2e310000000000000000000000010054480a0100000004000100000000000000000000000000000000000000000000000000000000000000002800000000
cterm2_1  | INFO:onusim:received message Set(attr_mask=0x400, cterm_name='channeltermination.1', extended=False, me_class=256, me_inst=0, onu_id=1, tci=84, values={'battery_backup': 1}) from ('172.20.0.5', 50100)
cterm2_1  | DEBUG:onusim.database:set onu_id=1, me_class=256, me_inst=0, attr_mask=0x0400 values={'battery_backup': 1}, extended=False
cterm2_1  | DEBUG:onusim.database:instance {'me_inst': (0,), 'vendor_id': (1234,), 'version': ('v2',), 'serial_number': ('abcdefgh', 5678), 'traffic_management': ('priority-controlled',), 'battery_backup': (False,), 'admin_state': ('unlock',)}
cterm2_1  | INFO:onusim.database:MIB 256(ONU-G) #0 6(battery_backup) = (1,)
cterm2_1  | DEBUG:onusim.database:instance {'me_inst': (0,), 'mib_data_sync': (0,)}
cterm2_1  | INFO:onusim.database:updated: MIB 2(ONU data) = {'me_inst': (0,), 'mib_data_sync': (1,)}
cterm2_1  | DEBUG:onusim.endpoint:sent 76 bytes to ('172.20.0.5', 50100)
cterm2_1  | DEBUG:onusim.endpoint:6368616e6e656c7465726d696e6174696f6e2e310000000000000000000000010054280a01000000000000000000000000000000000000000000000000000000000000000000000000000028
cterm2_1  | INFO:onusim:sent response SetResponse(attr_exec_mask=0x0, cterm_name='channeltermination.1', extended=False, me_class=256, me_inst=0, onu_id=1, opt_attr_mask=0x0, reason=0, tci=84) to ('172.20.0.5', 50100)
polt_1    | [1390570: D POLT                ] bcm_tr451_polt_common.cc 689| Sent OMCI message to ONU channeltermination.1:1. 48 bytes
polt_1    | [1390587: D POLT                ] sim_tr451_polt_vendor.cc 117| RX from ONU: cterm=channeltermination.1 onu_id=1 length=44 OMCI_HDR=0054280a 01000000
vomci_1   | [1390629: D POLT                ] sim_tr451_polt_vendor.cc 191| TX to ONU: cterm=channeltermination.1 onu_id=1 length=44 OMCI_HDR=0054280a 01000000
vomci_1   | [1390629: D POLT                ] bcm_tr451_polt_common.cc 689| Sent OMCI message to ONU channeltermination.1:1. 44 bytes
```

**Shut down services (in services window):**

^C

```
Gracefully stopping... (press Ctrl+C again to force)
Stopping onusim_vomci_1  ... done
Stopping onusim_polt_1   ... done
Stopping onusim_cterm1_1 ... done
Stopping onusim_cterm2_1 ... done
Stopping onusim_cterm_1  ... done
%
```

### With tr451_polt_simulator: old (not using docker-compose)

[OBBAA-237][OBBAA-237-test] explains how a second `tr451_polt_simulator` instance can be used to inject test OMCI messages. Here's how I tried it.

I defined these aliases:

```
% alias onu='docker container run -it --name obbaa-onu-simulator --rm -v $APPROOT:/app -w /opt/obbaa-polt-simulator/build/fs broadbandforum/obbaa-onu-simulator:latest'
% alias onue='docker container exec -it obbaa-onu-simulator bash'
```

`onu` runs the container and `onue` ("ONU exec") execs bash in the running container (so effectively logs into it).

I copied the certificates (attached to OBBAA-237) to `./share`, so they are available at `/app/share` in the container.

I followed the instructions in `obbaa-polt-simulator/README.md` and OBBAA-237.

Note:

1. The README says to run `bin/start_netconf_server.sh` but I assume that's a typo because that script doesn't exist

**Window 1: ONU simulator**

The simulator is started with the same port, cterm_name and onu_id that Igor uses below.

Command:

```
onusim.py -n channeltermination.1 -i 1 -p 50000 -l 2
```

Output:

```
DEBUG:onusim:args Namespace(address='0.0.0.0', ctermname='channeltermination.1',
dumpfile=None, extended=False, loglevel=2, onuidfirst=1, onuidlast=None, port=50000)
DEBUG:onusim:server Endpoint(address=('0.0.0.0', 50000), is_server=True,
cterm_name='channeltermination.1', onu_id_range=range(1, 2), tr451=True, dumpfd=None)
```

**Window 2: pOLT simulator #1 (pOLT)**

Command:

```
./start_tr451_polt.sh -d
```

Script (`./share/polt.cli`):

```
/po/set client_server=server enable=yes
/po/au priv_key=/app/share/polt_privatekey.pem local_cert=/app/share/polt.cer peer_cert=/app/share/vomci.cer
/po/en client_server=server name=polt port=8433
/polt/filter client_server=server name=filt1 priority=100 ep_name=vomci1 Type=any
/po/onu channel_term=channeltermination.1 onu_id=1 serial_vendor_id=BRCM serial_vendor_specific=00000001
```

```
/po/rx_mode mode=onu_sim onu_sim_ip=127.0.0.1 onu_sim_port=50000 local_udp_port=50100
```

**Window 3: pOLT simulator #2 (vOMCI)**

Command:

```
./start_tr451_polt.sh -d
```

Script (`./share/vomci.cli`):

```
/po/au priv_key=/app/share/vomci_privatekey.pem local_cert=/app/share/vomci.cer peer_cert=/app/share/polt.cer
/po/set client_server=client enable=yes
/po/end client_server=client name=polt1 port=8433 host=localhost
/po/filter client_server=client name=filt1 priority=100 ep_name=polt1 Type=any
/po/onu channel_term=channeltermination.1 onu_id=1 serial_vendor_id=BRCM serial_vendor_specific=00000001
```

```
/po/inject channeltermination.1 1 0054480a01000000040001000000000000000000000000000000000000000000000000000000000000000028
```

Window 1: ONU simulator:

```
DEBUG:onusim.endpoint:received 80/2048 bytes from ('127.0.0.1', 50100)
ERROR:onusim.message:OMCI message length (80) doesn't match expected length (76)
DEBUG:onusim.endpoint:6368616e6e656c7465726d696e6174696f6e2e310000000000000000000000010054480a0100000004000100000000000000000000000000000000000000000000000000000000000000002800000000
INFO:onusim:received message Set(attr_mask=0x400, cterm_name='channeltermination.1', extended=False, me_class=256, me_inst=0, onu_id=1, tci=84, values={'battery_backup': 1}) from ('127.0.0.1', 50100)
DEBUG:onusim.database:set onu_id=1, me_class=256, me_inst=0, attr_mask=0x0400 values={'battery_backup': 1}, extended=False
DEBUG:onusim.database:instance {'me_inst': (0,), 'vendor_id': (1234,), 'version': ('v2',), 'serial_number': ('abcdefgh', 5678), 'traffic_management': ('priority-controlled',), 'battery_backup': (False,), 'admin_state': ('unlock',)}
INFO:onusim.database:MIB 256(ONU-G) #0 6(battery_backup) = (1,)
DEBUG:onusim.database:instance {'me_inst': (0,), 'mib_data_sync': (0,)}
INFO:onusim.database:updated: MIB 2(ONU data) = {'me_inst': (0,), 'mib_data_sync': (1,)}
DEBUG:onusim.endpoint:sent 76 bytes to ('127.0.0.1', 50100)
DEBUG:onusim.endpoint:6368616e6e656c7465726d696e6174696f6e2e310000000000000000000000010054280a01000000000000000000000000000000000000000000000000000000000000000000000000000028
INFO:onusim:sent response SetResponse(attr_exec_mask=0x0, cterm_name='channeltermination.1', extended=False, me_class=256, me_inst=0, onu_id=1, opt_attr_mask=0x0, reason=0, tci=84) to ('127.0.0.1', 50100)
```

<!-- links -->

[obbaa-polt-simulator]: https://code.broadband-forum.org/projects/OBBAA/repos/obbaa-polt-simulator/browse

[OBBAA-237]: https://issues.broadband-forum.org/browse/OBBAA-237

[OBBAA-237-test]: https://issues.broadband-forum.org/browse/OBBAA-237?focusedCommentId=70976&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-70976

[MIB]: MIB
[action]: Action

[ONU-G]: onu_g_mib
[ONU2-G]: onu2_g_mib
[ONU data]: onu_data_mib
[Software image]: software_image_mib

[Get]: actions.get
[Set]: actions.set
[MIB reset]: actions.reset
[MIB upload]: actions.upload
[MIB upload next]: actions.upload

[database]: obbaa_onusim.database
