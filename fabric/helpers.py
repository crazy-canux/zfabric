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

"""Helpers functions."""

import subprocess

from fabric.api import local, abort


def package_has_upstream():
    """
    Test if the package has a upstream source by looking if pristine-tar branch
    exists in remote origin.

    :rtype: bool
    """
    try:
        subprocess.check_call(
            'git ls-remote --exit-code '
            'origin refs/heads/pristine-tar 2>&1 >/dev/null',
            shell=True)
        return True
    except subprocess.CalledProcessError:
        return False


def get_package_list():
    """
    Get the names of all generated deb packages.

    :return: the list of package names.
    :rtype: list(str)
    """
    names = local('dh_listpackages', capture=True)
    return names.splitlines()


def tag():
    """
    Tag package version.
    """
    local("git-buildpackage --git-tag-only")


def new_version(version):
    """
    Create a new version and update changelog.

    :param version: version to create (eg. 1.0.5)
    :type version: str
    """
    from semantic_version import Version

    # Make a new version
    new_release = Version(version)

    # Get the last released version from changelog
    last_released_version = get_last_version()

    if new_release > last_released_version:
        local('git-dch -R -N {0}'.format(version))
        local('git commit debian/changelog \\'
              '-m \'Update changelog for %s release.\'' % version)
    else:
        abort('New version \'%s\' precedes last released version \'%s\' !' %
              (new_release, last_released_version))


def get_last_version():
    """
    Get the last version from the changelog and return it as a
    :class:`Version` instance.

    :return: :class:`Version` instance.
    :rtype: Version
    """
    import re
    from semantic_version import Version

    version_regex = r'[a-zA-Z0-9\-]+\s\((?P<version>.*)\)'
    version_line = local('head -1 debian/changelog', capture=True)
    version_match = re.match(version_regex, version_line)

    if version_match:
        match_groups = version_match.groupdict()
        version = Version(match_groups['version'])
        return version
    else:
        raise StandardError('Not able to find a suitable version for this '
                            'project !')


def get_distribution_name():
    """
    Get the package distribution used to upload in right repository.

    :return: distribution name (like precise, trusty, ...)
    :rtype: str, unicode

    >>> get_distribution_name() in ('trusty', 'precise')
    True
    """
    distrib = subprocess.check_output(
        "head -1 debian/changelog | cut -d';' -f1 | awk '{print $3}'",
        shell=True)
    return distrib.strip()