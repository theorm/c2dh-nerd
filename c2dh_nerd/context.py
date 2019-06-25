from typing import Callable
from .ner.flair import FlairNer
from .ner.spacy import SpacyNer
from .ned.opentapioca import OpenTapiocaNed
from .ned.gkg import GoogleKnowledgeGraphNed
from .ned.fusion import FusionNed

def lazy_factory(tag: str, app, constructor: Callable[[], object]):
  def factory():
    instance_tag = '{}__instance'.format(tag)
    if instance_tag not in app:
      app[instance_tag] = constructor()
    return app[instance_tag]
  return factory

def add_context(app):
  app['ner_flair'] = lazy_factory('ner_flair', app, FlairNer)

  app['ner_spacy_small_en'] = lazy_factory('ner_spacy_small_en', app, lambda: SpacyNer('small_en'))
  app['ner_spacy_small_multi'] = lazy_factory('ner_spacy_small_multi', app, lambda: SpacyNer('small_multi'))
  app['ner_spacy_large_en'] = lazy_factory('ner_spacy_large_en', app, lambda: SpacyNer('large_en'))

  app['ned_opentapioca'] = lazy_factory('ned_opentapioca', app, OpenTapiocaNed)
  app['ned_gkg'] = lazy_factory('ned_gkg', app, GoogleKnowledgeGraphNed)

  app['ned_fusion-spacy_large_en-gkg'] = lazy_factory('ned_gkg', app, lambda: FusionNed([app['ner_spacy_large_en']()], [app['ned_gkg']()]))

  return app
