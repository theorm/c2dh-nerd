from aiohttp import web
from ..util.routes import json_dumps

async def load_handler(request):
  body = await request.json()
  url = body.get('url')

  entities_store = request.app['entities_store']
  entities_set = await entities_store.get(url)

  return web.json_response(
    { 'headers': entities_set.headers }
  )

async def search_handler(request):
  body = await request.json()
  url = body.get('url')
  query = body.get('query')

  entities_store = request.app['entities_store']
  entities_set = await entities_store.get(url)

  results = await entities_set.search(query, 10)

  return web.json_response(
    { 'results': results },
    dumps = json_dumps
  )
