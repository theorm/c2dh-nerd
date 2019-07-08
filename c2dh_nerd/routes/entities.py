import re
from aiohttp import web
from ..util.routes import json_dumps

MODEL_NAMES = {
  '^opentapioca$': 'ned_opentapioca',
  '^gkg$': 'ned_gkg',
  '^external:.*$': 'ned_custom_entities',
}

MODEL_NAMES = {re.compile(k):v for k, v in MODEL_NAMES.items()}

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

async def expand_handler(request):
  body = await request.json()
  model_name = body.get('model')
  resource_id = body.get('id')
  label = body.get('label')

  ned_models = [v for p, v in MODEL_NAMES.items() if p.match(model_name)]
  ned_model_name = ned_models[0] if len(ned_models) > 0 else None
  assert ned_model_name is not None, 'Unknown model name: {}'.format(model_name)

  ned_model = request.app[ned_model_name]()
  
  assert resource_id is not None, '"ID" must be provided'

  entity = await ned_model.expand_resource(model_name, resource_id, label)

  return web.json_response(
    { 'entity': entity },
    dumps = json_dumps
  )
