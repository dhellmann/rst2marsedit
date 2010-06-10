==============
 rst2marsedit
==============

rst2marsedit is a Python script for converting reStructuredText_ input
to HTML that can be used with the MarsEdit_ blogging tool.

Usage
=====

::

    Usage: rst2marsedit <infile>

Options:

  -h, --help            show this help message and exit
  -b BLOG, --blog=BLOG  The blog name
  -t TAGS, --tag=TAGS   Tag names

For example::

  $ rst2marsedit -t board -b 'Python Software Foundation' 2010-05-10/sprints.rst

produced the post at http://pyfound.blogspot.com/2010/06/psf-sponsored-sprints.html

Installation
============

::

    $ pip install rst2marsedit


.. _reStructuredText: http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html

.. _MarsEdit: http://www.red-sweater.com/marsedit/
