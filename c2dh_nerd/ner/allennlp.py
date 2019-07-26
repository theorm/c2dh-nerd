from typing import List, Tuple, Any
from allennlp.predictors.predictor import Predictor
from allennlp.models.archival import load_archive
import torch

from .ner import NER, TextOrSentences, text_to_sentences, sentences_to_text
from .result import NerResult, NerResultEntity

MODELS_MAPPING = {
  'fine-grained-ner': 'https://s3-us-west-2.amazonaws.com/allennlp/models/fine-grained-ner-model-elmo-2018.12.21.tar.gz',
  'elmo-ner': 'https://s3-us-west-2.amazonaws.com/allennlp/models/ner-model-2018.12.18.tar.gz',
}

NER_LABEL_MAPPING = {
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

flatten = lambda l: [item for sublist in l for item in sublist]

def item_group_to_ner_result_entity(sentence: str, tag: str, word_token_paris: List[Tuple[str, Any]], offset) -> NerResultEntity:
  pos_start = word_token_paris[0][1].idx
  pos_end = word_token_paris[-1][1].idx + len(word_token_paris[-1][1].text)
  entity = sentence[pos_start:pos_end]

  return NerResultEntity(
    entity = entity,
    tag = NER_LABEL_MAPPING.get(tag, None),
    left = pos_start + offset,
    right = pos_end + offset,
    score = 1.0
  )

def group_with_bioul(word_tag_token_items: List[Tuple[str, str, Any]]) -> List[Tuple[str, List[Tuple[str, Any]]]]:
  groups = []
  current_group = []
  for (word, tag, token) in word_tag_token_items:
    if tag == 'O':
      if current_group != []:
        raise Exception('Unexpected "O" tag "{}" in group: {}'.format(word, ', '.join([x[0] for x in current_group])))
      current_group = []
      groups.append(
        (tag, [(word, token)])
      )
    elif tag.startswith('U-'):
      if current_group != []:
        raise Exception('Unexpected "U-" tag "{}" in group: {}'.format(word, ', '.join([x[0] for x in current_group])))
      current_group = []
      groups.append(
        (tag.replace('U-', ''), [(word, token)])
      )
    elif tag.startswith('B-'):
      current_group = [(word, tag.replace('B-', ''), token)]
    elif tag.startswith('I-'):
      current_group.append((word, tag.replace('I-', ''), token))
    elif tag.startswith('L-'):
      current_group.append((word, tag.replace('L-', ''), token))

      tags = list(set([i[1] for i in current_group]))
      if len(tags) != 1:
        raise Exception('More than one type of tag ({}) found in group: {}', tags, ', '.join([x[0] for x in current_group]))
      tag = tags[0]

      group = (tag, [(word, token) for word, _, token in current_group])

      groups.append(group)
      current_group = []
    else:
      raise Exception('Unknown tag for word "{}": {}'.format(word, tag))

  if current_group != []:
    raise Exception('Unfinished group at the end of sentence: {}'.format(', '.join([x[0] for x in current_group])))

  return groups

class AllenNlpNer(NER):
  def __init__(self, model_name: str = 'fine-grained-ner'):
    assert model_name in MODELS_MAPPING, \
      'Unknown model name: "{}". Available models: {}'.format(model_name, ', '.join(MODELS_MAPPING.keys()))
    model_url = MODELS_MAPPING[model_name]
    try:
      cuda_device = torch.cuda.current_device()
    except:
      cuda_device = -1
    self._predictor = Predictor.from_archive(load_archive(model_url, cuda_device=cuda_device))

  async def extract(self, text: TextOrSentences) -> NerResult:
    full_text = sentences_to_text(text)
    sentences = text_to_sentences(text)
    entities = self._extract(sentences)
    return NerResult(full_text, entities)

  def _extract(self, sentences: List[Tuple[str, int]]):
    entities = flatten([
      self._extract_sentence(sentence, offset)
      for (sentence, offset) in sentences
    ])

    return [e for e in entities if e.tag is not None]

  def _extract_sentence(self, sentence: str, offset: int):
    prediction = self._predictor.predict(sentence=sentence)
    tokens = self._predictor._tokenizer.split_words(sentence)
    items = zip(prediction['words'], prediction['tags'], tokens)
    items_groups = group_with_bioul(items)

    return [
      item_group_to_ner_result_entity(sentence, tag, word_token_pairs, offset)
      for tag, word_token_pairs in items_groups
    ]

