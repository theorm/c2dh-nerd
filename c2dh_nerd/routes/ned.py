from aiohttp import web
import json
from timeit import default_timer as timer

from ..ned import NED

METHODS = [
  'opentapioca',
  'gkg',
  'fusion-spacy_large_en-gkg',
  'fusion-flair-gkg'
]

async def handler(request):
  body = await request.json()
  method = body.get('method')
  text = body.get('text')

  assert method in METHODS, 'Unknown method "{}". Supported methods are: {}'.format(method, ', '.join(METHODS))
  assert text, '"text" must be provided'

  ned: NED = request.app['ned_{}'.format(method)]()

  start = timer()
  result = await ned.extract(text)
  end = timer()

  time_elapsed = end - start
  result.time_elapsed_seconds = time_elapsed

  return web.json_response(
    result,
    dumps = lambda x: json.dumps(x, default=lambda o: o.__dict__)
  )
