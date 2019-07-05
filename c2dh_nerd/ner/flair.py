from typing import List, Tuple
from flair.data import Sentence
from flair.models import SequenceTagger

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity

flatten = lambda l: [item for sublist in l for item in sublist]

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
    self._tagger = SequenceTagger.load('ner-fast')

  async def extract(self, text: TextOrSentences) -> NerResult:
    sentences_and_offsets = text_to_sentences(text)
    entities = self._extract_sentences(sentences_and_offsets)
    return NerResult(sentences_to_text(text), entities)

  def _extract_sentences(self, sentence_and_offset_list: List[Tuple[str, int]]):
    flair_sentences = [Sentence(sentence) for sentence, _ in sentence_and_offset_list]
    self._tagger.predict(flair_sentences)

    return flatten([
      [as_ner_result_entity(s, offset) for s in flair_sentence.get_spans('ner')]
      for flair_sentence, (_, offset) in zip(flair_sentences, sentence_and_offset_list)
    ])
