import spacy

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity

MODELS_MAPPING = {
  'small_en': 'en_core_web_sm',
  'small_multi': 'xx_ent_wiki_sm',
  # 'large_en': 'en_core_web_lg'
}

# Mapping to three standard wikidata classes: ORG, PER, LOC
# https://github.com/explosion/spaCy/blob/719a15f23d76f219fd303e94a8384c50c9fd61e2/spacy/glossary.py#L282-L309
SPACY_NER_LABEL_MAPPING = {
 "PERSON": "PER", # "People, including fictional",
  "NORP": "ORG", # "Nationalities or religious or political groups",
  "FACILITY": "LOC", # "Buildings, airports, highways, bridges, etc.",
  "FAC": "LOC", # "Buildings, airports, highways, bridges, etc.",
  "ORG": "ORG", # "Companies, agencies, institutions, etc.",
  "GPE": "LOC", # "Countries, cities, states",
  "LOC": "LOC", # "Non-GPE locations, mountain ranges, bodies of water",
  # "PRODUCT": "Objects, vehicles, foods, etc. (not services)",
  # "EVENT": "Named hurricanes, battles, wars, sports events, etc.",
  # "WORK_OF_ART": "Titles of books, songs, etc.",
  # "LAW": "Named documents made into laws.",
  # "LANGUAGE": "Any named language",
  # "DATE": "Absolute or relative dates or periods",
  # "TIME": "Times smaller than a day",
  # "PERCENT": 'Percentage, including "%"',
  # "MONEY": "Monetary values, including unit",
  # "QUANTITY": "Measurements, as of weight or distance",
  # "ORDINAL": '"first", "second", etc.',
  # "CARDINAL": "Numerals that do not fall under another type",
  # Named Entity Recognition
  # Wikipedia
  # http://www.sciencedirect.com/science/article/pii/S0004370212000276
  # https://pdfs.semanticscholar.org/5744/578cc243d92287f47448870bb426c66cc941.pdf
  "PER": "PER", # "Named person or family.",
  # "MISC": "Miscellaneous entities, e.g. events, nationalities, products or works of art",
}

def as_ner_result_entity(entity) -> NerResultEntity:
  return NerResultEntity(
    entity = entity.text,
    tag = SPACY_NER_LABEL_MAPPING[entity.label_],
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
    return [as_ner_result_entity(e) for e in doc.ents if e.label_ in SPACY_NER_LABEL_MAPPING]

