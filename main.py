#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import redis
import string
import random
import logging
from tools import server
from Handlers.BaseHandler import BaseHandler
from Handlers.LoginHandler import LoginHandler
from Handlers.RegisterHandler import RegisterHandler
from Handlers.LogoutHandler import LogoutHandler
from Handlers.ChatSocketHandler import ChatSocketHandler
from tornado import escape, web, websocket

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

logging.basicConfig(level="DEBUG")
logger = logging.getLogger(__name__)


class Application(web.Application):
    """Application
    """
    def __init__(self, redis_client: redis.Redis):
        handlers = [
            (r'/', MainHandler),
            (r'/login', LoginHandler, dict(redis_client=redis_client)),
            (r'/register', RegisterHandler, dict(redis_client=redis_client)),
            (r'/logout', LogoutHandler),
            (r'/chatsocket/(.*)$', ChatSocketHandler, dict(redis_client=redis_client)),
        ]
        settings = {
            'cookie_secret': ''.join([random.choice(string.printable) for _ in range(64)]),
            'template_path': './templates',
            'static_path': './static',
            'login_url': '/login',
            'xsrf_cookies': True,  # secret cookie
        }
        super(Application, self).__init__(handlers, **settings)


class MainHandler(BaseHandler):
    """MainHandler provide main page
    """
    @web.authenticated
    def get(self):
        """get main page
        """
        self.render('index.html', messages=[])


def main():
    """main
    """
    tchat_port = '8888'
    redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)
    redis_client.ping()
    app = Application(redis_client=redis_client)
    server.start_http(app, 8888)


if __name__ == '__main__':
    main()
