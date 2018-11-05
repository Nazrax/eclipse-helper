# IBM Confidential - OCO Source Materials
# Copyright (c) IBM Corp. 1992-2018
# Copyright (c) Internet Security Systems, Inc. 1992-2006
# The source code for this program is not published or otherwise divested of its trade secrets,
# irrespective of what has been deposited with the U.S. Copyright Office.

import json
import logging
import os
import re

import requests
from tornado.options import define, options
import tornado.web
import tornado.websocket

import asyncio
import aioredis


DIST_PATH = os.path.join(os.path.dirname(__file__), "dist")
STATIC_PATH = os.path.join(DIST_PATH, 'static')
DATA_PATH = os.path.join(os.path.dirname(__file__), "data")
DEV_MODE = False
TECHS_JSON_RE = re.compile(r"^/techs/(\w+).json$")
WS_JSON_RE = re.compile(r"^/websocket/(\w+)$")


class Game:
  games = {}

  def __init__(self):
    self.techs = {}
    self.colors = {}
    self.categories = {}

    self.load_techs()

  @classmethod
  def get_game(cls, game_id):
    if game_id not in cls.games:
      logging.info("Loading game ID %s" % game_id)
      cls.games[game_id] = Game()

    return cls.games[game_id]

  def load_techs(self):
    with open(os.path.join(DATA_PATH, 'techs.json')) as f:
      data = json.load(f)

    self.colors = data['colors']
    self.categories = data['categories']

    for color in self.colors.values():
      color['techs'] = []

    for category in self.categories.values():
      category['techs'] = []

    stats = data['stats']

    for color, techs in data['techsByColor'].items():
      for i, tech in enumerate(techs):
        tech['key'] = '-'.join(map(lambda s: s.lower(), tech['name'].split(' ')))
        tech['cost'] = stats[i]['cost']
        tech['minCost'] = stats[i]['minCost']
        tech['count'] = stats[i]['count']
        tech['drawn'] = 0  # TODO Rig up Reddis
        tech['purchased'] = 0  # TODO Rig up Reddis
        tech['color'] = color

        self.techs[tech['key']] = tech
        self.categories[tech['category']]['techs'].append(tech['key'])
        self.colors[color]['techs'].append(tech['key'])


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

  def get(self, *args, **kwargs):
    match = re.match(TECHS_JSON_RE, self.request.uri)
    if match:
      game_id = match.groups()[0]
      game = Game.get_game(game_id)

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
      self.game_id = match.groups()[0]
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

  def on_message(self, message):
    logging.info("Got message %r for %s" % (message, self.game_id))
    parsed = tornado.escape.json_decode(message)
    tech_key = parsed['key']
    field = parsed['field']
    action = parsed['action']

    game = Game.get_game(self.game_id)

    if tech_key not in game.techs:
      logging.warning("Invalid tech key provided: %s" % message)
      return

    tech = game.techs[tech_key]
    send_updates = False
    if field == 'drawn':
      ceiling = tech['count']
      floor = tech['purchased']
    elif field == 'purchased':
      ceiling = tech['drawn']
      floor = 0
    else:
      logging.warning("Invalid field attempted: %s" % message)
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
      logging.warning("Invalid action attempted: %s" % message)
      return

    if send_updates:
      logging.info(f"{tech_key}:{field} is now {tech[field]}")
      type(self).send_updates(self.game_id, json.dumps({'key': tech_key, 'field': field, 'value': tech[field]}))

def main():
  global STATIC_PATH, DEV_MODE
  # global TECH_TRACKER
  # TECH_TRACKER = TechTracker()

  define("port", default=os.environ.get('PORT', 8888), help="run on the given port", type=int)
  define("dev", default=False, help="run in dev mode", type=bool)

  tornado.options.parse_command_line()
  DEV_MODE = options.dev

  # if DEV_MODE:
  #   STATIC_PATH = FRONTEND_PATH
  # else:
  #   STATIC_PATH = DIST_PATH

  logging.info("MAIN starting up")
  app = Application()
  app.listen(options.port)
  logging.info("Starting main loop")
  tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
  main()
