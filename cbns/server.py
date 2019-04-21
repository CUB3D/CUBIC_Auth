from starlette.routing import Mount, Route, Router
from starlette.websockets import WebSocket
from starlette.applications import Starlette

app = Starlette()

@app.websocket_route('/')
async def ws_(ws):
    await ws.accept()
    await ws.send_text('Hi')
    await ws.close()

#class CBNSApp:
#    def __init__(self, scope):
#        assert scope['type'] == 'websocket'
#        self.scope = scope

#    async def __call__(self, receive, send):
#        ws = WebSocket(self.scope, receive=receive, send=send)
#        await ws.accept()
#        t = await ws.receive_text()
#        await ws.send_text(t)

#app = Router([
#    Route('/', endpoint=CBNSApp, methods=['GET'])
#])


