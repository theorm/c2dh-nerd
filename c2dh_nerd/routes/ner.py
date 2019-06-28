from aiohttp import web
import json
from timeit import default_timer as timer

from ..ner import NER
from ..util.routes import json_dumps

METHODS = [
  'flair',
  'spacy_small_en',
  'spacy_small_multi',
  'spacy_large_en'
]

async def handler(request):
  body = await request.json()
  method = body.get('method')
  text = body.get('text')

  assert method in METHODS, 'Unknown method "{}". Supported methods are: {}'.format(method, ', '.join(METHODS))
  assert text, '"text" must be provided'

  ner: NER = request.app['ner_{}'.format(method)]()

  start = timer()
  result = await ner.extract(text)
  end = timer()

  time_elapsed = end - start
  result.time_elapsed_seconds = time_elapsed

  return web.json_response(
    result,
    dumps = json_dumps
  )
