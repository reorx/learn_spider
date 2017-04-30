#!/usr/bin/env python
# coding: utf-8

import gevent
import gevent.monkey

gevent.monkey.patch_socket()

import httpretty
from tornado.ioloop import IOLoop
from tornado.httpclient import HTTPClient, AsyncHTTPClient


httpretty.enable()
httpretty.HTTPretty.allow_net_connect = False

httpretty.register_uri(httpretty.GET, 'http://www.google.com', body='OK')

io_loop = IOLoop.instance()


http_client = HTTPClient()
response = http_client.fetch("http://www.google.com")
print response.body


def handle_resp(resp):
    print 'callbacks', len(io_loop._callbacks)
    print 'timeouts', len(io_loop._timeouts)
    print 'resp', resp.request.url, resp.code

    if not io_loop._timeouts:
        io_loop.stop()


def add_tasks(*args, **kwargs):
    print args, kwargs
    client = AsyncHTTPClient()
    for i in xrange(3):
        client.fetch('http://www.google.com', handle_resp)

    print 'callbacks', len(io_loop._callbacks)

io_loop.add_callback(add_tasks)

io_loop.start()
