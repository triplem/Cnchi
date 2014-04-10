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

import xml.etree.ElementTree as etree


class XmlParser:

    def __init__(self, file_name):
        self.file_name = file_name

        self.namespace = "{http://antergos.com/cnchi/}"
        self.tree = etree.parse(file_name)


    def editions_installer(self):
        """
            returns all editions, which can be shown in the installer.

            the returned dict has the following fields:

            name - the name of the edition, a required field
            title - the title of the edition, this is an optional field (see xsd)
            description - the description of the edition, this is an option field as well
        """
        editions = []

        for xml_edition in self.tree.findall("{0}editions/{0}edition".format(self.namespace)):

            enabled = self.transform_to_boolean(xml_edition, 'enabled')
            show = self.transform_to_boolean(xml_edition, 'showInInstaller')

            if enabled and show:
                edition = {}
                edition['name'] = xml_edition.get('name')
                edition['title'] = xml_edition.get('title')
                edition['description'] = xml_edition.find('description')

                editions.append(edition)

        return editions

    def packages(self, edition_name):
        """
            determines all packages belonging to the given edition.
            if the edition extends another edition, these packages are added to the returned list as well.

            note that we are using findall on the tree,
            there is a guarantee, that each edition name is unique (restricted through the xsd) and with find
            which returns just the first found element is only returning the content (children) of the found
            element, and not the element itself.

            the returned dict has the following fields:

            name - the name of the edition, a required field
            nm -
            dm -
            conflicts -
        """
        packages = []

        for xml_edition in self.tree.findall("{0}editions/{0}edition/[@name='{1}']".format(self.namespace, edition_name)):
            if 'extends' in xml_edition.attrib:
                packages.extend(self.packages(xml_edition.get('extends')))

            for xml_package in xml_edition.findall("./{0}pkgname".format(self.namespace)):
                package = {}

                package['name'] = xml_package.text

                if 'nm' in xml_package.attrib:
                    package['nm'] = xml_package.get('nm')

                if 'dm' in xml_package.attrib:
                    package['dm'] = xml_package.get('dm')

                if 'conflicts' in xml_package.attrib:
                    package['conflicts'] = xml_package.get('conflicts')

                packages.append(package)

        return packages


    def transform_to_boolean(self, element, attrib_name):
        return True if element.get(attrib_name, default='true') == 'true' else False
