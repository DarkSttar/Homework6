import asyncio
import logging
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import names
from assistant import connect_to_server
import json
from main import BOT_NAME,AUTH

#UPDATINGGG=========================================

logging.basicConfig(level=logging.INFO)
class Server:
    def __init__(self) -> None:
        
        self.clients = dict()
        self.connectBot =  None
        self.Bot = None
        
        
        
    async def register(self,ws:WebSocketServerProtocol):                        
        if self.Bot == None:
            name = ws.request_headers.get('Client-name')
            auth = ws.request_headers.get('AUTH')
            if name == BOT_NAME and auth == AUTH:
                ws.name = name
                self.Bot = ws        
                print(f'{BOT_NAME} connect!')
        else:
            ws.name = names.get_full_name()
            self.clients.update({ws.name:ws}) 
        logging.info(f'{ws.remote_address} Connects')
        logging.info(f'Client Name: {ws.name}')
    
    async def unregister(self,ws:WebSocketServerProtocol):
        del self.clients[ws.name]
        logging.info(f'{ws.remote_address} Disconects')

    
    
    async def connect_bot(self):
        while True:
            if self.Bot == None:    
                connect = asyncio.create_task(connect_to_server())
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(1)
                if self.Bot.closed:  
                    print(f'Assistant Disconnect!')
                    self.Bot = None
                
                
               
    async def send_to_clients(self,message_for_client:str,current_client=None):
            if current_client:
                await self.clients[current_client].send(message_for_client)
            elif self.clients:
                for names in self.clients:
                    await self.clients[names].send(message_for_client)
    async def send_to_Assistant(self,message_for_bot):
        if self.Bot:
            await self.Bot.send(message_for_bot)           
    
    
    async def ws_handler(self, ws: WebSocketServerProtocol):
        
        await self.register(ws) # Реєструємо клієнта    
        
        try:
            print(self.Bot)
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)
        #await self.send_to_clients(f'{ws.name}: Message')
    
    
    async def distrubute(self,ws:WebSocketServerProtocol):    
        async for message in ws:
                    if ws.name == BOT_NAME:
                        arguments = json.loads(message)  
                        await self.send_to_clients(message_for_client=arguments['Message'],current_client=arguments['Target-Client'])
                    else:
                        arguments = {
                            "Name": ws.name,
                            "Message":message
                        }
                        
                        arguments_str = json.dumps(arguments)
                        await self.send_to_Assistant(message_for_bot=arguments_str)
                        await self.send_to_clients(message_for_client=f'{ws.name}: {message}')
            
                    
            
                

        

    
    