#!/usr/bin/env python
import asyncio
import json
import traceback
import websockets
import ssl
connected_users = []
identities = {}

async def kickws(websocket):
    try:
        connected_users.pop(connected_users.index(websocket))
        identities.pop(websocket)
    except:
        pass

def get_user(username):
    for u in identities.values():
        if u!= {} and 'username' in u.keys() and u['username'] == username:
            return u

async def index(websocket): 
    while True:
        try:
            msg = await websocket.recv()
        except:
            if websocket in connected_users or websocket:
                await kickws(websocket)
            continue

        if websocket not in connected_users:
            connected_users.append(websocket)
            identities[websocket] = {}

        if len(msg.split('USERNAME_'))>1:
            identities[websocket]['username'] = msg.split('USERNAME_')[1]
            await websocket.send("OK")
        elif len(msg.split('PGP_'))>1:
            identities[websocket]['pgp'] = msg.split('PGP_')[1]
            await websocket.send("OK")
        elif msg=='PGPLIST':
            pgplist = {}
            for u in identities.values():
                print(u)
                if u!= {} and 'username' in u.keys() and 'pgp' in u.keys():
                    pgplist[u['username']] = u['pgp']
            await websocket.send(json.dumps({'type': 'pgplist', 'result': pgplist}))
        elif len(msg.split("_"))>=3 and (msg.split('_')[0] == 'VOICE' or msg.split('_')[0] == 'TEXT' or msg.split('_')[0] == 'FILE'):
            try:
                type_og = msg.split('_')[0]
                type =  '_msg' if type_og == 'TEXT' else '' if type_og == 'VOICE' else '_file'
                u = get_user(msg.split('_')[1])
                ws = list(identities.keys())[list(identities.values()).index(u)]
                await ws.send(json.dumps({'type': f'receive{type}', 'from': identities[websocket]['username'], 'message': msg.split('_')[2]}))
                await websocket.send("OK")
            except Exception as e:
                print(e)
                traceback.print_exception(e)
                pass

    
async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('public.pem','privkey.pem')
    async with websockets.serve(index, "0.0.0.0", 20979, ssl=ssl_context):
        await asyncio.Future()

asyncio.run(main())
