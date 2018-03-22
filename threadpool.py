import threading
import time
import logging
import sys
import os
from time import gmtime, strftime
from logging.handlers import TimedRotatingFileHandler
try:
    from cStringIO import StringIO # Python 2
except ImportError:
    from io import StringIO        # Python 3

DEBUG = True

class PyLog():

  def __init__(self):
      self.FORMAT = '[%(threadName)2s] %(levelname)s: %(message)s'
      logging.basicConfig(format=self.FORMAT)
      self.directory = './log'
      try:
        os.makedirs(self.directory)
      except OSError:
        if not os.path.isdir(self.directory):
          raise
      self.filename = self.directory + strftime("/%Y-%m-%d.log", gmtime())
      self.log = logging.getLogger("PyLog")
      self.log.setLevel(logging.INFO)
      if DEBUG:
        self.log.setLevel(logging.DEBUG)
      self.handler = TimedRotatingFileHandler(self.filename, when='m', interval=1, backupCount=5)
      self.handler.setFormatter(logging.Formatter(self.FORMAT))
      self.log.addHandler(self.handler)

  def _log(self):
      return self.log

class ThreadPool():

    def __init__(self):
        self.active = []
        self.lock = threading.Lock()
        self.log = PyLog()._log()

    def makeActive(self, name):
        with self.lock:
            self.active.append(name)
            self.log.debug('Running: %s', self.active)

    def makeInactive(self, name):
        with self.lock:
            self.active.remove(name)
            self.log.debug('Remaining: %s', self.active)

######################################################
#                        TEST                        #
######################################################
def f(s, pool):
    pool.log.debug('Waiting to join the pool')
    with s:
        name = threading.currentThread().getName()
        pool.makeActive(name)
        time.sleep(0.5)
        pool.makeInactive(name)

def main():
    pool = ThreadPool()
    s = threading.Semaphore(3)
    for i in range(20):
        t = threading.Thread(target=f, name='thread_'+str(i), args=(s, pool))
        t.start()

if __name__ == '__main__':
    main()