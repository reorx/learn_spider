#!/usr/bin/env python
# coding: utf-8

"""
dq - Data Queue

This demo consists of two parts:
1. the master greenlet, ``recursive_crawl``
2. the spawned greenlets to fetch url, ``fetch_and_extract``

When urls are extracted from a html, every one of them, if hasn't been processed yet,
will spawn a new greenlet to fetch itself. This may be dangerous
if a html contains a huge number of urls, then almost the same amount of
greenlets will be spawned without limitation.
"""

from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import demo_helpers
demo_helpers.mock_uris()

import gevent
from gevent.queue import Queue
import urllib2


def fetch_and_extract(url, data_queue):
    r = urllib2.urlopen(url)
    html = r.read()

    hrefs = demo_helpers.extract_hrefs(html)
    #print('fetch ', url, html, hrefs)
    data_queue.put_nowait((url, hrefs))


def recursive_crawl(url):
    all_urls = set()
    processing_urls = set()
    processed_urls = set()
    data_queue = Queue()

    def is_processed(url):
        return url in processed_urls

    def is_processing(url):
        return url in processing_urls

    def mark_processed(url):
        if is_processing(url):
            processing_urls.remove(url)
        if is_processed(url):
            print('Duplicate processed url {}'.format(url))
        else:
            processed_urls.add(url)

    def mark_processing(url):
        processing_urls.add(url)

    def add_to_all(url):
        if url not in all_urls:
            print('Record url {}'.format(url))
            all_urls.add(url)

    mark_processing(url)
    fetch_and_extract(url, data_queue)

    while processing_urls:
        if data_queue.empty():
            gevent.sleep(0)
            continue

        done_url, hrefs = data_queue.get()

        mark_processed(done_url)

        for sub_url in hrefs:
            add_to_all(sub_url)

            if not is_processed(sub_url) and not is_processing(sub_url):
                mark_processing(sub_url)
                gevent.spawn(fetch_and_extract, sub_url, data_queue)

    print('Processed', len(processed_urls), 'All', len(all_urls))
    print('Total latency', demo_helpers.TOTAL_LATENCY)


if __name__ == '__main__':
    url = 'http://example.com'
    recursive_crawl(url)
