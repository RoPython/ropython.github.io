from pelican import signals



def categories(generator):
    generator.context['category_slugs'] = generator.settings['CATEGORY_SLUGS']


def register():
    signals.generator_init.connect(categories)