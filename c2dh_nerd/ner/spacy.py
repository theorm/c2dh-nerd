import spacy

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity
from .mapping import ONTONOTES_TO_WIKIPEDIA_LABEL_MAPPING

MODELS_MAPPING = {
  'small_en': 'en_core_web_sm',
  'small_multi': 'xx_ent_wiki_sm',
  # 'large_en': 'en_core_web_lg'
}

def as_ner_result_entity(entity) -> NerResultEntity:
  return NerResultEntity(
    entity = entity.text,
    tag = ONTONOTES_TO_WIKIPEDIA_LABEL_MAPPING.get(entity.label_, 'UNK'),
    left = entity.start_char,
    right = entity.end_char,
    score = 1.0
  )

class SpacyNer(NER):
  def __init__(self, model_name: str = 'small_en'):
    assert model_name in MODELS_MAPPING, \
      'Unknown model name: "{}". Available models: {}'.format(model_name, ', '.join(MODELS_MAPPING.keys()))
    self._model = spacy.load(MODELS_MAPPING[model_name])

  async def extract(self, text: TextOrSentences) -> NerResult:
    full_text = sentences_to_text(text)
    entities = self._extract(full_text)
    return NerResult(full_text, entities)

  def _extract(self, text: str):
    doc = self._model(text)
    return [as_ner_result_entity(e) for e in doc.ents]

