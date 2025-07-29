from dataclasses import dataclass
from fmconsult.utils.enum import CustomEnum
from fmconsult.utils.object import CustomObject

class SendType(CustomEnum):
  SEQUENTIALLY = 'SEQUENTIALLY'
  NON_SEQUENTIALLY = 'NON_SEQUENTIALLY'

@dataclass
class Webhook(CustomObject):
  name: str
  url: str
  email: str
  events: list[str]
  enabled: bool = True
  authToken: str = None
  apiVersion: str = "3"
  interrupted: bool = False
  sendType: SendType = SendType.SEQUENTIALLY