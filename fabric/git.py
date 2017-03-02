# -*- coding: utf-8 -*-
# Copyright (C) Canux CHENG <canuxcheng@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Manipulate Git repository."""

from fabric.api import *


def fetch(all_remotes=False):
    """
    Fetch remote repository for changes. Can check all remotes.

    :param all_remotes: set it to True if all remotes should be fetched.
    :type all_remotes: bool
    """
    if all_remotes:
        local('git fetch --all')
    else:
        local('git fetch origin')


def push():
    """Push all commits and tags from master branch to origin."""
    local('git push origin master --tags')


def has_tag(tagname=None):
    """
    Check if a tag is found with ``tagname`` or if none specified check if
    project have at least one tag.

    :param tagname: specify the tag that should be checked for existence.
    :type tagname: str
    :return: True if specified tag exists or the project has tags. False
    otherwise.

    >>> has_tag('1.0.0')
    True
    >>> has_tag('1.0')
    False
    >>> has_tag()
    True
    """
    import subprocess
    import traceback

    try:
        if tagname:
            t = subprocess.call(['git', 'show-ref', '-q', '--tags', tagname])
            return True if t == 0 else False
        else:
            t = int(subprocess.check_output('git tag | wc -l', shell=True))
            return True if t > 0 else False
    except:
        print "Exception raised:\n%s" % traceback.format_exc()
        abort('Error: not able to check if project have tags !')

