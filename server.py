# IBM Confidential - OCO Source Materials
# Copyright (c) IBM Corp. 1992-2018
# Copyright (c) Internet Security Systems, Inc. 1992-2006
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.

import copy
import json
import logging
import os
import re

import requests
from tornado.options import define, options
import tornado
import tornado.web
import tornado.websocket

import aioredis


DIST_PATH = os.path.join(os.path.dirname(__file__), "dist")
STATIC_PATH = os.path.join(DIST_PATH, 'static')
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
DEV_MODE = False
TECHS_JSON_RE = re.compile(r"^/techs/(\w+).json$")
WS_JSON_RE = re.compile(r"^/websocket/(\w+)$")

pool = None


async def get_key_as_int(key):
  with await pool as redis:
    v = await redis.get(key)

  return int(v) if v else 0


async def set_key(key, value):
  with await pool as redis:
    logging.info("Updating Redis: Setting %s to %s" % (key, value))
    await redis.set(key, value)


# TODO Actually implement this
async def set_key_cas(key, old, new):
  _ = old
  await set_key(key, new)


class Game:
  cache_loaded = False
  colors = {}
  tech_cache = {}
  categories = {}

  def __init__(self, game_id):
    cls = type(self)
    self.game_id = game_id
    self.techs = {}

    cls.load_cache()
    self.techs = copy.deepcopy(cls.tech_cache)

  async def load_counts(self):
    for tech in self.techs.values():
      await self.load_counts_for(tech)

  async def load_counts_for(self, tech):
    tech['used'] = await self.get_value(tech['key'], 'used')
    tech['drawn'] = await self.get_value(tech['key'], 'drawn')

  async def get_value(self, tech_key, suffix):
    key = f"{self.game_id}/{tech_key}/{suffix}"
    value = await get_key_as_int(f"{key}")
    return value

  @classmethod
  def load_cache(cls):
    if cls.cache_loaded:
      return

    with open(os.path.join(DATA_PATH, 'techs.json')) as f:
      data = json.load(f)

    cls.colors = data['colors']
    cls.categories = data['categories']

    for color in cls.colors.values():
      color['techs'] = []

    for category in cls.categories.values():
      category['techs'] = []

    stats = data['stats']

    for color, techs in data['techsByColor'].items():
      for i, tech in enumerate(techs):
        tech['key'] = '-'.join(map(lambda s: s.lower(), tech['name'].split(' ')))
        tech['cost'] = stats[i]['cost']
        tech['minCost'] = stats[i]['minCost']
        tech['count'] = stats[i]['count']
        tech['color'] = color

        cls.tech_cache[tech['key']] = tech
        cls.categories[tech['category']]['techs'].append(tech['key'])
        cls.colors[color]['techs'].append(tech['key'])

    cls.cache_loaded = True


class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", DefaultHandler),
      (r"/techs/.*", TechsJsonHandler),
      (r"/websocket/.*", WebSocketHandler),
      # (r"/foo", MainHandler),
      # (r"/.*", DefaultHandler)
      # (r"/techs.js", TechsJsHandler),
      # (r"/", MainHandler)
      # (r"/(.*)", tornado.web.StaticFileHandler, {'path': STATIC_PATH, 'default_filename': 'index.html'}),
    ]
    settings = dict(
      cookie_secret="aoeusnth",
      # template_path=os.path.join(os.path.dirname(__file__), "templates"),
      static_path=STATIC_PATH,
      xsrf_cookies=True,
      debug=True,
      default_handler_class=DefaultHandler
    )
    super().__init__(handlers, **settings)


class DefaultHandler(tornado.web.RequestHandler):
  def data_received(self, chunk):
    raise NotImplementedError

  def get(self, *args, **kwargs):
    if DEV_MODE:
      self.write(requests.get("http://localhost:8080/%s" % self.request.uri).text)
    else:
      with open(os.path.join(DIST_PATH, "index.html")) as f:
        self.write(f.read())


