from starlette.applications import Starlette
from starlette.websockets import WebSocketDisconnect
from starlette.responses import JSONResponse
import redis

app = Starlette()

redis_server = redis.Redis(host='redis', port=6379, password='')


@app.websocket_route('/')
async def ws_(ws):
    await ws.accept()
    await ws.send_text('Hi')
    await ws.close()


@app.websocket_route('/poll/{id}')
async def poll_for_notifications(ws):
    id = ws.path_params['id']
    await ws.accept()
    redis_server.sadd('connected_devices', id)

    ps = redis_server.pubsub()
    ps.subscribe(f"channel_device_{id}", "channel_device_common")
    print(f"Starting poll for {id}")

    try:
        while True:
            msg = ps.get_message()

            if msg and msg['type'] != 'subscribe':
                print("D: ", msg['type'])
                print(f"Got message: {msg}")
                data = msg['data'].decode("utf-8")

                await ws.send_text(data)
    except WebSocketDisconnect as e:
        print(e)
    finally:
        print(f"Client {id} dc")

    await ws.close()
    redis_server.srem('connected_devices', id)


@app.route('/post/{data}', methods=['POST'])
async def data_post(req):
    data = req.path_params['data']
    redis_server.publish('channel_device_common', data)
    return JSONResponse({
        'Status': 1
    })
