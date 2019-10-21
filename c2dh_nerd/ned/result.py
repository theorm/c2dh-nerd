from typing import List

# Based on wikipedia types
ENTITY_TYPES = [
  'PER',
  'LOC',
  'ORG',
  'UNK'
]

class NedResource:
  '''
  Globally unique ID of the resource: [`model`, `id`].
  '''
  def __init__(self,
    score: float, # higher is better
    model: str, # model that was used to discover this resource.
    id: str, # ID of the resource within this model.
    tag: str,
    label: str, 
    description: str = None,
    image_url: str = None,
    wikidata_id: str = None,
    dbpedia_uri: str = None,
    google_kg_id: str = None,
    wikipedia_uri: str = None,
    viaf_uri: str = None,
    metadata: dict = {}
  ):
    self.score = score
    self.model = model
    self.id = id
    self.tag = tag
    self.label = label
    self.description = description
    self.image_url = image_url
    self.wikidata_id = wikidata_id
    self.dbpedia_uri = dbpedia_uri
    self.google_kg_id = google_kg_id
    self.wikipedia_uri = wikipedia_uri
    self.viaf_uri = viaf_uri
    self.metadata = metadata

    assert tag in ENTITY_TYPES, 'Unknown tag {}. Should be one of: {}'.format(tag, ', '.join(ENTITY_TYPES))

class NedResultEntity:
  def __init__(self, entity: str, score: float, left: int, right: int, resources: List[NedResource], matched_resource: NedResource = None):
    self.entity = entity
    self.score = score
    self.left = left
    self.right = right
    self.resources = resources
    self.matched_resource = matched_resource
    self.tag = matched_resource.tag if matched_resource is not None else None

    assert left < right, 'Left ({}) must be less than right ({})'.format(left, right)


class NedResult:
  def __init__(self, text: str, entities: List[NedResultEntity]):
    self.text = text
    self.entities = entities
