# START OF ONU-SIMULATOR

Onu-Simulator presents a process that runs to receive data from Polt Simulator, and on the other hand presents a side process that sends data to Polt Simulator. In the latter case, this data refers to the alarms that are processed and sent upstream.
Starting with the process of receiving data from Polt Simulator:
- The file to run is onusim.py
- The arguments used are:
   - Port (-p), that in this case port 50000 is used
   - Channel Termination (-n) (ex. CT_1, CT_2 ...)
   - Onu ID (-i) (ex. 1, 2 ...)
   - Logs (-l) (details of Onu-Simulator)

So the command to run would be as follows:

- onusim.py -p 50000 -n CT_1 -i 1 -l 2

By running this command, we can then send downstream the data that we want to receive in the Onu Simulator.

# SEND ALARMS FROM ONU-SIMULATOR

As mentioned before, there is another lateral process that sends the alarms. To verify this process, having obviously run the command described above, we will have to proceed with the following steps:
- Click on the <enter> key, where you will be asked to put the input command
- The arguments used to send the alarms are the following:
    - Name of what will be sent (Alarm, Notification, Changes)
    - Entity Class (ex. 7, 11 ...)
    - Entity Instance (ex. 1, 2 ...)
    - Frame consisting of 28 bytes regarding the status of the alarms to be sent (ex. ff000000000000000000000000000000000000000000000000000000)
    - Sequence Number (ex. 1, 2 ...)

After clicking on the <enter> key while running the command in onusim.py, you will proceed with the following command:

- alarm 11 1 80000000000000000000000000000000000000000000000000000000 1 (ex.)

The alarm will be sent upstream and the vOMCI Function will check if it has been received. The command described above can be used as many times as necessary, depending on the alarms to be sent.

# ONU simulator and test client
See the full [documentation](docs/html/index.html).
