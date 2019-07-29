from typing import List

# Based on wikipedia types
ENTITY_TYPES = [
  'PER',
  'LOC',
  'ORG',
  'UNK'
]

TextOrSentences = ('TextOrSentences', str, List[str])

class NerResultEntity:
  def __init__(self, entity: str, tag: str, left: int, right: int, score: float, sentence_index: int = None):
    self.entity = entity
    self.tag = tag
    self.left = left
    self.right = right
    self.score = score
    self.sentence_index = sentence_index

    assert left < right, 'Left ({}) must be less than right ({})'.format(left, right)


class NerResult:
  def __init__(self, text: TextOrSentences, entities: List[NerResultEntity]):
    self.text = text
    self.entities = entities
