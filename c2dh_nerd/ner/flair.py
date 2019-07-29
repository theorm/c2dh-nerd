from typing import List, Tuple
from flair.data import Sentence
from flair.models import SequenceTagger

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity
from .mapping import ONTONOTES_TO_WIKIPEDIA_LABEL_MAPPING

flatten = lambda l: [item for sublist in l for item in sublist]

def as_ner_result_entity(span, offset: int, index: int, return_sentences = False) -> NerResultEntity:
  # print('S', span, dir(span), span.__dict__)
  # {'tokens': [Token: 5 Robert, Token: 6 Goebbels,], 'tag': 'PER', 'score': 0.8921127617359161, 'start_pos': 17, 'end_pos': 33}
  left = span.start_pos if return_sentences else span.start_pos + offset
  right = span.end_pos if return_sentences else span.end_pos + offset
  sentence_index = index if return_sentences else None
  tag = ONTONOTES_TO_WIKIPEDIA_LABEL_MAPPING.get(span.tag, 'UNK') 

  return NerResultEntity(
    entity = span.text,
    tag = tag,
    left = left,
    right = right,
    score = span.score,
    sentence_index = sentence_index
  )

class FlairNer(NER):
  def __init__(self, model_name='ner-fast'):
    self._tagger = SequenceTagger.load(model_name)

  async def extract(self, text: TextOrSentences, return_sentences = False) -> NerResult:
    sentences_and_offsets = text_to_sentences(text)
    entities = self._extract_sentences(sentences_and_offsets, return_sentences)

    if return_sentences:
      result_text = [s for s, _ in sentences_and_offsets]
    else:
      result_text = sentences_to_text(text)

    return NerResult(result_text, entities)

  def _extract_sentences(self, sentence_and_offset_list: List[Tuple[str, int]], return_sentences = False):
    flair_sentences = [Sentence(sentence) for sentence, _ in sentence_and_offset_list]
    self._tagger.predict(flair_sentences)

    return flatten([
      [as_ner_result_entity(s, offset, index, return_sentences) for s in flair_sentence.get_spans('ner')]
      for index, (flair_sentence, (_, offset)) in enumerate(zip(flair_sentences, sentence_and_offset_list))
    ])
