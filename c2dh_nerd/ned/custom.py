import re
import aiohttp
from .ned import NED, TextOrSentences, sentences_to_text
from .result import NedResult, NedResource

EXTERNAL_REGEX = re.compile('^external:(.*)$')

class CustomEntitiesSourceNed(NED):
  def __init__(self, custom_entities_store):
    self.custom_entities_store = custom_entities_store

  async def extract(self, text: TextOrSentences, **kwargs) -> NedResult:
    full_text = sentences_to_text(text)
    url = kwargs.get('url')

    custom_entities_set = await self.custom_entities_store.get(url)
    return await custom_entities_set.search(full_text, 10)

  async def expand_resource(self, model_name, resource_id, label = None) -> NedResource:
    url = re.sub(EXTERNAL_REGEX, r'\1', model_name)

    custom_entities_set = await self.custom_entities_store.get(url)
    resource = custom_entities_set.get_by_id(resource_id)

    if resource is None:
      resource = custom_entities_set.get_by_label(label)

    return resource
