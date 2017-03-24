#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import os
import sys
import time
import json
import random
import logging
import requests
from bs4 import BeautifulSoup
from AbstractDaemon import Daemon

logging.basicConfig(filename='connected_object_simulator.log', level='DEBUG')
logger = logging.getLogger(__name__)

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

target_url = 'http://127.0.0.1:8888'

possible_positions = [
    'Toulouse',
    'Paris',
    'Bordeau',
    'Lyon',
    'Marseille',
    'Lille'
]
meteo = {}
with open('openweathermap.token', mode='r') as file:
    api_token = file.read().strip()


def refresh_user_object(session, username, password):
    try:
        r = session.get(target_url + '/login')
    except requests.exceptions.RequestException:
        logger.error('This host can not be contacted...')
        return  # exit this function on error
    if r.status_code != 200:
        logger.error('The login page can not be retrieve...')
        return  # exit this function on error
    b = BeautifulSoup(str(r.text), 'lxml')
    token = b.find(attrs={'name': '_xsrf'})
    if token:
        token = token.get('value')
        data = {
            '_xsrf': token,
            'username': username,
            'password': password
        }
        session.post(target_url + '/login', data=data)
        if r.status_code != 200:
            logger.error('The login request encounter an error...')
            return  # exit this function on error
    else:
        logger.error('Can not retrieve the token')
    objectname = 'objects-' + username
    position = random.choice(possible_positions)  # random city
    if position not in meteo:  # not already retrieve for this refresh run
        r = requests.get('http://api.openweathermap.org/data/2.5/forecast?q=' + position + ',fr&APPID=' + api_token)
        meteo[position] = json.loads(r.text)
    data = {
        '_xsrf': token,
        'data': json.dumps({
            'name': objectname[8:],
            'position': position,
            'weather': meteo[position]
        })
    }
    session.post(target_url + '/update/' + objectname, data=data)


def do_something():
    meteo.clear()  # reset
    session = requests.Session()
    files = [f for f in os.listdir('.') if os.path.isfile(f) and f.endswith('.object')]
    for filename in files:
        username = filename[:-7]
        with open(filename, mode='r') as file:
            password = file.read().strip()
        if username and password:
            refresh_user_object(session, username, password)
        else:
            logger.warning('Can not find right username and password in : ' + filename)
    logger.debug('It\'s a good time to be a simulator !')


class MyDaemon(Daemon):

    def run(self):
        while True:
            do_something()
            time.sleep(5 * 60)  # 5 minutes = 5 * 60 seconds


def usage_help():
    print('usage: ' + sys.argv[0] + ' start|stop|restart|status|help|run-once')


if __name__ == '__main__':
    daemon = MyDaemon('/tmp/MyDaemon.pid')
    if len(sys.argv) >= 2:
        if 'start' == sys.argv[1]:
            print('Starting daemon')
            daemon.start()
        elif 'stop' == sys.argv[1]:
            print('Stopping daemon')
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            print('Restarting daemon')
            daemon.restart()
        elif 'status' == sys.argv[1]:
            if daemon.status():
                print('running')
            else:
                print('not running')
        elif 'help' == sys.argv[1]:
            usage_help()
        elif 'run-once' == sys.argv[1]:
            do_something()
        else:
            print('Unknown argument')
            usage_help()
            sys.exit(2)
        sys.exit(0)
    else:
        print('No argument')
        usage_help()
        sys.exit(2)
