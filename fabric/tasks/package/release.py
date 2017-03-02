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

"""Tasks to release a new version."""

from fabric import helpers

from fabric.api import *
from fabric.colors import *
from fabric.contrib.console import confirm

from fabric import git

from semantic_version import Version


@task
def new(version_string=None):
    """
    Release a brand new package version or specified.

    If ``version_string`` is None, this may be because this is the first
    release.

    :param version_string: this is the version to release (eg. 1.0.5)
    :type version_string: str
    """
    from .build import build
    import util

    # Ensure that all tags are downloaded from remote
    git.fetch()

    version = None
    distribution = helpers.get_distribution_name()

    try:
        if version_string:
            version = Version(version_string)
        else:
            if git.has_tag():
                abort('You must specify a new version !')
            else:
                version = helpers.get_last_version()
    except ValueError:
        abort('The version specified \'%s\' is not Semantic Versioning !' %
              version_string)

    puts(green(
        'Releasing a new package: v{0} for {1}.'.format(
            version, distribution), bold=True))

    # Exit if specified version already exist
    if version_string and git.has_tag(str(version)):
        abort('Error: version \'%s\' already exist !' % version)

    # Clean working copy
    local('make distclean')

    # Create the version in changelog if tags are found
    if version_string and git.has_tag():
        helpers.new_version(str(version))

    # Tag the release
    if not git.has_tag(str(version)):
        helpers.tag()

    # Build package
    build()

    # Confirm before pushing centrally
    # Summary of changes
    puts('\n\nYou are about to push package(s): {}'.format(", ".join(
        helpers.get_package_list())))
    puts('The new version is: {}'.format(version))
    puts('The target distribution is: {}'.format(distribution))

    answer = confirm(red(
        'Last chance before pushing centrally, are you ready ?',
        bold=True), default=False)
    if not answer or answer == 'no':
        puts(yellow('Deleting local tag.'))
        local('git tag -d {}'.format(version))
        abort('Aborting. Pushing is cancelled.')
    else:
        # Push commits and DEB package
        git.push()
        execute(util.upload, distribution)


@task
def major(level=None):
    """
    Release a major version for this package. Increase the first part of the
    version number by 1 or by ``level`` if specified.

    Use this for cases when the project has completly changed !

    :param level: set the major level to this number.
    :type level: int
    """
    # Stop if project has no tags
    if not git.has_tag():
        abort('You should use package.release.new() task as it seems there is'
              ' no version yet !')

    # Get the last released version from changelog
    last_released_version = helpers.get_last_version()
    puts(cyan('Last released version is %s.' % last_released_version))

    # Make a new version
    new_version = Version(str(last_released_version))

    if level:
        new_version.major = int(level)
    else:
        new_version.major += 1

    # Reset others
    new_version.minor = 0
    new_version.patch = 0
    new_version.build = None

    # Call new to init the full process
    execute(new, str(new_version))


@task
def minor(level=None):
    """
    Release a minor version for this package. Increase the middle part of the
    version number by 1 or by ``level`` if specified.

    :param level: set the minor level to this number.
    :type level: int
    """
    # Stop if project has no tags
    if not git.has_tag():
        abort('You should use package.release.new() task as it seems there is'
              ' no version yet !')

    # Get the last released version from changelog
    last_released_version = helpers.get_last_version()
    puts(cyan('Last released version is %s.' % last_released_version))

    # Make a new version
    new_version = Version(str(last_released_version))

    if level:
        new_version.minor = int(level)
    else:
        new_version.minor += 1

    # Reset others
    new_version.patch = 0
    new_version.build = None

    # Call new to init the full process
    execute(new, str(new_version))


@task
def patch(level=None):
    """
    Release a patch for this package. Increase the last part of the version
    number by 1 or by ``level`` if specified.

    :param level: set the patch level to this number.
    :type level: int
    """
    # Stop if project has no tags
    if not git.has_tag():
        abort('You should use package.release.new() task as it seems there is'
              ' no version yet !')

    # Get the last released version from changelog
    last_released_version = helpers.get_last_version()
    puts(cyan('Last released version is %s.' % last_released_version))

    # Make a new version
    new_version = Version(str(last_released_version))

    if level:
        new_version.patch = int(level)
    else:
        new_version.patch += 1

    # Reset others
    new_version.build = None

    # Call new to init the full process
    execute(new, str(new_version))
