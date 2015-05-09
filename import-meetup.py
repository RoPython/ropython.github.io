from __future__ import unicode_literals

import io
import os
import subprocess
import tempfile
from cStringIO import StringIO
from glob import glob
from datetime import datetime
from pprint import pformat


import click
from cachecontrol import CacheControl
from cachecontrol.caches import FileCache
from cachecontrol.heuristics import ExpiresAfter
from html2rest import html2rest
from pelican.utils import slugify
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.shortcuts import get_input
from requests import Session


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
def main(group_id, location, time_boundary, event_status, pandoc):
    key_path = os.path.normpath(os.path.expanduser('~/.meetup.com-key'))
    if os.path.exists(key_path):
        with open(key_path) as fh:
            key = fh.read().strip()

    cache = FileCache('.web_cache', forever=True)
    requests = CacheControl(
        Session(), cache,
        cache_etags=False,
        heuristic=ExpiresAfter(days=1)
    )

    while True:
        resp = requests.get('https://api.meetup.com/status', params=dict(key=key))
        if resp.status_code == 200:
            break
        elif resp.status_code == 401:
            click.echo('Your meetup.com key is required. You can get it from https://secure.meetup.com/meetup_api/key/\n')

            if click.confirm('Open https://secure.meetup.com/meetup_api/key/ in your web browser?'):
                click.launch('https://secure.meetup.com/meetup_api/key/')

            click.echo('')
            key = click.prompt('Key', hide_input=True)
        else:
            click.fail('Failed to get meetup.com status. Response was {!r}'.format(resp.text))

    click.secho('For convenience your key is saved in `{}`.\n'.format(key_path), fg='magenta')
    with open(key_path, 'w') as fh:
        fh.write(key)

    while not location:
        location = location or get_input('Location: ', completer=WordCompleter(['cluj', 'iasi', 'timisoara'], ignore_case=True))

    while True:
        group_id = group_id or get_input('Group ID: ', completer=WordCompleter(['Cluj-py', 'RoPython-Timisoara'], ignore_case=True))

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
            click.secho('Invalid group `{}`. Response was [{}] {!r}'.format(group_id, resp.status_code, resp.text), fg='red')

    # click.echo(pformat(dict(resp.headers)))

    for event in json['results']:
        dt = datetime.fromtimestamp(event['time']/1000)
        click.echo("{}: {}".format(
            dt.strftime('%Y-%m-%d %H:%M:%S'),
            event['name']
        ))
        existing_path = glob(os.path.join('content', '*', dt.strftime('%Y-%m-%d*'), 'index.rst'))
        if existing_path:
            if len(existing_path) > 1:
                click.secho('\tERROR: multiple paths matched: {}'.format(existing_path))
            else:
                click.secho('\t`{}` already exists. Not importing.'.format(*existing_path), fg='yellow')
        else:
            target_dir = os.path.join('content', location, '{}-{}'.format(dt.strftime('%Y-%m-%d'), slugify(event['name'])))
            target_path = os.path.join(target_dir, 'index.rst')
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)

            if pandoc:
                with tempfile.NamedTemporaryFile(delete=False) as fh:
                    fh.write(event['description'].encode('utf-8'))
                rst = subprocess.check_output(['pandoc', '--from=html', '--to=rst', fh.name]).decode('utf-8')
                print fh.name
                #os.unlink(fh.name)
            else:
                stream = StringIO()
                html2rest(event['description'].encode('utf-8'), writer=stream)
                rst = stream.getvalue().decode('utf-8')

            with io.open(target_path, 'w', encoding='utf-8') as fh:
                fh.write('''
{name}
###############################################################

:tags: unknown

{rst}'''.format(rst=rst, **event))
            click.secho('\tWrote `{}`.'.format(target_path), fg='green')







if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    main()
