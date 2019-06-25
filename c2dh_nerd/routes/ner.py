from aiohttp import web
import json

from ..ner import NER

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

  result = await ner.extract(text)

  return web.json_response(
    result,
    dumps = lambda x: json.dumps(x, default=lambda o: o.__dict__)
  )
