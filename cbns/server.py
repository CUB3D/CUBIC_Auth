from starlette.applications import Starlette
from starlette.websockets import WebSocketDisconnect
from starlette.responses import JSONResponse
import aioredis
from aioredis.pubsub import Receiver

app = Starlette()

# redis_server = redis.Redis(host='redis', port=6379, password='')

REDIS_URL = "redis://redis:6379"


@app.websocket_route('/')
async def ws_(ws):
    await ws.accept()
    await ws.send_text('Hi')
    await ws.close()


async def poll_channel_manager(ws, channel):
    try:
        while await channel.wait_message():
            msg = await channel.get(encoding='utf-8')

            if msg:
                print(f"Got message: {msg}")

                await ws.send_text(msg)
    except WebSocketDisconnect as e:
        print(e)
    finally:
        print(f"Client {id} dc")


@app.websocket_route('/poll/{id}')
async def poll_for_notifications(ws):
    id = ws.path_params['id']
    await ws.accept()

    redis_server = await aioredis.create_redis(REDIS_URL)
    await redis_server.sadd('connected_devices', id)

    # multi_reciever = Receiver()
    # await redis_server.subscribe


    channel_device, channel_common = await redis_server.subscribe(f"channel_device_{id}", "channel_device_common")
    print(f"Starting poll for {id}")

    await poll_channel_manager(ws, channel_common)

    await ws.close()
    await redis_server.srem('connected_devices', id)


@app.route('/post/{data}', methods=['POST'])
async def data_post(req):
    data = req.path_params['data']
    redis_server = await aioredis.create_redis('redis://redis:6379')
    await redis_server.publish('channel_device_common', data)
    return JSONResponse({
        'Status': 1
    })
