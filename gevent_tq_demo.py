#!/usr/bin/env python
# coding: utf-8

"""
tq - Task Queue

This demo use a ``task_queue`` to schedule url fetching tasks.
Unlike ``gevent_dq_demo.py``, the fetched data will be handled in task,
rather that in a centralized master greenlet, new tasks are also
generated in task itself.

Since each task will modify the global sets which store the urls and processing state,
the working flow of this program is not very clear, thus it's not recommended.
"""

from __future__ import print_function

import gevent.monkey
gevent.monkey.patch_all()

import demo_helpers
demo_helpers.mock_uris()

import gevent
from gevent.queue import JoinableQueue
import urllib2


def url_worker(name, processed_urls, add_to_all, q):
    print('worker start', name)
    while True:
        url = q.get()
        print('worker {} get {}'.format(name, url))

        r = urllib2.urlopen(url)
        html = r.read()

        hrefs = demo_helpers.extract_hrefs(html)
        #print('fetch ', url, html, hrefs)
        for sub_url in hrefs:
            add_to_all(sub_url)
            if sub_url not in processed_urls:
                q.put_nowait(sub_url)

        if url in processed_urls:
            print('Duplicate processed url {}'.format(url))
        else:
            processed_urls.add(url)
        q.task_done()


def recursive_crawl(url):
    all_urls = set()
    processed_urls = set()
    task_queue = JoinableQueue()

    def add_to_all(url):
        if url not in all_urls:
            print('Record url {}'.format(url))
            all_urls.add(url)

    task_queue.put_nowait(url)

    # Start workers
    workers = []
    for i in xrange(10):
        workers.append(
            gevent.spawn(url_worker,
                         i, processed_urls, add_to_all, task_queue)
        )
    print('workers', len(workers))

    task_queue.join()

    print('Processed', len(processed_urls), 'All', len(all_urls))
    print('Total latency', demo_helpers.TOTAL_LATENCY)


if __name__ == '__main__':
    url = 'http://example.com'
    recursive_crawl(url)
