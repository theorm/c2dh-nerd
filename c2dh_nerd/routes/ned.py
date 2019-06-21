from aiohttp import web
import json

from ..ned import NED

METHODS = [
  'opentapioca'
]

async def handler(request):
  body = await request.json()
  method = body.get('method')
  text = body.get('text')

  assert method in METHODS, 'Unknown method "{}". Supported methods are: {}'.format(method, ', '.join(METHODS))
  assert text, '"text" must be provided'

  ned: NED = request.app['ned_{}'.format(method)]()

  result = await ned.extract(text)

  return web.json_response(
    result,
    dumps = lambda x: json.dumps(x, default=lambda o: o.__dict__)
  )
