#!/usr/bin/env python
# coding: utf-8

import gevent
import gevent.monkey

gevent.monkey.patch_all()

import time


def foo():
    print '> foo'
    gevent.spawn(bar)
    gevent.sleep(1)
    print 'foo >'


def bar():
    print '> bar'
    gevent.sleep(4)
    print 'bar >'


gevent.joinall([
    gevent.spawn(foo)
])
