import aiohttp
from .ned import NED, TextOrSentences, sentences_to_text
from .result import NedResult, NedResultEntity, NedResource


# On tagging entities
# https://github.com/wetneb/opentapioca/blob/62c832152e79e064ca10500bb3cfddfada7c7f83/docs/indexing.rst#indexing-for-tagging
# {"type": "Q43229", "property": "P31"}, - organization
# {"type": "Q618123", "property": "P31"}, - geographical object
# {"type": "Q5", "property": "P31"} - human

# "P2427", "P1566", "P496", # Include all items bearing any of these properties
# P2427 - institutional identifier from the GRID.ac global research identifier database
# P1566 - GeoNames ID
# P496 - ORCID iD - identifier for a person

WIKIDATA_QUALIFIER_TO_ENTITY_TYPE = {
  'Q5': 'PER',
  'Q618123': 'LOC',
  'Q43229': 'ORG',
}

# NOTE: countries have Q43229=true (org) but Q618123=false (loc)
# We may need to dig deeper into qualifiers of the entities to
# get more information. Or add a country wikidata id -> country
# lookup.

def as_ned_resource(t):
  tag = 'UNK'
  for qualifier, entity_type in WIKIDATA_QUALIFIER_TO_ENTITY_TYPE.items():
    if t.get('types', {}).get(qualifier, None):
      tag = entity_type
      break

  return NedResource(
    score = t['rank'],
    tag = tag,
    label = t['label'][0],
    description = t['desc'],
    wikidata_id = t['id'],
  )

def as_ned_result_entity(annotation, text):
  start, end = annotation['start'], annotation['end']
  resources = [as_ned_resource(t) for t in annotation['tags']]

  return NedResultEntity(
    entity = text[start:end],
    score = annotation['log_likelihood'],
    left = start,
    right = end,
    resources = resources,
    matched_resource = resources[0]
  )

class OpenTapiocaNed(NED):
  def __init__(self):
    self._endpoint = 'https://opentapioca.org/api/annotate'

  async def extract(self, text: TextOrSentences) -> NedResult:
    full_text = sentences_to_text(text)
    opentapioca_response = await self.get_opentapioca_response(full_text)

    annotations = opentapioca_response['annotations']

    return NedResult(full_text, [as_ned_result_entity(a, full_text) for a in annotations])


  async def get_opentapioca_response(self, text):
    req = {
      'query': text
    }

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
      async with session.post(self._endpoint, data=req) as resp:
        return await resp.json()
