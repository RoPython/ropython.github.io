import json

from docutils.parsers.rst import directives, Directive
from docutils import nodes


class GithubRepo(Directive):
    """ Embed Github Gist Snippets in rst text

        GIST_ID and FILENAME are required.

        Usage:
          .. gist:: GIST_ID FILENAME

    """

    required_arguments = 2
    has_content = True

    def run(self):
        self.assert_has_content()
        user = self.arguments[0]
        name = self.arguments[1]

        element = nodes.paragraph()
        self.state.nested_parse(self.content, self.content_offset, element)

        return [
            nodes.raw(text="""
    <div class="gh-repo">
        <div class="gh-title">
            <a href="%(url)s">%(name)s</a>
            <span id="ghrepo-%(user)s-%(name)s"></span>
            <script>jQuery(function($){
                $("#ghrepo-%(user)s-%(name)s").GitHubButton(%(json)s);
            });</script>
        </div>""" % {
            'url': 'https://github.com/%s/%s' % (user, name),
            'name': name,
            'user': user,
            'json': json.dumps(dict(owner=user, repo=name, text='Star', errorText='?')),
            'description': '\n'.join(self.content)
        }, format='html'),
            element,
            nodes.raw(text="</div>", format='html')
        ]


def register():
    directives.register_directive('ghrepo', GithubRepo)
