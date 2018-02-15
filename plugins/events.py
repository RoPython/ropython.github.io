# -*- coding: utf-8 -*-
"""
events plugin for Pelican
=========================

This plugin looks for and parses an "events" directory and generates
blog posts with a user-defined event date. (typically in the future)
It also generates an ICalendar v2.0 calendar file.
https://en.wikipedia.org/wiki/ICalendar


Author: Federico Ceratto <federico.ceratto@gmail.com>
Released under AGPLv3+ license, see LICENSE
"""

from datetime import datetime, timedelta

from icalendar import vDatetime
from pelican import signals, utils
from collections import namedtuple, defaultdict
import icalendar
import logging
import os.path
import pytz

log = logging.getLogger(__name__)

TIME_MULTIPLIERS = {
    'w': 'weeks',
    'd': 'days',
    'h': 'hours',
    'm': 'minutes',
    's': 'seconds'
}

events = []
localized_events = defaultdict(list)
Event = namedtuple("Event", "dtstart dtend metadata")


def parse_tstamp(ev, field_name):
    """Parse a timestamp string in format "YYYY-MM-DD HH:MM"

    :returns: datetime
    """
    try:
        return datetime.strptime(ev[field_name], '%Y-%m-%d %H:%M')
    except Exception as e:
        log.error("Unable to parse the '%s' field in the event named '%s': %s" % (field_name, ev['title'], e))
        raise


def parse_timedelta(ev):
    """Parse a timedelta string in format [<num><multiplier> ]*
    e.g. 2h 30m

    :returns: timedelta
    """

    chunks = ev['duration'].split()
    tdargs = {}
    for c in chunks:
        try:
            m = TIME_MULTIPLIERS[c[-1]]
            val = int(c[:-1])
            tdargs[m] = val
        except KeyError:
            log.error("""Unknown time multiplier '%s' value in the \
'duration' field in the '%s' event. Supported multipliers \
are: '%s'.""" % (c, ev['title'], ' '.join(TIME_MULTIPLIERS)))
            raise RuntimeError("Unknown time multiplier '%s'" % c)
        except ValueError:
            log.error("""Unable to parse '%s' value in the 'duration' \
field in the '%s' event.""" % (c, ev['title']))
            raise ValueError("Unable to parse '%s'" % c)
    return timedelta(**tdargs)


def generate_ical_file(generator, **_):
    """Generate an iCalendar file
    """
    ics_fname = generator.settings['PLUGIN_EVENTS']['ics_fname']
    if not ics_fname:
        return

    ics_fname = os.path.join(generator.settings['OUTPUT_PATH'], ics_fname)
    log.debug("Generating calendar at %s with %d events" % (ics_fname, len(events)))

    tz = generator.settings.get('TIMEZONE', 'UTC')
    tz = pytz.timezone(tz)
    siteurl = "%s/{}" % generator.settings['SITEURL']

    ical = icalendar.Calendar()
    ical.add('prodid', generator.settings['SITENAME'])
    ical.add('version', '2.0')

    for article in generator.articles:
        if 'start' not in article.metadata:
            continue

        dtstart = tz.localize(parse_tstamp(article.metadata, 'start')).astimezone(pytz.UTC)
        dtdelta = parse_timedelta(article.metadata)
        dtend = dtstart + dtdelta
        ie = icalendar.Event(
            summary=article.title,
            dtstart=vDatetime(dtstart),
            dtend=vDatetime(dtend),
            priority=5,
            uid=article.url,
            url=siteurl.format(article.url),
            location=article.metadata['location'],
        )
        ie.add('description', article.content, {'altrep': siteurl.format(article.url)})
        ie.add('x-alt-desc', article.content, {'fmttype': 'text/html'})
        ical.add_component(ie)

    with open(ics_fname, 'wb') as f:
        f.write(ical.to_ical())


def register():
    signals.article_writer_finalized.connect(generate_ical_file)


