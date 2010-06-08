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
import subprocess
import tempfile

from BeautifulSoup import BeautifulSoup

def main():
    parser = optparse.OptionParser('%prog <infile>')
    options, args = parser.parse_args()

    if not args:
        parser.error('Please specify an input rst file')
    
    rst_file = args[0]

    # Convert RST to HTML
    rst2html = subprocess.Popen(['rst2html.py', '--no-generator', '--initial-header-level=4',
                                 rst_file],
                                stdout=subprocess.PIPE)
    html = rst2html.communicate()[0]
    soup = BeautifulSoup(html)

    # Pull out the body of the HTML to make the blog post,
    # removing the H1 element with the redundant title.
    body = soup.find('body')
    [h1.extract() for h1 in body.findAll('h1')]
    content = ''.join(unicode(c) for c in body.contents).strip()

    # Save the results to a file so the script can read it.
    with tempfile.NamedTemporaryFile('w') as f:
        out = codecs.getwriter('utf-8')(f)
        out.write(content)
        f.flush()

        # Get the title of the article
        title = ''.join(unicode(c) for c in soup.find('title').contents)

        # Find the AppleScript
        bindir = os.path.dirname(__file__)
        scriptname = os.path.join(bindir, 'SendToMarsEdit.applescript')

        # Open a new blog entry in MarsEdit
        mars = subprocess.Popen(['osascript',
                                 scriptname,
                                 f.name,
                                 title,
                                 ])
        mars.communicate()
    return


if __name__ == '__main__':
    main()
