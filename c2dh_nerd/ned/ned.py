from typing import TypeVar, List, Tuple
from segtok.segmenter import split_single

from ..ner.ner import text_to_sentences, sentences_to_text, TextOrSentences
from .result import NedResult, NedResource

class NED:
  async def extract(self, text: TextOrSentences, **kwargs) -> NedResult:
    raise NotImplementedError()

  async def expand_resource(self, model_name, resource_id, label = None) -> NedResource:
    raise NotImplementedError()
