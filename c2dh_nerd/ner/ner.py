from typing import TypeVar, List, Tuple
from segtok.segmenter import split_single

from .result import NerResult

TextOrSentences = ('TextOrSentences', str, List[str])

def text_to_sentences(text: TextOrSentences) -> List[Tuple[str, int]]:
  if isinstance(text, str):

    last_sentence_offset = { 'v': 0, 'text': str(text) }
    def get_sentence_and_offset(sent):
      span_start = last_sentence_offset['text'].find(sent)
      span_end = span_start + len(sent) + 1

      offset = last_sentence_offset['v'] + span_start
      x = (sent, offset)
      last_sentence_offset['text'] = last_sentence_offset['text'][span_end:]
      last_sentence_offset['v'] += span_end
      return x

    return [get_sentence_and_offset(sent) for sent in split_single(text) if len(sent.strip()) > 0]
  else:
    last_offset = { 'v': 0 }

    def get_sentence_and_offset(sent):
      x = (last_offset['v'], sent)
      last_offset['v'] += len(sent)
      return x

    return [(sentence, 0) for sentence in text]

def sentences_to_text(text: TextOrSentences) -> str:
  if isinstance(text, str):
    return text
  return ''.join(text)

class NER:
  async def extract(self, text: TextOrSentences) -> NerResult:
    raise NotImplementedError()

