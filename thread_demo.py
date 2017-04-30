#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import demo_helpers
demo_helpers.mock_uris()

import urllib2
from threading import Thread
from Queue import Queue

def worker():
    while True:
        item = q.get()
        do_work(item)
        q.task_done()

q = Queue()
for i in range(3):
     t = Thread(target=worker)
     t.daemon = True
     t.start()

for item in source():
    q.put(item)

q.join()       # block until all tasks are done
