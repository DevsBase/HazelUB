import websockets
import logging
import random 

logger = logging.getLogger(__name__)

class Client:
    def __init__(self, url: str) -> None:
        self.url: str = url
        self.hazel_id: int = 10000
        self.ws = None
    
    async def connect(self) -> bool:
        self.hazel_id = random.randint(10000, 99999)
        self.ws = await websockets.connect(self.url+f"ws/HazelUB?Hazel_ID={self.hazel_id}")
        return True
    
    async def getConn(self) -> object | None:
        return self.ws
    
    async def get(self):
        raise NotImplementedError
    
    async def post(self):
        raise NotImplementedError