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

"""Servers Inventory."""

from fabric.api import env
import textwrap


# Inventory
#
_roles = {
    # Operating systems
    "debian": [],
    "ubuntu": [],
    "redhat": [],

    # Groups
    "central": [
        "canuxcheng.com",
    ],
    "satellites": [
        "canuxcheng.com",
    ],
    "workers": [
        "canuxcheng.com",
    ],
    "omnibus": [
        "canuxcheng.com",
    ],
}

# Operating Systems
#
# Ubuntu
_roles["ubuntu"].extend(_roles["central"])
_roles["ubuntu"].extend(_roles["satellites"])
_roles["ubuntu"].extend(_roles["workers"])

# Debian (keep compat with old scripts)
_roles["debian"].extend(_roles["ubuntu"])

# RedHat
_roles["redhat"].extend(_roles["omnibus"])

# Load inventory in shared fabric env
env.roledefs.update(_roles)

#------------------------------------------------------------------------------

# Show some very very very useful information in DEBUG ;-)
if env.get('DEBUG'):
    print "Available server's roles: (specify with -R)\n"

    role_string_length = len(max(env.roledefs.keys(), key=len))
    jitter = 3
    role_string_format = '\033[1;33m{0:%d}:' \
                         '\033[0m {1:80}' % role_string_length

    for role, servers in sorted(env.roledefs.viewitems()):
        print role_string_format.format(
            role, textwrap.fill(
                ", ".join(servers),
                width=80 - role_string_length - jitter,
                subsequent_indent=" " * (role_string_length + jitter)))

    print "\n",
