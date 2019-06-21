import itertools
from flair.data import Sentence
from flair.models import SequenceTagger

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity

def as_ner_result_entity(span, offset: int) -> NerResultEntity:
  # print('S', span, dir(span), span.__dict__)
  # {'tokens': [Token: 5 Robert, Token: 6 Goebbels,], 'tag': 'PER', 'score': 0.8921127617359161, 'start_pos': 17, 'end_pos': 33}
  return NerResultEntity(
    entity = span.text,
    tag = span.tag,
    left = offset + span.start_pos,
    right = offset + span.end_pos,
    score = span.score
  )

class FlairNer(NER):
  def __init__(self):
    self._tagger = SequenceTagger.load('ner')

  def extract(self, text: TextOrSentences) -> NerResult:
    sentences_and_offsets = text_to_sentences(text)
    entities = [self._extract_sentence(sentence, offset) for sentence, offset in sentences_and_offsets]
    flattened_entities = list(itertools.chain.from_iterable(entities))
    return NerResult(sentences_to_text(text), flattened_entities)

  def _extract_sentence(self, sentence: str, offset: int):
    flair_sentence = Sentence(sentence)
    self._tagger.predict(flair_sentence)
  
    return [as_ner_result_entity(s, offset) for s in flair_sentence.get_spans('ner')]

