#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  installation_process.py
#
#  Copyright 2013 Antergos
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.

import logging
import os
import urllib.request
import urllib.error

def load_xml_file(params):

# 'http://install.antergos.com/packages-%s.xml'

    if len(params['alternate_package_list']) > 0:
        packages_xml = params['alternate_package_list']
    else:
        # The list of packages is retrieved from an online XML to let us
        # control the pkgname in case of any modification
        logging.info(_("Getting package list..."))

        try:
            url =  params['CNCHI_EDITION_URL'] % params['CNCHI_VERSION']
            packages_xml = urllib.request.urlopen(url, timeout=5)
        except urllib.error.URLError as err:
            # If the installer can't retrieve the remote file, try to install with a local
            # copy, that may not be updated
            logging.warning(err)
            logging.debug(_("Can't retrieve remote package list, using a local file instead."))
            data_dir = params['settings'].get("data")
            packages_xml = os.path.join(data_dir, 'editions.xml')

    return packages_xml


