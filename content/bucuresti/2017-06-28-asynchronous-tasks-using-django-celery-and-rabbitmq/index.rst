Asynchronous tasks using Django, Celery and RabbitMQ
###############################################################

:tags: prezentari
:registration:
    meetup.com: https://www.meetup.com/RoPython-Bucuresti/events/240190073/
:event-start: 2017-06-28 18:00
:event-duration: 8100s
:event-location: Str. Sevastopol 13-17, Bucharest, Romania


Celery is an asynchronous task queue based on distributed message
passing. It is focused on real-time operations, but supports
scheduling as well. RabbitMQ, is a message broker which is used by
Celery to distribute messages.

Celery is perfectly suited for tasks which will take some time to
execute but we don’t want our requests to be blocked while these tasks
are processed.
Example use cases: sending emails, heavy background processing (eg:
multimedia encoding), sending bulk messages, periodic tasks, complex
concurrent workflows.

**Schedule:**

* 06:00 - Entry. There will be pizza, snacks and beer, courtesy of `Pentalog Bucharest <https://www.pentalog.ro/bucuresti>`_.
* 06:20 - Introduction to asynchronous tasks, Celery (with Django) and RabbitMQ.
* 06:40 - The Architecture of a typical setup.
* 07:00 - short break
* 07:10 - How to implement and consume asynchronous tasks.
* 07:50 - Advanced Tips & Best practices with Celery
* 08:00 - Closing

