#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import demo_helpers
demo_helpers.mock_uris()

import gevent
from gevent.queue import Queue
import urllib2


URLS_SET = {}


def fetch_and_extract(url, task_queue):
    r = urllib2.urlopen(url)
    html = r.read()

    hrefs = demo_helpers.extract_hrefs(html)
    #print('fetch ', url, html, hrefs)
    task_queue.put_nowait((url, hrefs))


def recursive_crawl(url):
    all_urls = set()
    processing_urls = set()
    processed_urls = set()
    task_queue = Queue()

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
    fetch_and_extract(url, task_queue)

    while processing_urls:
        if task_queue.empty():
            gevent.sleep(0)
            continue

        done_url, hrefs = task_queue.get()

        mark_processed(done_url)

        for url in hrefs:
            add_to_all(url)

            if not is_processed(url) and not is_processing(url):
                mark_processing(url)
                gevent.spawn(fetch_and_extract, url, task_queue)

    print('Total latency', demo_helpers.TOTAL_LATENCY)


if __name__ == '__main__':
    url = 'http://example.com'
    recursive_crawl(url)
