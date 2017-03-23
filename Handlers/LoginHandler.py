# -*- coding: utf-8 -*-

import redis
import logging
from tornado import escape
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class LoginHandler(BaseHandler):
    """Handle user login actions
    """
    def initialize(self, redis_client: redis.Redis):
        """initialize

        :param redis_client:
        :return:
        """
        self.redis_client = redis_client

    def get(self):
        """Get login form
        """
        self.render('login.html', user=self.current_user)

    def post(self):
        """Post connection form and try to connect with these credentials
        """
        getusername = escape.xhtml_escape(self.get_argument('username'))
        getpassword = escape.xhtml_escape(self.get_argument('password'))
        if self.redis_client.exists('users-' + getusername) \
                and getpassword == bytes.decode(self.redis_client.get('users-' + getusername)):
            logger.debug('user connected : ' + getusername)
            self.set_secure_cookie("user", getusername, expires_days=1)
            self.redirect('/')
        else:
            logger.info('invalid credentials : "' + getusername + '" "' + getpassword + '"')
            self.render('login.html', user=self.current_user)
