# -*- coding: utf-8 -*-

import redis
import logging
from tornado import web, websocket
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class ObjectSocketHandler(websocket.WebSocketHandler, BaseHandler):
    """ObjectSocketHandler
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
        logger.info('open ws for "' + path_request + '"')
        self.channel = path_request
        self.subscrib.subscribe(**{self.channel: self.send_updates})
        self.thread = self.subscrib.run_in_thread(sleep_time=0.001)
        object_data = self.redis_client.get(path_request)
        if object_data:
            self.write_message(object_data)  # send initial state

    def on_close(self):
        """on_close on websocket close
        """
        self.subscrib.unsubscribe(self.channel)
        self.thread.stop()

    def send_updates(self, message):
        """send_updates

        :param message: object data received from a publication (redis)
        """
        logger.info('send message for %s\'s object', self.current_user.decode())
        try:
            self.write_message(message['data'])  # redis has the true message object under the 'data' key
        except websocket.WebSocketClosedError:
            logger.error("Error sending message", exc_info=True)

    def on_message(self, message):
        """on_message

        :param message: message received from the user object
        """
        logger.info('got message "%r" from %s\'s object', message, self.current_user.decode())
        self.redis_client.publish(self.channel, message)  # publish it on the queue
        self.redis_client.set(self.channel, message)  # write it in the database
