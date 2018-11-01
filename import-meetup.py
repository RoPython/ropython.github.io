import io
import os
import subprocess
import tempfile
try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
from datetime import datetime, timedelta
from glob import glob

import click
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from cachecontrol.heuristics import ExpiresAfter
from creole import html2rest
from pelican.utils import slugify
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import get_input
from requests import Session


def format_duration(duration):
    minutes, seconds = divmod(duration, 60)
    hours, minutes = divmod(minutes, 60)
    out = []
    for val, unit in [
        (hours, 'h'),
        (minutes, 'm'),
        (seconds, 's'),
    ]:
        if val:
            out.append('%s%s' % (val, unit))
    return ' '.join(out)


@click.command()
@click.argument('group-id', required=False)
@click.argument('location', required=False)
@click.option('--time-boundary', '-t', default='-1m,1m',
              help='Time boundary to import (2 deltas separated by comma). Default: -1m,1m (from 1 month in the '
                   'past till 1 month in the future).')
@click.option('--event-status', '-s', default='past',
              type=click.Choice(['past', 'suggested', 'proposed', 'draft', 'cancelled', 'upcoming']),
              help='Event type to import. Default: past.')
@click.option('--pandoc', '-p', is_flag=True, help='Use `pandoc` to convert the event description.')
@click.option('--force', '-f', is_flag=True, help='Override existing files.')
def main(group_id, location, time_boundary, event_status, pandoc, force):
    key_path = os.path.normpath(os.path.expanduser('~/.meetup.com-key'))
    if os.path.exists(key_path):
        with io.open(key_path, encoding='utf8') as fh:
            key = fh.read().strip()
    else:
        key = None
    cache = FileCache('.web_cache', forever=True)
    requests = CacheControl(
        Session(), cache,
        cache_etags=False,
        heuristic=ExpiresAfter(days=1)
    )

    while True:
        resp = requests.get('https://api.meetup.com/status', params=dict(key=key))
        if resp.status_code == 200 and resp.json().get('status') == 'ok':
            break
        elif resp.status_code == 200 and any('auth_fail' == e.code for e in resp.json().get('errors', [])):
            click.echo(
                'Your meetup.com key is required. You can get it from https://secure.meetup.com/meetup_api/key/\n')

            if click.confirm('Open https://secure.meetup.com/meetup_api/key/ in your web browser?'):
                click.launch('https://secure.meetup.com/meetup_api/key/')

            click.echo('')
            key = click.prompt('Key', hide_input=True)
        else:
            raise click.ClickException('Failed to get meetup.com status. Response was {!r} {!r}'.format(resp.status_code, resp.text))

    click.secho('For convenience your key is saved in `{}`.\n'.format(key_path), fg='magenta')
    with open(key_path, 'w') as fh:
        fh.write(key)

    while not location:
        location = location or get_input(u'Location: ', completer=WordCompleter([
            u'cluj', u'iasi', u'timisoara', u'bucuresti'], ignore_case=True))

    while True:
        group_id = group_id or get_input(u'Group ID: ', completer=WordCompleter([
            u'RoPython-Bucuresti', u'RoPython-Cluj', u'RoPython_Iasi', u'RoPython-Timisoara'], ignore_case=True))

        resp = requests.get('https://api.meetup.com/2/events', params=dict(
            key=key,
            group_urlname=group_id,
            time=time_boundary,
            status=event_status,
        ))
        if resp.status_code == 200:
            json = resp.json()
            if json['results']:
                break
            else:
                click.secho('Invalid group `{}`. It has no events!'.format(group_id), fg='red')
                group_id = None
        if resp.status_code == '400':
            click.fail('Failed to get make correct request. Response was {!r}'.format(resp.text))
        else:
            click.secho('Invalid group `{}`. Response was [{}] {!r}'.format(group_id, resp.status_code, resp.text),
                        fg='red')

    # click.echo(pformat(dict(resp.headers)))

    for event in json['results']:
        dt = datetime.fromtimestamp(event['time'] / 1000)
        event['duration'] = format_duration(event.get('duration', 3600000) / 1000)
        event['time'] = dt.strftime('%Y-%m-%d %H:%M')
        click.echo("{time}: {name}".format(**event))
        existing_path = glob(os.path.join('content', '*', dt.strftime('%Y-%m-%d*'), 'index.rst'))
        if existing_path and not force:
            if len(existing_path) > 1:
                click.secho('\tERROR: multiple paths matched: {}'.format(existing_path))
            else:
                click.secho('\t`{}` already exists. Not importing.'.format(*existing_path), fg='yellow')
        else:
            target_dir = os.path.join('content', location,
                                      '{}-{}'.format(dt.strftime('%Y-%m-%d'), slugify(event['name'])))
            target_path = os.path.join(target_dir, 'index.rst')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            if pandoc:
                with tempfile.NamedTemporaryFile(delete=False) as fh:
                    fh.write(event['description'].encode('utf-8'))
                rst = subprocess.check_output(['pandoc', '--from=html', '--to=rst', fh.name]).decode('utf-8')
                os.unlink(fh.name)
            else:
                rst = html2rest(event['description'])

            doc = u'''{name}
###############################################################

:tags: prezentari
:registration:
    meetup.com: {event_url}
:start: {time}
:duration: {duration}
:location: {venue[address_1]}, {venue[city]}, {venue[localized_country_name]}

{rst}'''.format(rst=rst, **event)
            with io.open(target_path, 'w', encoding='utf-8') as fh:
                fh.write(doc)
            click.secho('\tWrote `{}`.'.format(target_path), fg='green')


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.DEBUG)
    main()
