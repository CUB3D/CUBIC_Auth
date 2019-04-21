from starlette.applications import Starlette
import redis
from starlette.websockets import WebSocket

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
    redis_server.sadd('connected_devices', str(id))