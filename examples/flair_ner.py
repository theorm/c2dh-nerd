import asyncio
import re
from c2dh_nerd.ner.flair import FlairNer
from c2dh_nerd.util.routes import json_dumps
from spacy.lang.en import English

TEXT = '''
Le président de la République a convié le nouveau premier ministre britannique à une visite en France, indique une source à l'Élysée.

Emmanuel Macron et Boris Johnson, élu mardi 23 juillet à la tête du Parti conservateur et successeur désigné de Theresa May à la tête du gouvernement britannique, s'entretiendront du Brexit dans les prochaines semaines, «dans le respect des exigences de l'Union européenne», a indiqué une source à l'Élysée.
'''

sentence_splitter = English()
sentence_splitter.add_pipe(sentence_splitter.create_pipe("sentencizer", {"punct_chars": [".", "!", "?", ";"]}))

def text_to_sentences(text):
  if (len(text.strip()) == 0):
    return []

  doc = sentence_splitter(text)
  return [s.text for s in doc.sents]



sentences = text_to_sentences(TEXT)

ner_en = FlairNer(model_name='ner')
ner_fr = FlairNer(model_name='fr-ner')
ner_mul = FlairNer(model_name='ner-multi')

def normalise_entity(e):
  return re.sub(r'^[^0-9a-zA-Z]*(.+?)[^0-9a-zA-Z]*$', r'\1', str(e))

async def main():
  for s in sentences:
    print(s)

  for ner, label in [(ner_en, 'en'), (ner_fr, 'fr'), (ner_mul, 'multilang')]:
    print(f'NER {label}:')
  
    result = await ner.extract(sentences)

    for e in result.entities:
      print(f"{e.tag}: {normalise_entity(e.entity)} = {e.score}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()

