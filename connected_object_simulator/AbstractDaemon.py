# -*- coding: utf-8 -*-
"""Generic linux daemon base class for python 3.x.

For further information take a look at :
https://github.com/toast254/SimpleDaemon/tree/master/simpledaemon
"""

import os
import time
import atexit
import signal
import logging

logger = logging.getLogger(__name__)


class Daemon:
    """A generic daemon class.
    Usage: subclass the daemon class and override the run() method."""

    def __init__(self, pidfile):
        self.pidfile = pidfile

    def daemonize(self):
        """Deamonize class. UNIX double fork mechanism."""
        # do first fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit first parent
        except OSError as err:
            logger.error('fork #1 failed : ' + str(err))
            sys.exit(1)
        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # exit from second parent
        except OSError as err:
            logger.error('fork #2 failed : ' + str(err))
            sys.exit(1)
        # redirect standard file descriptors
        sys.stdin.flush()
        sys.stdout.flush()
        sys.stderr.flush()
        dev_null = os.open(os.devnull, os.O_RDWR)
        os.dup2(dev_null, sys.stdin.fileno())
        os.dup2(dev_null, sys.stdout.fileno())
        os.dup2(dev_null, sys.stderr.fileno())
        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, mode='w+') as f:
            f.write(pid + '\n')

    def delpid(self):
        os.remove(self.pidfile)

    def check_pid(self):
        """Check the daemon pidfile to see if the daemon runs"""
        try:
            with open(self.pidfile, mode='r') as pf:
                return int(pf.read().strip())
        except IOError:
            logger.error('Can not read pidfile : ' + self.pidfile)
        return None

    def start(self):
        """Start the daemon."""
        if self.check_pid():
            logger.info('pidfile ' + str(self.pidfile) + ' already exist. Daemon already running ?')
            sys.exit(1)
        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """Stop the daemon."""
        if not self.check_pid():
            logger.info('pidfile ' + str(self.pidfile) + ' does not exist. Daemon not running ?')
            return  # not an error in a restart
        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            e = str(err.args)
            if e.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    logger.warning('Can not find the pidfile : "' + pidfile + '" while a Daemon process runs')
            else:
                logger.error(str(err.args))
                sys.exit(1)

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    def status(self):
        """Status of the daemon.
        :return True if running
        """
        return self.check_pid() is not None

    def run(self):
        """You should override this method when you subclass Daemon.
        It will be called after the process has been daemonized by
        start() or restart()."""
        raise NotImplementedError()
