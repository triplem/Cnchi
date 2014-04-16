#!/usr/bin/python
# -*- coding: UTF-8 -*-
#
# Copyright (c) 2012 Canonical Ltd.
# Copyright (c) 2013 Antergos
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import src.canonical.misc as misc

# Some of these tmp files are created with sudo privileges
# (this should be fixed) meanwhile, we need sudo privileges to remove them
@misc.raise_privileges
def remove_temp_files(delete_log=False):
    """ Remove Cnchi temporary files """
    temp_files = [".setup-running", ".km-running", "setup-pacman-running",
                  "setup-mkinitcpio-running", ".tz-running", ".setup",
                  ".editions.xml"]

    if delete_log:
        temp_files.append("Cnchi.log")

    for temp in temp_files:
        path = os.path.join("/tmp", temp)
        if os.path.exists(path):
            os.remove(path)