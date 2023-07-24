import asyncio
import logging
import websockets
import names
from datetime import datetime

from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from aiofile import async_open
from aiopath import Path

from exchange.exchange import show_data


logging.basicConfig(level=logging.INFO)

class Server:
    clients = set()

    async def register(self, ws:WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'User: {ws.name} [{ws.remote_address}] - connects!')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'User: {ws.name} [{ws.remote_address}] - disconnects!')

    async def send_to_clients(self, message: str):
        if self.clients:
            await asyncio.gather(*(client.send(message) for client in self.clients))

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        except Exception as e:
            logging.exception(e) 
        finally:
            await self.unregister(ws)
    

    async def write_log(self, data: str):
        async with async_open(Path('logs/log.txt'), 'a') as fh:
            await fh.write(data + '\n') 

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message.startswith('exchange'):
                data = await show_data(int(message.split(' ')[1].strip()))

                exchanges = []
                for el in data:
                    for key, value in el.items():
                        exchanges.append(f"{key} - EUR [{value['EUR']['buy']}], USD [{value['USD']['buy']}] | ")

             
                task_1 = self.write_log(f'{str(datetime.now())} - [INFO] - {ws.name} using command exchange!')
                task_2 = self.send_to_clients(f'{ws.name}: {"".join(exchanges)}')
                
                await asyncio.gather(task_1, task_2)
            else:
                await self.send_to_clients(f'{ws.name}: {message}')

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Event().wait()

if __name__ == '__main__':
    asyncio.run(main())