#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Convert an RST file to HTML suitable for posting to the PSF blog.
"""

import codecs
import optparse
import string
import subprocess
import tempfile

from rst2marsedit.rst2post import format_post
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
    title, content, parsed_tags = format_post(rst_file)
    tags = [t.encode('ascii')
            for t in parsed_tags + options.tags
            ]

    # Save the body to a file so the AppleScript can read it.
    f = tempfile.NamedTemporaryFile(mode='w', suffix='.html')
    try:
        out = codecs.getwriter('utf-8')(f)
        out.write(content)
        f.flush()

        # Build the AppleScript file from the template
        script_file = tempfile.NamedTemporaryFile(mode='w',
                                                  suffix='.applescript',
                                                  )
        try:
            script_template = string.Template(
                pkg_resources.resource_string(__name__, SCRIPT_TEMPLATE_NAME)
                )

            if options.blog:
                blog_instruction = 'set current weblog of document 1 to weblog "%s"' % options.blog
            else:
                blog_instruction = ''

            script_body = script_template.safe_substitute(
                categories=', '.join('"%s"' % t for t in tags),
                blog_instruction=blog_instruction,
                )
            script_file.write(script_body)
            script_file.flush()

            # Open a new blog entry in MarsEdit
            mars = subprocess.Popen(
                ['osascript', script_file.name, f.name, title],
                )
            mars.communicate()
        finally:
            script_file.close()
    finally:
        f.close()
    return


if __name__ == '__main__':
    main()
