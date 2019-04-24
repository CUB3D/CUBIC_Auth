from starlette.applications import Starlette
from starlette.websockets import WebSocketDisconnect
from starlette.responses import JSONResponse
import aioredis
from aioredis.pubsub import Receiver
import asyncio
import sys

app = Starlette()

REDIS_URL = "redis://redis:6379"

@app.websocket_route('/')
async def ws_(ws):
    await ws.accept()
    await ws.send_text('Hi')
    await ws.close()


async def poll_channel_manager(ws, reciever):
    try:
        async for channel, msg in reciever.iter(encoding='utf-8'):
            print(f"Got message: {msg} on {channel.name.decode('utf-8')} {ws.application_state}", file=sys.stderr)

            await ws.send_text(msg)
    except Exception as e:
        print(e, file=sys.stderr)
    print(f"Client {ws} dc", file=sys.stderr)


@app.websocket_route('/poll/{id}')
async def poll_for_notifications(ws):
    id = ws.path_params['id']
    await ws.accept()
    print(f"Starting poll for {id}", file=sys.stderr)

    redis_server = await aioredis.create_redis(REDIS_URL)
    await redis_server.sadd('connected_devices', id)

    multi_reciever = Receiver()

    channel_device = multi_reciever.channel(f"channel_device_{id}")
    channel_common = multi_reciever.channel("channel_device_common")
    await redis_server.subscribe(channel_device, channel_common)

    await poll_channel_manager(ws, multi_reciever)

    print(f"Closing websocket for {id}", file=sys.stderr)
    await ws.close()
    # Need a new redis instance, the other one is locked to sub mode after .subscribe
    redis_server = await aioredis.create_redis(REDIS_URL)
    await redis_server.srem('connected_devices', id)


@app.route('/post/{data}', methods=['POST'])
async def data_post(req):
    data = req.path_params['data']
    redis_server = await aioredis.create_redis('redis://redis:6379')
    await redis_server.publish('channel_device_common', data)
    return JSONResponse({
        'Status': 1
    })
