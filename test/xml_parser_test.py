#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  installation_process.py
#
#  Copyright 2014 Antergos
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

import os, sys
import logging

logging.basicConfig(level=10)
logger = logging.getLogger(__name__)

parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parentdir)
sys.path.append(os.path.join(parentdir, 'src'))

logger.debug("parentdir: %s" % parentdir)

from installation.xml_parser import XmlParser

def test_parse_editions():

    parser = XmlParser('test/test-editions.xml')

    editions = parser.enabled_editions()

    logger.debug("Editions: %s" % len(editions))

    assert len(editions) == 3

    for counter, edition in enumerate(editions):
        if counter == 0:
            assert edition['name'] == 'gnome'
            assert edition['title'] == 'Gnome3'
            assert 'description' in edition
        elif counter == 1:
            assert edition['name'] == 'cinnamon'
            assert edition['title'] == 'Cinnamon'
        elif counter == 2:
            assert edition['name'] == 'nox'
            assert edition['title'] == 'Base Install'

    # return all editions available
    editions = parser.editions()

    logger.debug("Editions: %s" % len(editions))

    assert len(editions) == 6



def test_packages_edition():

    parser = XmlParser("test/test-editions.xml")

    packages = parser.packages_edition('gnome')

    assert len(packages) == 16

def test_available_userfeatures():

    parser = XmlParser("test/test-editions.xml")

    user_features = parser.available_userfeatures('cinnamon')

    assert len(user_features) == 2

    assert user_features[0]['description'] == 'ArchUserRepository'

    assert user_features[1].get('description', 'EMPTY') == 'EMPTY'

def test_packages_feature():

    parser = XmlParser("test/test-editions.xml")

    packages = parser.packages_feature('filesystems')

    assert len(packages) == 9

    assert packages[0]['name'] == 'btrfs-progs'

    packages = parser.packages_feature('filesystems', {'alias': 'ext2'})

    assert len(packages) == 1

    assert packages[0]['name'] == 'e2fsprogs'
