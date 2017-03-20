# -*- coding: utf-8 -*-

import json
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
        """
        self.redis_client = redis_client

    def get(self):
        """Get register form
        """
        if self.current_user:
            self.redirect('/')
            return
        self.render('register.html')

    def post(self):
        """Post register form and try to sign up with these credentials
        """
        if self.current_user:
            self.redirect('/')
            return
        getusername = escape.xhtml_escape(self.get_argument('username'))
        getpassword = escape.xhtml_escape(self.get_argument('password'))
        getobjectname = escape.xhtml_escape(self.get_argument('object-name'))
        if not self.redis_client.exists('users-' + getusername) and \
            len(getusername) > 4 and len(getpassword) > 7:
                logger.debug('register new user : ' + getusername)
                self.redis_client.set('users-' + getusername, getpassword)
                self.redis_client.set('objects-' + getusername, json.dumps({'name': getobjectname}))
                self.set_secure_cookie('user', getusername, expires_days=1)
                self.set_secure_cookie('incorrect', '0')
                self.redirect('/')
        else:
            logger.info('invalid register form received : "' + getusername + '" "' + getpassword + '"')
            self.render('register.html', error='You can\'t create an account with these informations')
