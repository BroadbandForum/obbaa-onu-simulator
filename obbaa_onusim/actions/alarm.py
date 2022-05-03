from ..action import Action
from ..message import Message
from ..types import FieldDict

class Alarm(Message):
    def __init__(self, _no_validate: bool = False, **fields):
        self.bitmap = bytes(fields.get('bitmap'))
        self.seqNum = fields.get('seqNum')
        super().__init__(_no_validate, **fields)


    def validate(self) -> FieldDict:

        return {'bitmap': self.bitmap, 'seqNum': self.seqNum}


    def encode_contents(self) -> bytearray:
        num = 0 | int.from_bytes(self.bitmap,'big') << 32 | self.seqNum
        contents = bytearray(num.to_bytes(32,'big'))


        return contents
    
    def process(self, server: object):
        server.database.set_alarm(self.me_class,self.me_inst, self.bitmap,
                                 self.onu_id, extended=self.extended)


class AlarmResponse(Message):
    pass


alarm_action = Action(16, 'Alarm', 'Alarm action', Alarm, AlarmResponse)
"""Alarm `Action`.

This specifies the message type and provides a link between the action's
command and response messages.
"""

        


    