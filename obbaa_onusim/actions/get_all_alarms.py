import logging
from ..action import Action
from ..message import Message
from ..types import Bytes, FieldDict
from ..types import Number, FieldDict

logger = logging.getLogger(__name__.replace('obbaa_', ''))


class GetAllAlarms(Message):

    def validate(self) -> FieldDict:
        alarm_retrieval_mode = 0 or 1
        return {'alarm_retrieval_mode': alarm_retrieval_mode}


    def encode_contents(self) -> bytearray:
        contents = bytearray()

        alarm_retrieval_mode = self.alarm_retrieval_mode
        contents += Number(1).encode(alarm_retrieval_mode)


        return contents
    
    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.
        """
        offset = 0

        alarm_retrieval_mode, offset = Number(1).decode(contents, offset)
        
        return {'alarm_retrieval_mode': alarm_retrieval_mode}

    def process(self, server: object) -> 'GetAllAlarmsResponse':

        results=server.database.get_all_alarms(self.onu_id, self.me_class,
                                      self.me_inst, extended=self.extended)

        
        response = GetAllAlarmsResponse(cterm_name=self.cterm_name,
                                         onu_id=self.onu_id,
                                         extended=self.extended, tci=self.tci,
                                         me_class=self.me_class,
                                         me_inst=self.me_inst,
                                         num_alarms_nexts = results.num_alarms_nexts)
        return response


class GetAllAlarmsResponse(Message):
    
    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(self.num_alarms_nexts)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``num_alarms_nexts``: number of `GetAllAlarmsNext` commands
              required; 0-65535
        """
        num_alarms_nexts, _ = Number(2).decode(contents, 0)
        return {'num_alarms_nexts': num_alarms_nexts}


class GetAllAlarmsNext(Message):
    """Get All Alarms next command message.
    """

    def encode_contents(self) -> bytearray:
        contents = Number(2).encode(self.seq_num)
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``seq_num``: command sequence number; 0-65535
        """
        seq_num, _ = Number(2).decode(contents, 0)
        return {'seq_num': seq_num}

    def process(self, server: object) -> 'GetAllAlarmsNextResponse':
        results = server.database.get_all_alarms_next(self.onu_id, self.me_class,
                                              self.me_inst, self.seq_num,
                                              extended=self.extended)


        response = GetAllAlarmsNextResponse(cterm_name=self.cterm_name,
                                         onu_id=self.onu_id,
                                         extended=self.extended, tci=self.tci,
                                         me_class=self.me_class,
                                         me_inst=self.me_inst,
                                         bit_map_alarms=results.bit_map_alarms,
                                         me_class_reported = results.me_class_reported,
                                         me_inst_reported = results.me_inst_reported)
        return response

class GetAllAlarmsNextResponse(Message):
    
    
    def encode_contents(self) -> bytearray:

        contents = bytearray()
        contents += Number(2).encode(self.me_class_reported)
        contents += Number(2).encode(self.me_inst_reported)
        contents += Bytes(28).encode(self.bit_map_alarms)
        
        return contents

    def decode_contents(self, contents: bytearray) -> FieldDict:
        """Decode this message's contents, i.e. its type-specific payload.

        Returns:
            Dictionary with the following items.

            * ``me_class.me_inst.bit_map_alarms`: the item name is the
               dot-separated ME class (MIB number), ME instance,
               and bit_map_alarms.
        """
        offset = 0

        # XXX review this termination criterion
        while offset < len(contents):

            me_class_alarm, offset = Number(2).decode(contents, offset)
            # XXX this is baseline-only; should be an error for extended
            if me_class_alarm == 0:
                break

            # if can't find MIB, can't proceed for baseline
            from ..mib import mibs
            mib = mibs.get(me_class_alarm, None)
            if mib is None:
                raise Exception('MIB %d not found' % me_class_alarm)

            me_inst_alarm, offset = Number(2).decode(contents, offset)

            bit_map_alarms, offset = Number(2).decode(contents, offset)
        
        return {'me_class_alarm': me_class_alarm, 'me_inst_alarm': me_inst_alarm, 'bit_map_alarms': bit_map_alarms}
    


get_all_alarms_action = Action(11, 'get-all-alarms', 'Get all alarms action', GetAllAlarms,
                           GetAllAlarmsResponse)
"""Get All alarms `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""

get_all_alarms_next_action = Action(12, 'get-all-alarms-next', 'Get all alarms next action', GetAllAlarmsNext,
                                GetAllAlarmsNextResponse)
"""Get All alarms next `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""
