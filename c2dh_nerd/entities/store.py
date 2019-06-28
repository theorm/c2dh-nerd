import aiohttp
import csv
from .set import EntitiesSet

async def get_content(url):
  async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(verify_ssl=False)) as session:
    async with session.get(url) as resp:
      if resp.status != 200:
        raise Exception('An error returned while trying to download file from {}: {}'.format(url, resp.status))
      return await resp.text()


class EntitiesSetsStore:
  def __init__(self):
    self.store = {}

  async def get(self, url):
    if url not in self.store:
      text = await get_content(url)

      csv_reader = csv.reader(text.split('\n'))
      rows = [r for r in csv_reader]
      headers = rows[0]
      rows = rows[1:]

      entities_set = EntitiesSet(url, headers, rows)
      self.store[url] = entities_set
    return self.store[url]
