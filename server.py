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
import time

import requests
from tornado.options import define, options
import tornado
import tornado.web
import tornado.websocket

import aioredis


DIST_PATH = os.path.join(os.path.dirname(__file__), "dist")
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
IMAGES_PATH = os.path.join(os.path.dirname(__file__), "static", "images")
STATIC_PATH = os.path.join(DIST_PATH, 'static')
DEV_MODE = False
TECHS_JSON_RE = re.compile(r"^/techs/(\w+).json$")
WS_JSON_RE = re.compile(r"^/websocket/(\w+)$")

LEFT_PERCENT = 5.4
RIGHT_PERCENT = 84.2

TOP_PERCENT = 31
BOTTOM_PERCENT = 88

pool = None


async def get_key_as_int(key, dflt=0):
  with await pool as redis:
    v = await redis.get(key)

  # noinspection PyBroadException
  try:
    return int(v) if v else dflt
  except Exception:
    return dflt


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
    self.round = 0
    self.round_time = 0

    cls.load_cache()
    self.techs = copy.deepcopy(cls.tech_cache)

  async def load_counts(self):
    for tech in self.techs.values():
      await self.load_counts_for(tech)

  async def load_counts_for(self, tech):
    tech['used'] = await self.get_value(tech['key'], 'used')
    tech['drawn'] = await self.get_value(tech['key'], 'drawn')

  async def save_counts_for(self, tech):
    await self.set_value(tech['used'], tech['key'], 'used')
    await self.set_value(tech['drawn'], tech['key'], 'drawn')

  async def load_round(self):
    self.round = await self.get_value('round', 'value', dflt=1)
    self.round_time = await self.get_value('round', 'time', dflt=int(time.time()))

  async def save_round(self, new_round, new_time):
    await self.set_value(new_round, 'round', 'value')
    await self.set_value(new_time, 'round', 'time')

  async def get_value(self, *path, dflt=0):
    key = "/".join([self.game_id, *path])
    value = await get_key_as_int(f"{key}", dflt)
    return value

  async def set_value(self, value, *path):
    key = "/".join([self.game_id, *path])
    await set_key_cas(key, -1, value)

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
        tech['top'] = "%s%%" % str(TOP_PERCENT + (BOTTOM_PERCENT - TOP_PERCENT) / 2 * (cls.colors[color]['index']))
        tech['left'] = "%s%%" % str(LEFT_PERCENT + (RIGHT_PERCENT - LEFT_PERCENT) / 7 * i)

        cls.tech_cache[tech['key']] = tech
        cls.categories[tech['category']]['techs'].append(tech['key'])
        cls.colors[color]['techs'].append(tech['key'])

    cls.cache_loaded = True


class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"/", DefaultHandler),
      (r"/techs/.*", JsonHandler),
      (r"/websocket/.*", WebSocketHandler),
      (r"/images/(.*)", tornado.web.StaticFileHandler, {'path': IMAGES_PATH}),
      # (r"/settings.json", SettingsHandler),
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


class JsonHandler(tornado.web.RequestHandler):
  def data_received(self, chunk):
    raise NotImplementedError

  async def get(self, *args, **kwargs):
    match = re.match(TECHS_JSON_RE, self.request.uri)
    if match:
      game_id = match.groups()[0].strip()
      game = Game(game_id)
      await game.load_counts()
      await game.load_round()

      self.set_header("Content-Type", 'application/javascript')
      self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

      settings = {
        'available_checkbox_url': os.environ.get('AVAILABLE_CHECKBOX_URL', '/images/available_checkbox.png'),
        'empty_checkbox_url': os.environ.get('EMPTY_CHECKBOX_URL', '/images/empty_checkbox.png'),
        'taken_checkbox_url': os.environ.get('TAKEN_CHECKBOX_URL', '/images/taken_checkbox.png'),
        'techboard_url': os.environ.get('TECHBOARD_URL', '/images/empty_techboard.png')
      }

      rv = {
        'techs': game.techs,
        'colors': game.colors,
        'categories': game.categories,
        'settings': settings,
        'round': game.round,
        'round_time': game.round_time
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
    logging.info(f" - {self.game_id} now has {len(self.game_clients[self.game_id])} clients")

  def on_close(self):
    logging.info("Client disconnected from %s" % self.game_id)
    type(self).game_clients[self.game_id].remove(self)

  @classmethod
  async def send_updates(cls, game_id, msg):
    logging.info("Sending message to %d clients", len(cls.game_clients[game_id]))
    for client in cls.game_clients[game_id]:
      # noinspection PyBroadException
      try:
        await client.write_message(msg)
      except Exception:
        logging.error("Error sending message", exc_info=True)

  async def on_message(self, message):
    parsed = json.loads(message)

    if parsed['type'] != 'ping':
      logging.info("Got message %r for %s" % (message, self.game_id))

    message_type = parsed['type']
    if message_type == 'ping':
      pass
    elif message_type == 'tech':
      await self.update_tech(parsed)
    elif message_type == 'round':
      await self.update_round(parsed)
    else:
      logging.warning(f"Got message with invalid action: {parsed}")

  async def update_round(self, parsed):
    new_round = int(parsed['round'])
    new_time = int(time.time())

    if new_round < 1 or new_round > 9:
      logging.warning("Sent bad round %s" % new_round)
      return

    game = Game(self.game_id)
    await game.load_round()
    if new_round != game.round:
      logging.info(f"Round is now {new_round}")
      toast = f"Round went from {game.round} to {new_round}"
      await game.save_round(new_round, new_time)
      await set_key_cas(f"{self.game_id}/round/value", -1, new_round)
      await set_key_cas(f"{self.game_id}/round/time", -1, new_time)
      payload = {
        'type': 'round',
        'round': new_round,
        'time': new_time,
        'toast': toast
      }
      await type(self).send_updates(self.game_id, json.dumps(payload))

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

    old_value = tech[field]

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
      payload = {
        'type': 'tech',
        'key': tech_key,
        'field': field,
        'value': tech[field],
        'toast': f"{tech['name']}:{field} went from {old_value} to {tech[field]}"
      }
      await type(self).send_updates(self.game_id, json.dumps(payload))


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
