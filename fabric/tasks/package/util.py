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

"""Utility tasks."""


from fabric.api import env, task, roles, cd, run, put, puts, abort
from fabric.colors import yellow, green

from monitoring.fabric import helpers


@task
@roles('central')
def upload(distribution=None):
    """
    Upload Debian package to central APT repository. This will also register it
    so it is available by apt-get.

    :roles: central
    """
    supported_distributions = (
        'precise',
        'trusty',
    )

    if not distribution:
        abort('Distribution is not known ! Cannot upload. Aborting.')
    else:
        if not distribution in supported_distributions:
            abort('The distribution {} is not supported ! Aborting.'.format(
                distribution))

    env.user = 'aptcentral'
    repository_dir = '/var/www/packages/apt/{}'.format(distribution)

    # Check old versions and clean if necessary
    for package in helpers.get_package_list():
        # Do not delete old packages ! Keep history in case of...
        with cd(repository_dir):
            num_old_version = int(run('find . -name \'{0}_*_*.deb\' | \\'
                                      'wc -l'.format(package)))

            # Keep latest 5 old versions of a package
            if num_old_version > 4:
                puts(yellow('Deleting old release...'))
                num_to_delete = num_old_version - 4
                run('ls -t1 {0}_*_*.deb | \\'
                    'tail -{1} | \\'
                    'xargs rm -v'.format(package, num_to_delete))

        # Upload new package(s)
        puts(green('Uploading new package to central APT repository...'))
        put('pkg-build/{}_*.deb'.format(package), repository_dir)

    # Generate Release and sign it
    puts(green('Signing release file for APT usage...'))
    with cd(repository_dir):
        run('dpkg-scanpackages -m . > Packages')
        run('apt-ftparchive release . > Release')
        run('gpg -u Monitoring --yes --output Release.gpg -ba Release')