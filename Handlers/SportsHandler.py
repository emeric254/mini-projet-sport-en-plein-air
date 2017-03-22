# -*- coding: utf-8 -*-

import redis
import logging
from tornado import web
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class SportsHandler(BaseHandler):
    """SportsHandler
    """
    def initialize(self, redis_client: redis.Redis):
        """initialize

        :param redis_client: redis connection
        """
        self.redis_client = redis_client

    @web.authenticated
    def get(self):
        self.write(self.redis_client.get('sports'))
