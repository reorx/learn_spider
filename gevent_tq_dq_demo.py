#!/usr/bin/env python
# coding: utf-8

"""
tq_dq - Task Queue and Data Queue

This demo combines the benefits of both ``task_queue`` and ``data_queue``,
it use a centralized master greenlet to control both task scheduling
and data processing.
"""

from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import demo_helpers
demo_helpers.mock_uris()

import gevent
from gevent.queue import Queue
import urllib2


def url_worker(name, tq, dq):
    print('worker start', name)
    while True:
        url = tq.get()
        print('worker {} get {}'.format(name, url))

        r = urllib2.urlopen(url)
        html = r.read()

        hrefs = demo_helpers.extract_hrefs(html)

        dq.put_nowait((url, hrefs))


def recursive_crawl(url):
    all_urls = set()
    processing_urls = set()
    processed_urls = set()
    task_queue = Queue()
    data_queue = Queue()

    def is_processed(url):
        return url in processed_urls

    def is_processing(url):
        return url in processing_urls

    def mark_processed(url):
        if is_processing(url):
            processing_urls.remove(url)
        #if is_processed(url):
        #    print('Duplicate processed url {}'.format(url))
        #else:
        #    processed_urls.add(url)
        processed_urls.add(url)

    def mark_processing(url):
        processing_urls.add(url)

    def add_to_all(url):
        if url not in all_urls:
            print('Record url {}'.format(url))
            all_urls.add(url)

    mark_processing(url)
    task_queue.put_nowait(url)

    # Start workers
    workers = []
    for i in xrange(10):
        workers.append(
            gevent.spawn(url_worker,
                         i, task_queue, data_queue)
        )
    print('workers', len(workers))

    while processing_urls:
        if data_queue.empty():
            gevent.sleep(0)
            continue

        done_url, hrefs = data_queue.get()

        mark_processed(done_url)

        for sub_url in hrefs:
            add_to_all(sub_url)

            # test duplication
            if not is_processed(sub_url) and not is_processing(sub_url):
                mark_processing(sub_url)
                task_queue.put_nowait(sub_url)

    print('Processed', len(processed_urls), 'All', len(all_urls))
    print('Total latency', demo_helpers.TOTAL_LATENCY)


if __name__ == '__main__':
    url = 'http://example.com'
    recursive_crawl(url)
