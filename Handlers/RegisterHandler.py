# -*- coding: utf-8 -*-

import redis
import logging
from tornado import escape
from Handlers.BaseHandler import BaseHandler

logger = logging.getLogger(__name__)


class RegisterHandler(BaseHandler):
    """Handle user register actions
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
        incorrect = self.get_secure_cookie('incorrect') or 0
        if int(incorrect) > 5:
            logger.warning('an user have been blocked : ' + self.current_user)
            self.write('<center>blocked</center>')
            return
        self.render('login.html', user=self.current_user)

    def post(self):
        """Post register form and try to sign up with these credentials
        """
        getusername = escape.xhtml_escape(self.get_argument('username'))
        getpassword = escape.xhtml_escape(self.get_argument('password'))
        if not self.redis_client.exists('users-' + getusername):
            logger.debug('register new user : ' + getusername)
            self.redis_client.set('users-' + getusername, getpassword)
            self.set_secure_cookie("user", getusername, expires_days=1)
            self.set_secure_cookie("incorrect", "0")
            self.redirect('/')
        else:
            logger.info('invalid credentials : "' + getusername + '" "' + getpassword + '"')
            incorrect = self.get_secure_cookie('incorrect') or 0
            self.set_secure_cookie('incorrect', str(int(incorrect) + 1), expires_days=1)
            self.render('login.html', user=self.current_user)
