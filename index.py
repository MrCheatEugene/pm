#!/usr/bin/env python
from http import HTTPStatus
import asyncio
import json
import traceback
import websockets
import os
import base64
import ssl

if not os.path.exists('files'):
    os.mkdir('files')

password = 'adminadmin'
server_password = '123'
connected_users = []
identities = {}
admins = []
auth_sockets = []

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

        if websocket not in auth_sockets and  server_password != '':
            if len(msg.split('AUTH_'))>1 and msg.split('AUTH_')[1] == server_password:
                auth_sockets.append(websocket)
                await websocket.send('OK')
            else:
                #print(len(msg.split('AUTH_'))>1, msg.split('AUTH_'), server_password)
                await websocket.close()
                return

        if websocket not in connected_users:
            connected_users.append(websocket)
            identities[websocket] = {}
        if len(msg.split('ADMIN_'))>1 and msg.split("_")[1] == password:
            admins.append(websocket)
            await websocket.send("OK")
        if len(msg.split('USERNAME_'))>1:
            identities[websocket]['username'] = msg.split('USERNAME_')[1]
            await websocket.send("OK")
        elif len(msg.split('KICK_'))>1 and websocket in admins:
            u = get_user(msg.split('_')[1])
            ws = list(identities.keys())[list(identities.values()).index(u)]
            await kickws(ws)
            await ws.close()
            await websocket.send("OK")
        elif len(msg.split('PGP_'))>1:
            identities[websocket]['pgp'] = msg.split('PGP_')[1]
            await websocket.send("OK")
        elif msg=='PGPLIST':
            pgplist = {}
            for u in identities.values():
                #print(u)
                if u!= {} and 'username' in u.keys() and 'pgp' in u.keys():
                    pgplist[u['username']] = u['pgp']
            await websocket.send(json.dumps({'type': 'pgplist', 'result': pgplist}))
        elif len(msg.split("_"))>=3 and (msg.split('_')[0] == 'VOICE' or msg.split('_')[0] == 'TEXT' or msg.split('_')[0] == 'POSTFILE'):
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
        elif len(msg.split('FILE_'))==2:
            print(msg, "UPLOAD")
            if len(msg.split('_'))==3:
                fid = msg.split('_')[2].replace('/', '').replace('.','').replace('\\', '')
                with open(f'files/{fid}', 'ab') as f:
                    f.write(base64.b64decode(msg.split('_')[1]))
                await websocket.send(json.dumps({'type':'fid', 'fid': fid, 'status': True}))
            else:
                fid = os.urandom(32).hex()
                with open(f'files/{fid}', 'wb') as f:
                    f.write(base64.b64decode(msg.split('FILE_')[1]))
                await websocket.send(json.dumps({'type':'fid','fid': fid, 'status': True}))

async def process_request(path, headers):
    print(path)
    if path != '/':
        fid = path.split('/')[1].replace('/', '').replace('.','').replace('\\', '')
        if fid != '' and os.path.exists(f'files/{fid}'):
            with open(f'files/{fid}', 'rb') as f:
                file = f.read()
            fn = "\""+path.split('/')[2].replace('/', '').replace('..','').replace('\\', '')+"\""
            return [HTTPStatus.OK, {'Content-Type': 'application/octet-stream', 'Content-Disposition': 'attachment; filename='+fn}, file]
    return None

async def main():
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ssl_context.load_cert_chain('cert.pem','privkey.pem')
    async with websockets.serve(index, "0.0.0.0", 20979, ssl=ssl_context, process_request=process_request):
        await asyncio.Future()

asyncio.run(main())
