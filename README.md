# Learn Spider

Practicing code to learn to write a spider

To see how it works, first install requirements: `pip install -r requirements.txt`,
then execute each demo by `time python <demo file name>`.


- `gevent_dq_demo.py`

  dq - Data Queue

  This demo consists of two parts:
  1. the master greenlet, ``recursive_crawl``
  2. the spawned greenlets to fetch url, ``fetch_and_extract``

  When urls are extracted from a html, every one of them, if hasn't been processed yet,
  will spawn a new greenlet to fetch itself. This may be dangerous
  if a html contains a huge number of urls, then almost the same amount of
  greenlets will be spawned without limitation.

- `gevent_dqp_demo.py`

  dqp - Data Queue with a greenlet Pool

  This is an enhanced version of ``gevent_dq_demo.py``, it use a greenlet pool
  to restrict the number of greenlets that could be spawned simultaneously.

- `gevent_tq_demo.py`

  tq - Task Queue

  This demo use a ``task_queue`` to schedule url fetching tasks.
  Unlike ``gevent_dq_demo.py``, the fetched data will be handled in task,
  rather that in a centralized master greenlet, new tasks are also
  generated in task itself.

  Since each task will modify the global sets which store the urls and processing state,
  the working flow of this program is not very clear, thus it's not recommended.

- `gevent_tq_dq_demo.py`

  tq_dq - Task Queue and Data Queue

  This demo combines the benefits of both ``task_queue`` and ``data_queue``,
  it use a centralized master greenlet to control both task scheduling
  and data processing.
