import os
import aiohttp
import urllib.parse
from .ned import NED, TextOrSentences, sentences_to_text
from .result import NedResult, NedResultEntity, NedResource

def get_tag_from_types(types):
  if 'Person' in types:
    return 'PER'
  if 'Organization' in types:
    return 'ORG'
  if 'Place' in types:
    return 'LOC'
  # shall we handle "Event" ?
  # return None
  return 'ORG' # not sure if this is the best fallback...

def as_ned_resource(item):
  result = item['result']
  types = result['@type']
  tag = get_tag_from_types(types)

  return NedResource(
    score = item.get('resultScore'),
    tag = tag,
    label = result.get('name'),
    description = result.get('description', ''),
    google_kg_id = result['@id'],
    wikipedia_uri = result.get('detailedDescription', {}).get('url', None)
  )

def as_ned_result_entity(items, text):
  start, end = 0, len(text)
  resources = [as_ned_resource(i) for i in items]

  return NedResultEntity(
    entity = text[start:end],
    score = 1.0,
    left = start,
    right = end,
    resources = resources,
    matched_resource = resources[0] if len(resources) > 0 else None
  )

MAX_ATTEMPTS = 5

class GoogleKnowledgeGraphNed(NED):
  def __init__(self):
    self._endpoint = 'https://content-kgsearch.googleapis.com/v1/entities:search?prefix=true&query={}&key={}'
    self._api_key = os.environ['GKG_API_KEY']

  async def extract(self, text: TextOrSentences, attempt = 0) -> NedResult:
    full_text = sentences_to_text(text)
    response = await self.get_gkg_response(full_text)

    if response.get('error', {}).get('code', None) == 503:
      if attempt < MAX_ATTEMPTS:
        # try again
        return await self.extract(text, attempt = attempt + 1)
      else:
        raise Exception('Had {} attempts getting data. Failing for good. Last error {}'.format(attempt, response.get('error', {}).get('message', None)))
    
    if 'itemListElement' not in response:
      print('ERR: No "itemListElement" in response ({})'.format(full_text), response)

    items = response['itemListElement']

    return NedResult(full_text, [as_ned_result_entity(items, full_text)])


  async def get_gkg_response(self, text):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
      url = self._endpoint.format(urllib.parse.quote(text), self._api_key)

      async with session.get(url) as resp:
        return await resp.json()
