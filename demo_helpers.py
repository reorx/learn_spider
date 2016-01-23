#!/usr/bin/env python
# coding: utf-8

import time
import random
import httpretty
from bs4 import BeautifulSoup


URIS = ['example.com', 'foo.com', 'bar.com', 'baz.com', 'qux.com']


def mock_uris():
    httpretty.enable()
    httpretty.HTTPretty.allow_net_connect = False

    for i in URIS:
        url = 'http://{}'.format(i)
        #print 'Register', url
        httpretty.register_uri(
            httpretty.GET, url,
            streaming=True,
            body=mock_latency_response(i, url))
        for j in xrange(1, 6):
            url = 'http://{}/{}'.format(i, j)
            #print 'Register', url
            httpretty.register_uri(
                httpretty.GET, url,
                streaming=True,
                body=mock_latency_response('end_page', url))


TOTAL_LATENCY = 0


def mock_latency_response(domain, seed):
    global TOTAL_LATENCY
    random.seed(seed)
    latency = float(random.randint(1, 9)) / 10
    TOTAL_LATENCY += latency
    time.sleep(latency)
    html = get_file_data('data/{}.html'.format(domain))
    yield html


def get_file_data(filename):
    with open(filename, 'r') as f:
        return f.read()


def extract_hrefs(html):
    if isinstance(html, str):
        html = html.decode('utf8')
    soup = BeautifulSoup(html, 'html.parser')

    hrefs = set()
    for i in soup.find_all('a'):
        href = i.attrs.get('href')
        if href:
            hrefs.add(href)

    return hrefs
