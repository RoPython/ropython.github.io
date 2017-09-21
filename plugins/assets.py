from __future__ import unicode_literals

import logging
import os
import posixpath
from os.path import join

import jinja2
import webassets
from jinja2 import ext
from pelican import signals
from rcssmin import cssmin
from webassets import Environment
from webassets.ext.jinja2 import AssetsExtension
from webassets.filter import Filter, register_filter
from webassets.filter.rjsmin.rjsmin import jsmin

logger = logging.getLogger(__name__)


@jinja2.contextfunction
def asset(ctx, name):
    env = ctx.environment.assets_environment
    bundle = env[name]
    bundle.build()
    return jinja2.Markup(open(os.path.join(env.directory, bundle.output)).read())


class Extension(ext.Extension):
    def __init__(self, environment):
        environment.globals.update(
            asset=asset,
        )
        environment.filters['cssmin'] = cssmin
        environment.filters['jsmin'] = jsmin


def add_jinja2_ext(pelican):
    """Add Webassets to Jinja2 extensions in Pelican settings."""

    if 'JINJA_ENVIRONMENT' in pelican.settings:  # pelican 3.7+
        pelican.settings['JINJA_ENVIRONMENT']['extensions'].append(Extension)
        pelican.settings['JINJA_ENVIRONMENT']['extensions'].append(AssetsExtension)
    else:
        pelican.settings['JINJA_EXTENSIONS'].append(Extension)
        pelican.settings['JINJA_EXTENSIONS'].append(AssetsExtension)


def create_assets_env(generator):
    """Define the assets environment and pass it to the generator."""

    theme_static_dir = generator.settings['THEME_STATIC_DIR']
    static_url = posixpath.join(generator.settings['SITEURL'], theme_static_dir)
    assets_destination = os.path.join(generator.output_path, theme_static_dir)
    generator.env.assets_environment = Environment(assets_destination, static_url)

    if 'ASSET_CONFIG' in generator.settings:
        for item in generator.settings['ASSET_CONFIG']:
            generator.env.assets_environment.config[item[0]] = item[1]

    if 'ASSET_BUNDLES' in generator.settings:
        for name, args, kwargs in generator.settings['ASSET_BUNDLES']:
            generator.env.assets_environment.register(name, *args, **kwargs)

    if 'ASSET_DEBUG' in generator.settings:
        generator.env.assets_environment.debug = generator.settings['ASSET_DEBUG']
    elif logging.getLevelName(logger.getEffectiveLevel()) == "DEBUG":
        generator.env.assets_environment.debug = True

    for path in (generator.settings['THEME_STATIC_PATHS'] + generator.settings.get('ASSET_SOURCE_PATHS', [])):
        full_path = os.path.join(generator.theme, path)
        generator.env.assets_environment.append_path(full_path, static_url)


def register():
    """Plugin registration."""
    if webassets:
        signals.initialized.connect(add_jinja2_ext)
        signals.generator_init.connect(create_assets_env)

        @register_filter
        class RCssMinFilter(Filter):
            name = 'rcssmin'

            def output(self, _in, out, **kwargs):
                out.write(cssmin(_in.read()))

    else:
        logger.warning('`assets` failed to load dependency `webassets`.'
                       '`assets` plugin not loaded.')
