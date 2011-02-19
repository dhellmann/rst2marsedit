#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Convert an RST file to HTML suitable for posting to the PSF blog.
"""

import codecs
import optparse
import os
import string
import subprocess
import tempfile

from BeautifulSoup import BeautifulSoup
import pkg_resources

SCRIPT_TEMPLATE_NAME = 'SendToMarsEdit.applescript'

def main():
    parser = optparse.OptionParser('%prog <infile>')
    parser.add_option('-b', '--blog',
                      action='store',
                      dest='blog',
                      default="",
                      help='The blog name',
                      )
    parser.add_option('-t', '--tag',
                      action='append',
                      dest='tags',
                      default=[],
                      help='Tag names',
                      )
    options, args = parser.parse_args()

    if not args:
        parser.error('Please specify an input rst file')
    
    rst_file = args[0]

    # Convert RST to HTML
    try:
        rst2html = subprocess.Popen(['rst2html.py', '--no-generator', '--initial-header-level=4',
                                     rst_file],
                                    stdout=subprocess.PIPE)
        html = rst2html.communicate()[0]
        if not html:
            raise ValueError('No HTML produced by rst2html.py')
    except:
        parser.error('Could not convert input file to HTML with rst2html.py')
    soup = BeautifulSoup(html)

    # Pull out the body of the HTML to make the blog post,
    # removing the H1 element with the redundant title.
    body = soup.find('body')
    [h1.extract() for h1 in body.findAll('h1')]
    content = ''.join(unicode(c) for c in body.contents).strip()
                    
    # Get the title of the article
    title = ''.join(unicode(c) for c in soup.find('title').contents)

    # Save the body to a file so the AppleScript can read it.
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.html')
    try:
        out = codecs.getwriter('utf-8')(f)
        out.write(content)
        f.flush()

        # Build the AppleScript file from the template
        script_file = tempfile.NamedTemporaryFile(mode='w', suffix='.applescript')
        try:
            script_template = string.Template(
                pkg_resources.resource_string(__name__, SCRIPT_TEMPLATE_NAME)
                )

            if options.blog:
                blog_instruction = 'set current weblog of document 1 to weblog "%s"' % options.blog
            else:
                blog_instruction = ''

            script_body = script_template.safe_substitute(
                categories = ', '.join('"%s"' % t for t in options.tags),
                blog_instruction = blog_instruction,
                )
            script_file.write(script_body)
            script_file.flush()

            # Open a new blog entry in MarsEdit
            mars = subprocess.Popen(['osascript', script_file.name, f.name, title])
            mars.communicate()
        finally:
            script_file.close()
    finally:
        f.close()
    return


if __name__ == '__main__':
    main()
