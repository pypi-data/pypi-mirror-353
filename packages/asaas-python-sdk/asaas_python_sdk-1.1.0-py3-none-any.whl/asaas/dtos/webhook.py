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
    enabled: bool
    interrupted: bool
    apiVersion: str = "3"
    authToken: str
    sendType: SendType
    events: list[str]