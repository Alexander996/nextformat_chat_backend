import asyncio
import websockets


HOST = 'localhost'
PORT = ':8000'
URL = 'ws://{}{}/ws/connect'.format(HOST, PORT)


async def test():
    print('Try connect to - ', URL, '...')
    async with websockets.connect(URL) as ws:
        status = await ws.recv()
        if 'success_auth' in status:
            print('Connection OK')
        else:
            print('Error, connection failed')
            return

        user_id = input("Enter user id: ")
        message = '{"event": "auth", "data": {"id": ' + user_id + '}}'
        await ws.send(message)

        while True:
            msg = await ws.recv()
            print("Server > {}".format(msg))

asyncio.get_event_loop().run_until_complete(test())
