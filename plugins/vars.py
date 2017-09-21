from pelican import signals



def categories(generator):
    generator.context['category_slugs'] = generator.settings['CATEGORY_SLUGS']
    generator.context['tag_names'] = generator.settings['TAG_NAMES']


def register():
    signals.generator_init.connect(categories)
