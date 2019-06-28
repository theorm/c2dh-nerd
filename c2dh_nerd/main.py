import os
import traceback
from aiohttp import web
from . import routes
from .context import add_context

@web.middleware
async def error_handler_middleware(request, handler):
    try:
        return await handler(request)
    except AssertionError as err:
        return web.json_response({
            'message': str(err)
        }, status=400)
    except Exception as err:
        return web.json_response({
            'message': '{}: {}'.format(err.__class__.__name__, str(err)),
            'stack': traceback.format_exc()
        }, status=500)

PORT = os.environ.get('PORT', 8002)

def main():
    app = web.Application(middlewares=[error_handler_middleware])
    app = add_context(app)
    app.add_routes([
        web.get('/status', routes.status.handler),
        web.post('/ner', routes.ner.handler),
        web.post('/ned', routes.ned.handler),
        web.post('/entities/load', routes.entities.load_handler),
        web.post('/entities/search', routes.entities.search_handler)
    ])
    web.run_app(app, port = PORT)
