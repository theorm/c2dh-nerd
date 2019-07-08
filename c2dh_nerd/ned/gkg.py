import os
import json
import hashlib
import aiohttp
import urllib.parse
from .ned import NED, TextOrSentences, sentences_to_text
from .result import NedResult, NedResultEntity, NedResource

DEFAULT_EXPIRATION_SEC = 30 * 24 * 60 * 60 # 30 days

def get_cache_key(text):
  text_hash = hashlib.blake2b(bytes(text, 'utf-8')).hexdigest()
  return 'gke:{}'.format(text_hash)

def get_id_cache_key(id):
  return 'gkg:{}'.format(id)

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
    model = 'gkg',
    id = result['@id'],
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
  def __init__(self, cache = None):
    self._endpoint = 'https://content-kgsearch.googleapis.com/v1/entities:search?prefix=true&query={}&key={}'
    self._id_endpoint = 'https://content-kgsearch.googleapis.com/v1/entities:search?prefix=true&ids={}&key={}'
    self._api_key = os.environ['GKG_API_KEY']
    self._cache = cache

  async def extract(self, text: TextOrSentences, **kwargs) -> NedResult:
    full_text = sentences_to_text(text)
    attempt = kwargs.get('attempt', 0)

    cache_key = get_cache_key(full_text)
    if self._cache and cache_key in self._cache:
      # print('GKE Cache hit for "{}": {}'.format(full_text, cache_key))
      response = json.loads(self._cache[cache_key])
    else:
      response, status = await self.get_gkg_response(full_text)
      if status < 400:
        self._cache.set(cache_key, json.dumps(response), expire = DEFAULT_EXPIRATION_SEC)

      if status >= 500:
        if attempt < MAX_ATTEMPTS:
          # try again
          return await self.extract(text, attempt = attempt + 1)
        else:
          raise Exception('Had {} attempts getting data. Failing for good. Last error ({}) {}'.format(attempt, status, json.dumps(response)))
      elif status >= 400:
        raise Exception('Received an error from GKE ({}): {}'.format(status, json.dumps(response)))

    if 'itemListElement' not in response:
      print('ERR: No "itemListElement" in response ({})'.format(full_text), response)

    items = response['itemListElement']

    return NedResult(full_text, [as_ned_result_entity(items, full_text)])


  async def get_gkg_response(self, text):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
      url = self._endpoint.format(urllib.parse.quote(text), self._api_key)

      async with session.get(url) as resp:
        body = await resp.json()
        return body, resp.status

  async def get_gkg_response_for_id(self, id):
    id_val = id[3:] if id.startswith('kg:') else id
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
      url = self._id_endpoint.format(urllib.parse.quote(id_val), self._api_key)

      async with session.get(url) as resp:
        body = await resp.json()
        return body, resp.status

  async def expand_resource(self, model_name, resource_id, label = None, **kwargs) -> NedResource:
    '''
    TODO: Extract wiki page metadata if page is present.
    '''
    attempt = kwargs.get('attempt', 0)

    cache_key = get_id_cache_key(resource_id)
    if self._cache and cache_key in self._cache:
      # print('GKE Cache hit for "{}": {}'.format(full_text, cache_key))
      response = json.loads(self._cache[cache_key])
    else:
      response, status = await self.get_gkg_response_for_id(resource_id)
      if status < 400:
        self._cache.set(cache_key, json.dumps(response), expire = DEFAULT_EXPIRATION_SEC)

      if status >= 500:
        if attempt < MAX_ATTEMPTS:
          # try again
          return await self.expand_resource(model_name, resource_id, label, attempt = attempt + 1)
        else:
          raise Exception('Had {} attempts getting data. Failing for good. Last error ({}) {}'.format(attempt, status, json.dumps(response)))
      elif status >= 400:
        raise Exception('Received an error from GKE ({}): {}'.format(status, json.dumps(response)))

    if 'itemListElement' not in response:
      print('ERR: No "itemListElement" in response ({})'.format(id), response)

    items = response['itemListElement']

    return as_ned_resource(items[0]) if len(items) > 0 else None
