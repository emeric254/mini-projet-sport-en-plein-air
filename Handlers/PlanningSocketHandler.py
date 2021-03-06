# -*- coding: utf-8 -*-

import json
import datetime
import redis
import logging
from tornado import web, websocket
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


def verif_planning(planning):
    timestamp = datetime.datetime.now().timestamp()
    hour = datetime.datetime.now().hour
    if not planning or not isinstance(planning, list):
        planning = [{
            'hour': datetime.datetime.now().hour - 1,
            'timestamp': timestamp - 3600,
            'users': []
        }]
    last_timestamp = planning[-1]['timestamp']
    while datetime.datetime.fromtimestamp(planning[0]['timestamp']).hour < hour:
        planning.pop(0)
        planning.append({
            'hour': datetime.datetime.fromtimestamp(last_timestamp).hour + 1,
            'timestamp': last_timestamp + 3600,
            'users': [],
        })
        last_timestamp = planning[-1]['timestamp']
    while len(planning) < 24:
        planning.append({
            'hour': datetime.datetime.fromtimestamp(last_timestamp).hour + 1,
            'timestamp': last_timestamp + 3600,
            'users': [],
        })
        last_timestamp = planning[-1]['timestamp']
    return planning


class PlanningSocketHandler(websocket.WebSocketHandler, BaseHandler):
    """ChatSocketHandler
    """
    def initialize(self, redis_client: redis.Redis):
        """initialize

        :param redis_client: redis connection
        """
        self.redis_client = redis_client
        self.subscrib = redis_client.pubsub()
        self.thread = None
        self.channel = None

    def get_compression_options(self):
        """get_compression_options
        """
        return {}  # Non-None enables compression with default options.

    @web.authenticated
    def open(self, path_request):
        """open

        :param path_request: uri requested for the websocket
        """
        logger.info('open ws for planning "' + path_request + '"')
        self.channel = path_request
        self.subscrib.subscribe(**{self.channel: self.send_updates})
        self.thread = self.subscrib.run_in_thread(sleep_time=0.001)
        # load and send initial data to the user
        planning_data = self.redis_client.get(path_request)
        if not planning_data:
            planning_data = []
            current_hour = datetime.datetime.now().hour
            timestamp = datetime.datetime.now().timestamp()
            for hour in range(current_hour, current_hour + 24):
                planning_data.append({
                    'hour': hour % 24,
                    'timestamp': timestamp,
                    'users': [],
                })
            planning_data = json.dumps(planning_data)
        self.write_message(planning_data)  # send initial state

    def on_close(self):
        """on_close on websocket close
        """
        self.subscrib.unsubscribe(self.channel)
        self.thread.stop()

    def send_updates(self, message):
        """send_updates

        :param message: object data received from a publication (redis)
        """
        logger.info('sending message for planning ' + self.channel)
        try:
            self.write_message(message['data'])  # redis has the true message object under the 'data' key
        except websocket.WebSocketClosedError:
            logger.error("Error sending message", exc_info=True)

    def on_message(self, message):
        """on_message

        :param message: message received from the user object
        """
        logger.info('got message for planning ' + self.channel)
        if message == 'refresh':
            message = verif_planning(self.redis_client.get(self.channel))
        else:
            data = json.loads(message)
            message = verif_planning(data)
        message = json.dumps(message)
        # add or remove current user to a time in the planning
        self.redis_client.publish(self.channel, message)  # publish it on the queue
        self.redis_client.set(self.channel, message)  # write it in the database
