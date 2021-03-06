import re
import asyncio
from .ned import NED, TextOrSentences, sentences_to_text
from .result import NedResult, NedResultEntity

ANY_TEXT_RE = re.compile(r'.*\w.*', re.M)

flatten = lambda l: [item for sublist in l for item in sublist]

def has_text(ner_entity):
  return ANY_TEXT_RE.match(ner_entity.entity) is not None

def merge_as_ned_result_entity(ner_entity, ned_entity):
  resources = ned_entity.resources if ned_entity is not None else []
  ned_entity_resources = [r for r in resources if r.tag == ner_entity.tag]

  # Now if nothing was found see if there is only one NED entity result regardless of the tag.
  # This may indicate the entity is rare and NER may have made a mistake classifyin it.
  if len(ned_entity_resources) == 0 and len(resources) == 1:
    ned_entity_resources = resources

  return NedResultEntity(
    entity = ner_entity.entity,
    score = ner_entity.score,
    left = ner_entity.left,
    right = ner_entity.right,
    resources = ned_entity_resources,
    matched_resource = ned_entity_resources[0] if len(ned_entity_resources) > 0 else None,
    tag = ner_entity.tag
  )

class FusionNed(NED):
  def __init__(self, ners, neds):
    assert len(ners) == 1, 'Only 1 NER is supported at the moment'
    assert len(neds) > 0, 'At least 1 NED is required'
    self._ner = ners[0]
    self._neds = neds

  async def extract(self, text: TextOrSentences, **kwargs) -> NedResult:
    ner_result = await self._ner.extract(text)
    entities = [e for e in ner_result.entities if has_text(e)]

    if len(entities) == 1:
      e = entities[0]
      full_text = sentences_to_text(text)
      entity_length_ratio = len(e.entity) / len(full_text)
      if entity_length_ratio > 0.5:
        print('A single very long entity detected ("{}") in {}'.format(e.entity, full_text))

    remaining_entities = entities[:]

    all_entity_and_ned_result_lists = []

    for ned_idx, ned in enumerate(self._neds):
      if len(remaining_entities) > 0:
        ned_results = await asyncio.gather(*[
          ned.extract(e.entity, **kwargs)
          for e in remaining_entities
        ])

        entity_and_ned_result_list = list(zip(remaining_entities, ned_results))

        remaining_entities = [
          entity
          for entity, result in entity_and_ned_result_list
          if len(result.entities) == 0 or result.entities[0].matched_resource is None
        ]

        if ned_idx < len(self._neds) - 1:
          entity_and_ned_result_list = [
            (entity, result)
            for entity, result in entity_and_ned_result_list
            if len(result.entities) > 0 and result.entities[0].matched_resource is not None
          ]

        all_entity_and_ned_result_lists.append(entity_and_ned_result_list)


    entity_and_ned_result_list = flatten(all_entity_and_ned_result_lists)
    # we do not accept results when a single entity from NER
    # was found to be multiple entities by NED. Such results
    # are filtered out.
    ned_result_entities = [
      merge_as_ned_result_entity(entity, ned_result.entities[0] if len(ned_result.entities) > 0 else None)
      for entity, ned_result in entity_and_ned_result_list
      if len(ned_result.entities) < 2 
    ]

    return NedResult(sentences_to_text(text), ned_result_entities)
