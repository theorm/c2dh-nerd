from whoosh import scoring
from whoosh.filedb.filestore import RamStorage
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser, FuzzyTermPlugin

from ..ned.result import NedResource, NedResultEntity, NedResult, ENTITY_TYPES

NAME_HEADER = 'name'
ALT_NAMES_HEADER = 'alternative_names'
TYPE_HEADER = 'type'

NED_RESOURCE_FIELDS = [
  'description',
  'image_url',
  'wikidata_id',
  'dbpedia_uri',
  'google_kg_id',
  'wikipedia_uri',
  'viaf_uri',
]

FIELD_MAPPERS = {
  'viaf_url': lambda v: ('viaf_uri', v.replace('https://viaf.org/viaf/', '').strip()),
  'alternative_names': lambda v: ('alternative_names', [i.strip() for i in v.split(';') if i.strip() != '']),
}

class EntitiesSet:
  def __init__(self, url, headers, rows):
    self.url = url
    self.headers = headers
    self.rows = rows

    self.schema = Schema(
      name=TEXT(stored=False),
      alternative_names=TEXT(stored=False),
      id=ID(stored=True)
    )
    self.index = RamStorage().create_index(self.schema)

    for c in [NAME_HEADER, ALT_NAMES_HEADER, TYPE_HEADER]:
      assert c in self.headers, 'Required "{}" column not found in {}'.format(c, url)

    name_idx = self.headers.index(NAME_HEADER)
    alt_names_idx = self.headers.index(ALT_NAMES_HEADER)

    writer = self.index.writer()
    for idx, row in enumerate(self.rows):
      name = row[name_idx]
      alt_names = row[alt_names_idx]
      writer.add_document(
        name=str(name),
        alternative_names=str(alt_names),
        id=str(idx)
      )
    writer.commit()

    parser = QueryParser("name", self.index.schema)
    parser.add_plugin(FuzzyTermPlugin())
    self.name_query_parser = parser

    parser = QueryParser("alternative_names", self.index.schema)
    parser.add_plugin(FuzzyTermPlugin())
    self.alt_names_query_parser = parser

  async def search(self, query_str, n_items):
    with self.index.searcher(weighting=scoring.Frequency) as searcher:
      name_query = self.name_query_parser.parse(query_str)
      alt_names_query = self.alt_names_query_parser.parse(query_str)

      query = name_query | alt_names_query
      
      results = searcher.search(query, limit=n_items)
      resources = [self.to_ned_result_item(i) for i in results]

      entity = NedResultEntity(
        entity = query_str,
        score = 1.0,
        left = 0,
        right = len(query_str),
        resources = resources,
        matched_resource = resources[0] if len(resources) > 0 else None
      )

      return NedResult(
        text = query_str,
        entities = [entity]
      )

  def to_ned_result_item(self, result):
    id = int(result['id'])
    row = self.rows[id]

    type_idx = self.headers.index(TYPE_HEADER)
    name_idx = self.headers.index(NAME_HEADER)

    resource_kwargs = {
      'score': result.score,
      'model': 'external:{}'.format(self.url),
      'id': result['id'],
      'tag': row[type_idx] if row[type_idx] in ENTITY_TYPES else 'UNK',
      'label': row[name_idx]
    }

    metadata = {}

    for header in self.headers:
      value = row[self.headers.index(header)].strip()
      if header in [NAME_HEADER, TYPE_HEADER]:
        continue
      if header in FIELD_MAPPERS:
        mapper = FIELD_MAPPERS[header]
        header, value = mapper(value)

      if len(value) == 0:
        continue
      
      if header in NED_RESOURCE_FIELDS:
        resource_kwargs[header] = value
      else:
        metadata[header] = value

    resource_kwargs['metadata'] = metadata

    return NedResource(**resource_kwargs)
