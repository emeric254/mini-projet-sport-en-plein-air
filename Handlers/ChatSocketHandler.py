# -*- coding: utf-8 -*-

import uuid
import json
import redis
import logging
from tornado import escape, web, websocket
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class ChatSocketHandler(websocket.WebSocketHandler, BaseHandler):
    """ChatSocketHandler
    """
    def initialize(self, redis_client: redis.Redis):
        """initialize

        :param redis_client:
        """
        self.redis_client = redis_client
        self.subscrib = redis_client.pubsub()
        self.thread = None

    def get_compression_options(self):
        """get_compression_options
        """
        return {}  # Non-None enables compression with default options.

    @web.authenticated
    def open(self, path_request):
        """open

        :param path_request:
        """
        self.channel = 'messages' + path_request
        self.subscrib.subscribe(**{self.channel: self.send_updates})
        self.thread = self.subscrib.run_in_thread(sleep_time=0.001)

    def on_close(self):
        """on_close
        """
        self.subscrib.unsubscribe(self.channel)
        self.thread.stop()

    def send_updates(self, chat):
        """send_updates

        :param chat:
        """
        try:
            self.write_message(chat['data'])
        except websocket.WebSocketClosedError:
            logger.error("Error sending message", exc_info=True)

    def on_message(self, message):
        """on_message

        :param message:
        """
        logger.info('got message "%r" from %s', message, self.current_user.decode())
        parsed = escape.json_decode(message)
        chat = {
            'id': str(uuid.uuid4()),
            'author': self.current_user.decode(),
            'body': parsed['body'],
        }
        chat['html'] = escape.to_basestring(self.render_string('message.html', message=chat))
        self.redis_client.publish(self.channel, json.dumps(chat))
