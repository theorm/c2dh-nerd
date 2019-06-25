from typing import TypeVar, List, Tuple
from segtok.segmenter import split_single

from .result import NerResult

TextOrSentences = ('TextOrSentences', str, List[str])

def text_to_sentences(text: TextOrSentences) -> List[Tuple[str, int]]:
  if isinstance(text, str):

    last_sentence_offset = { 'v': 0 }
    def get_sentence_and_offset(sent):
      x = (sent, last_sentence_offset['v'])
      last_sentence_offset['v'] += len(sent)
      return x

    return [get_sentence_and_offset(sent) for sent in split_single(text) if len(sent.strip()) > 0]
  return text

def sentences_to_text(text: TextOrSentences) -> str:
  if isinstance(text, str):
    return text
  return ''.join(text)

class NER:
  async def extract(self, text: TextOrSentences) -> NerResult:
    raise NotImplementedError()

