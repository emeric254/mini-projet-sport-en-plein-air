# -*- coding: utf-8 -*-

import redis
import logging
from tornado import web, escape
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class UpdateHandler(BaseHandler):
    """Handle update actions
    """
    def initialize(self, redis_client: redis.Redis):
        """initialize

        :param redis_client: redis connection
        """
        self.redis_client = redis_client

    @web.authenticated
    def post(self, path_request):
        message = self.get_body_argument('data')
        self.redis_client.publish(path_request, message)
        self.redis_client.set(path_request, message)
