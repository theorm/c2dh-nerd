import os
from typing import Callable
from diskcache import Cache

from .ner.flair import FlairNer
from .ner.spacy import SpacyNer
from .ner.allennlp import AllenNlpNer
from .ned.opentapioca import OpenTapiocaNed
from .ned.gkg import GoogleKnowledgeGraphNed
from .ned.fusion import FusionNed
from .entities.store import EntitiesSetsStore
from .ned.custom import CustomEntitiesSourceNed

def lazy_factory(tag: str, app, constructor: Callable[[], object]):
  def factory():
    instance_tag = '{}__instance'.format(tag)
    if instance_tag not in app:
      app[instance_tag] = constructor()
    return app[instance_tag]
  return factory

def get_cache():
  cache_location = os.path.realpath(os.environ.get('CACHE_DIR', os.path.join(os.getcwd(), 'cache')))
  print('Using "{}" as cache location'.format(cache_location))
  assert os.path.isdir(cache_location), 'Cache directory does not exist'
  return Cache(cache_location)

def add_context(app):
  # cache
  app['cache'] = get_cache()

  # Entities store
  app['entities_store'] = EntitiesSetsStore()

  # NED/NER
  app['ner_flair'] = lazy_factory('ner_flair', app, FlairNer)

  app['ner_spacy_small_en'] = lazy_factory('ner_spacy_small_en', app, lambda: SpacyNer('small_en'))
  app['ner_spacy_small_multi'] = lazy_factory('ner_spacy_small_multi', app, lambda: SpacyNer('small_multi'))
  # app['ner_spacy_large_en'] = lazy_factory('ner_spacy_large_en', app, lambda: SpacyNer('large_en'))

  app['ner_allennlp_finegrained'] = lazy_factory('ner_allennlp_finegrained', app, lambda: AllenNlpNer('fine-grained-ner'))

  app['ned_opentapioca'] = lazy_factory('ned_opentapioca', app, OpenTapiocaNed)
  app['ned_gkg'] = lazy_factory('ned_gkg', app, lambda: GoogleKnowledgeGraphNed(cache=app['cache']))
  app['ned_custom_entities'] = lazy_factory('ned_custom_entities', app, lambda: CustomEntitiesSourceNed(app['entities_store']))

  # app['ned_fusion-spacy_large_en-gkg'] = lazy_factory('ned_gkg', app, lambda: FusionNed([app['ner_spacy_large_en']()], [app['ned_gkg']()]))
  app['ned_fusion-flair-gkg'] = lazy_factory('ned_gkg', app, lambda: FusionNed([app['ner_flair']()], [app['ned_gkg']()]))
  app['ned_fusion-flair-custom_entities'] = lazy_factory('ned_fusion-flair-custom_entities', app, lambda: FusionNed([app['ner_flair']()], [app['ned_custom_entities']()]))
  app['ned_fusion-flair-custom_entities-gkg'] = lazy_factory('ned_fusion-flair-custom_entities', app, lambda: FusionNed([app['ner_flair']()], [app['ned_custom_entities'](), app['ned_gkg']()]))


  return app


def get_data():
  if str(os.environ.get('DOWNLOAD_MODELS', '')) == '1':
    from spacy.cli import download
    download('en_core_web_sm')
    download('xx_ent_wiki_sm')
    # download('en_core_web_lg')
