from typing import Callable
from .ner.flair import FlairNer
from .ned.opentapioca import OpenTapiocaNed

def lazy_factory(tag: str, app, constructor: Callable[[], object]):
  def factory():
    instance_tag = '{}__instance'.format(tag)
    if instance_tag not in app:
      app[instance_tag] = constructor()
    return app[instance_tag]
  return factory

def add_context(app):
  app['ner_flair'] = lazy_factory('ner_flair', app, FlairNer)
  app['ned_opentapioca'] = lazy_factory('ned_opentapioca', app, OpenTapiocaNed)
  return app
