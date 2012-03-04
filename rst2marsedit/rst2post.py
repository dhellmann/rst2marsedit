#!/usr/bin/env python
# encoding: utf-8
"""Convert an RST file to HTML suitable for posting to a blogger blog.

Requires BeautifulSoup 3.0.8.1 and docutils.

If you're a Mac user, see also http://pypi.python.org/pypi/rst2marsedit
"""

from pyquery import PyQuery

from docutils.core import publish_string
from docutils.parsers import rst


class TagsDirective(rst.Directive):
    """Directive for specifying the tags or categories for a post.
    """
    name = 'tags'
    has_content = True

    def run(self):
        # Save the tags back to the document settings so the code that
        # calls the parser can use the values.
        tags = self.state.document.settings.tags
        tags.extend(' '.join(self.content).split())
        return []


rst.directives.register_directive('tags', TagsDirective)


def format_post(rst_file, initial_header_level=4):
    """Read the rst file and return a tuple containing the title and
    an HTML string for the post.
    """
    with open(rst_file, 'r') as f:
        body = f.read()
    return format_post_from_string(body, initial_header_level)


def format_post_from_string(body, initial_header_level=4):
    """Returns a tuple containing the title and an HTML string for the
    post body.
    """
    tags = []
    try:
        html = publish_string(
            body,
            writer_name='html',
            settings_overrides={'initial_header_level': initial_header_level,
                                'generator': False,
                                'traceback': True,
                                'tags': tags,
                                },
            )
        if not html:
            raise ValueError('No HTML produced by docutils')
    except Exception as err:
        raise RuntimeError('Could not convert input file to HTML: %s' % err)

    # Pull out the body of the HTML to make the blog post,
    # removing the H1 element with the title.
    d = PyQuery(html, parser='html')
    title = d('body').find('h1:first').html()
    d('body').find('h1:first').remove()
    content = d('body').html()
    return title, content, tags
