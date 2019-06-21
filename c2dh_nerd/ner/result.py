from typing import List

# Based on wikipedia types
ENTITY_TYPES = [
  'PER',
  'LOC',
  'ORG',
  'UNK'
]

class NerResultEntity:
  def __init__(self, entity: str, tag: str, left: int, right: int, score: float):
    self.entity = entity
    self.tag = tag
    self.left = left
    self.right = right
    self.score = score

    assert left < right, 'Left ({}) must be less than right ({})'.format(left, right)


class NerResult:
  def __init__(self, text: str, entities: List[NerResultEntity]):
    self.text = text
    self.entities = entities
