# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from os.path import dirname
from os.path import join

from rcssmin import cssmin
from webassets.filter import register_filter, Filter
from webassets.filter.cssrewrite import CSSRewrite
from webassets.filter.datauri import CSSDataUri

AUTHOR = 'Echipa RoPython'
SITENAME = 'RoPython'

REAL_SITEURL = SITEURL = 'https://ropython.ro'
RELATIVE_URLS = False

DISQUS_SITENAME = '?'
GOOGLE_ANALYTICS_ACCOUNT = '?'
GOOGLE_ANALYTICS_DOMAIN = '?'

TIMEZONE = 'Europe/Bucharest'

LOCALE = 'rom', 'ro_RO',
DEFAULT_DATE_FORMAT = '%d %B %Y'
DEFAULT_LANG = 'ro'

FEED_ALL_RSS = 'feeds/all.rss.xml'
TAG_FEED_RSS = 'feeds/%s.rss.xml'

FEED_ALL_ATOM = 'feeds/all.atom.xml'
TAG_FEED_ATOM = 'feeds/%s.atom.xml'

DELETE_OUTPUT_DIRECTORY = True

DEFAULT_PAGINATION = 20

PATH = 'content'
STATIC_PATHS = ['']

THEME = 'theme'

SECTIONS = [
    ('Evenimente', ''),
    ('Locații', 'locatii/'),
    ('Forme', 'forme/'),
    ('Arhivă', 'arhiva/'),
]
THEME_STATIC_DIR = 'static'
THEME_STATIC_PATHS = ['static']
ASSET_SOURCE_PATHS = [join(dirname(__file__), 'theme', 'static')]
ASSET_BUNDLES = [
    ('screen',
     ("style.css", "layout.css", "pygments.css", "print.css", "fonts.css", "fontello-embedded.css"),
     dict(filters=[CSSDataUri(max_size=10240), "cssrewrite", "rcssmin"], output="all-min.css")),
    ('print', ("print.css",), dict(filters="rcssmin", output="print-min.css")),
    ('js', ("modernizr.js",), dict(filters="rjsmin", output="min.js")),
]
ASSET_CONFIG = {
    'auto_build': True
}

TAG_CLOUD_STEPS = 6
# TYPOGRIFY = True

PLUGIN_PATHS = ['plugins']
PLUGINS = (
    'sitemap',
    'headerid',
    'assets',
    'vars',
    'events',
)
SITEMAP = {
    'format': 'xml',
    'priorities': {
        'articles': 0.5,
        'indexes': 0.5,
        'pages': 0.5
    },
    'changefreqs': {
        'articles': 'monthly',
        'indexes': 'daily',
        'pages': 'monthly'
    }
}

TEMPLATE_PAGES = {
    'drafts.html': 'drafts/index.html'
}
# READERS = {'html': None}

FILENAME_METADATA = r'(?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)'
PATH_METADATA = r'(?P<category>[^/\\]+)[/\\](?P<date>\d{4}-\d{2}-\d{2})-(?P<slug>.*)[/\\]'

ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

YEAR_ARCHIVE_URL = '{date:%Y}/'
YEAR_ARCHIVE_SAVE_AS = '{date:%Y}/index.html'

MONTH_ARCHIVE_URL = '{date:%Y}/{date:%m}/'
MONTH_ARCHIVE_SAVE_AS = '{date:%Y}/{date:%m}/index.html'

PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

TAG_URL = 'forma/{slug}/'
TAG_SAVE_AS = 'forma/{slug}/index.html'

TAGS_URL = 'forme/'
TAGS_SAVE_AS = 'forme/index.html'

ARCHIVES_URL = 'arhive/'
ARCHIVES_SAVE_AS = 'arhive/index.html'

AUTHOR_URL = 'organizator/{slug}/'
AUTHOR_SAVE_AS = 'organizator/{slug}/index.html'

CATEGORY_URL = '{slug}/'
CATEGORY_SAVE_AS = '{slug}/index.html'
CATEGORIES_SAVE_AS = 'locatii/index.html'
USE_FOLDER_AS_CATEGORY = False
DEFAULT_CATEGORY = 'national'
CATEGORY_SLUGS = {  # this is custom setting, not a Pelican setting
    'cluj': 'Cluj-Napoca',
    'timisoara': 'Timișoara',
    'iasi': 'Iași',
    'baia-mare': 'Baia Mare',
    'bucuresti': 'București',
    'national': 'Național',
}
TAG_NAMES = {  # this is custom setting, not a Pelican setting
    'intalniri': 'Întâlniri',
    'conferinta': 'Conferință',
    'prezentari': 'Prezentări',
    'workshop': 'Atelier',
}

DIRECT_TEMPLATES = (
    'index',
    # 'forme',
    # 'arhiva',
    '404'
)

PAGINATION_PATTERNS = (
    (1, '{base_name}/', '{base_name}/index.html'),
    (2, '{base_name}/page-{number}/', '{base_name}/page-{number}/index.html'),
)

CACHE_PATH = '.cache'

READERS = {'html': None}  # Nu procesa fisierele .html ca si articole

EXTRA_PATH_METADATA = {
    'CNAME': {'path': 'CNAME'},
}
PLUGIN_EVENTS = {
    'ics_fname': 'calendar.ics',
}
