from aiohttp import web
import json
from timeit import default_timer as timer

from ..ned import NED
from ..util.routes import json_dumps

METHODS = [
  'opentapioca',
  'gkg',
  # 'fusion-spacy_large_en-gkg',
  'fusion-flair-gkg',
  'custom_entities',
  'fusion-flair-custom_entities',
  'fusion-flair-custom_entities-gkg'
]

async def handler(request):
  body = await request.json()
  method = body.get('method')
  text = body.get('text')

  extras = body.copy()
  extras.pop('method', None)
  extras.pop('text', None)

  assert method in METHODS, 'Unknown method "{}". Supported methods are: {}'.format(method, ', '.join(METHODS))
  assert text, '"text" must be provided'

  ned: NED = request.app['ned_{}'.format(method)]()

  start = timer()
  result = await ned.extract(text, **extras)
  end = timer()

  time_elapsed = end - start
  result.time_elapsed_seconds = time_elapsed

  return web.json_response(
    result,
    dumps = json_dumps
  )