class TechsJsonHandler(tornado.web.RequestHandler):
  def data_received(self, chunk):
    raise NotImplementedError

  async def get(self, *args, **kwargs):
    match = re.match(TECHS_JSON_RE, self.request.uri)
    if match:
      game_id = match.groups()[0].strip()
      game = Game(game_id)
      await game.load_counts()

      self.set_header("Content-Type", 'application/javascript')
      self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

      rv = {
        'techs': game.techs,
        'colors': game.colors,
        'categories': game.categories
      }

      self.write(json.dumps(rv, sort_keys=True, indent=2))


class WebSocketHandler(tornado.websocket.WebSocketHandler):
  game_clients = {}

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    self.game_id = None

  def data_received(self, chunk):
    raise NotImplementedError()

  def get_compression_options(self):
    return {}

  def open(self):
    logging.info("Client connected")
    match = re.match(WS_JSON_RE, self.request.uri)
    if match:
      self.game_id = match.groups()[0].strip()
    else:
      logging.warning("URI %s didn't match pattern" % self.request.uri)
      return

    logging.info(" - Client wants %s" % self.game_id)
    cls = type(self)
    if self.game_id not in cls.game_clients:
      cls.game_clients[self.game_id] = set()

    cls.game_clients[self.game_id].add(self)

  def on_close(self):
    logging.info("Client disconnected from %s" % self.game_id)
    type(self).game_clients[self.game_id].remove(self)

  @classmethod
  def send_updates(cls, game_id, msg):
    logging.info("Sending message to %d clients", len(cls.game_clients[game_id]))
    for client in cls.game_clients[game_id]:
      # noinspection PyBroadException
      try:
        client.write_message(msg)
      except Exception:
        logging.error("Error sending message", exc_info=True)

  async def on_message(self, message):
    logging.info("Got message %r for %s" % (message, self.game_id))
    parsed = json.loads(message)

    message_type = parsed['type']
    if message_type == 'ping':
      logging.info(f"Got ping from {self.game_id}")
    elif message_type == 'tech':
      await self.update_tech(parsed)
    else:
      logging.warning(f"Got message with invalid action: {parsed}")

  async def update_tech(self, parsed):
    tech_key = parsed['key']
    field = parsed['field']
    action = parsed['action']

    game = Game(self.game_id)

    if tech_key not in game.techs:
      logging.warning("Invalid tech key provided: %s" % parsed)
      return

    tech = game.techs[tech_key]
    await game.load_counts_for(tech)

    send_updates = False
    if field == 'drawn':
      ceiling = tech['count']
      floor = tech['used']
    elif field == 'used':
      ceiling = tech['drawn']
      floor = 0
    else:
      logging.warning("Invalid field attempted: %s" % parsed)
      return

    if action == 'inc':
      if tech[field] < ceiling:
        tech[field] += 1
        send_updates = True
      else:
        logging.warning(f"Trying to raise {field} above max")
    elif action == 'dec':
      if tech[field] > floor:
        tech[field] -= 1
        send_updates = True
      else:
        logging.warning(f"Trying to lower {field} below %d" % floor)
    else:
      logging.warning("Invalid action attempted: %s" % parsed)
      return

    if send_updates:
      logging.info(f"{tech_key}:{field} is now {tech[field]}")
      await set_key_cas(f"{self.game_id}/{tech_key}/{field}", -1, tech[field])
      type(self).send_updates(self.game_id, json.dumps({'key': tech_key, 'field': field, 'value': tech[field]}))


async def create_pool(redis_url):
  global pool

  logging.info("Creating Redis pool")
  pool = await aioredis.create_redis_pool(redis_url, minsize=1, maxsize=5)


def main():
  global STATIC_PATH, DEV_MODE
  # global TECH_TRACKER
  # TECH_TRACKER = TechTracker()

  define("port", default=os.environ.get('PORT', 8888), help="run on the given port", type=int)
  define("redis-url", default=os.environ.get("REDIS_URL", "redis://localhost"))
  define("dev", default=False, help="run in dev mode", type=bool)

  options.parse_command_line()
  DEV_MODE = options.dev

  # if DEV_MODE:
  #   STATIC_PATH = FRONTEND_PATH
  # else:
  #   STATIC_PATH = DIST_PATH

  logging.info("MAIN starting up")
  app = Application()
  app.listen(options.port)
  tornado.ioloop.IOLoop.current().run_sync(lambda: create_pool(options.redis_url))
  logging.info("Starting main loop")
  tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
  main()
