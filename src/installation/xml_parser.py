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

    def enabled_editions(self):
        """
            returns all enabled editions, which can be shown in the installer.
        """
        # if no filter is given, we are just returning all enabled and allowed editions
        filter = {'enabled': 'true', 'showInInstaller': 'true'}

        return self.editions(filter)

    def show_editions(self, filter):
        """
            returns all editions, which can be shown in the installer

            additional filter can be added
        """
        if not filter:
            filter = {}

        filter['showInInstaller': 'true']

        return self.editions(filter)


    def editions(self, filter={}):
        """
            returns all editions, which can be shown in the installer.

            the returned dict has the following fields:

            name - the name of the edition, a required field
            title - the title of the edition, this is an optional field (see xsd)
            description - the description of the edition, this is an option field as well
        """
        editions = []

        for xml_edition in self.tree.findall("{0}editions/{0}edition".format(self.namespace)):
            edition = self.map_edition(xml_edition, filter)

            if edition:
                editions.append(edition)

        return editions

    def edition(self, edition_name):
        """
            returns the edition object for the given edition name
        """
        for xml_edition in self.tree.findall("{0}editions/{0}edition/[@name='{1}']".format(self.namespace, edition_name)):
            edition = self.map_edition(xml_edition, {})

            # there should be just one, return
            return edition


    def map_edition(self, xml_edition, filter):
        """
            maps the given xml_edition to an edition dict.
        """
        edition = {}

        for key in filter.keys():
            if key in xml_edition.attrib:
                value = xml_edition.get(key)
                if filter.get(key) not in value:
                    return None

        edition['name'] = xml_edition.get('name')
        edition['title'] = xml_edition.get('title')

        description = xml_edition.find("{0}description".format(self.namespace))
        if description is not None:
            edition['description'] = description.text.strip()

        return edition

    def packages_edition(self, edition_name, filter={}):
        """
            determines all packages belonging to the given edition.
            if the edition extends another edition, these packages are added to the returned list as well.

            note that we are using findall on the tree,
            there is a guarantee, that each edition name is unique (restricted through the xsd) and with find
            which returns just the first found element is only returning the content (children) of the found
            element, and not the element itself.

            the returned dict is constructed in the method packages
        """
        packages = []

        for xml_edition in self.tree.findall("{0}editions/{0}edition/[@name='{1}']".format(self.namespace, edition_name)):
            if 'extends' in xml_edition.attrib:
                packages.extend(self.packages_edition(xml_edition.get('extends')))

            packages.extend(self.packages(xml_edition, filter))

        return packages

    def enabled_userfeatures(self):
        """
            returns only enabled userfeatures
        """
        # TODO add test
        return self.userfeatures({'enabled':'true'})


    def userfeatures(self, filter={}):
        """
            returns the list of all available userfeatures (for all editions).
        """
        user_features = []

        for xml_user_feature in self.tree.findall("{0}userfeatures/{0}userfeature".format(self.namespace)):
            user_feature = self.map_feature(xml_user_feature, filter)

            if user_feature:
                user_features.append(user_feature)

        return user_features


    def available_userfeatures(self, edition_name, filter={}):
        """
            returns the list of all available userfeatures for a given edition
            and their informations

        """
        user_features = []

        for xml_user_feature_ref in self.tree.findall("{0}editions/{0}edition/[@name='{1}']/{0}userfeatureset/{0}userfeature".format(self.namespace, edition_name)):
            reference = xml_user_feature_ref.get('ref')

            for xml_user_feature in self.tree.findall("{0}userfeatures/{0}userfeature/[@name='{1}']".format(self.namespace, reference)):
                # TODO add filter here as well - make it possible to disable a userfeature without removing it from
                # TODO all userfeaturesets
                user_feature = self.map_feature(xml_user_feature, filter)

            if user_feature:
                user_features.append(user_feature)

        return user_features

    def map_feature(self, xml_feature, filter):
        """
            maps a user_feature or a feature to a dict

            the returned dict has the following fields:

            name - the name of the feature
            title - the title of the feature
            description - the description of the feature
            tooltip - the tooltip of the feature
        """
        # TODO write Test for this method
        for key in filter.keys():
            if key in xml_feature.attrib:
                value = xml_feature.get(key)
                if filter.get(key) not in value:
                    return None

        user_feature = {}
        user_feature['name'] = xml_feature.get('name')
        user_feature['title'] = xml_feature.get('title')
        description = xml_feature.find("{0}description".format(self.namespace))
        tooltip = xml_feature.find("{0}tooltip".format(self.namespace))

        if description is not None:
            user_feature['description'] = description.text.strip()

        if tooltip is not None:
            user_feature['tooltip'] = tooltip.text.strip()

        return user_feature


    def packages_feature(self, feature_name, filter={}):
        """
            Returns the packages included in the given feature

            the returned dict is constructed in the method packages
        """
        packages = []

        for xml_edition in self.tree.findall("{0}features/{0}feature/[@name='{1}']".format(self.namespace, feature_name)):

            packages.extend(self.packages(xml_edition, filter))

        return packages

    def packages_selected_userfeature(self, userfeature_name, filter={}):
        """
            Returns the packages included in the given userfeature

            the returned dict is constructed in the method packages
        """
        packages = []

        for xml_edition in self.tree.findall("{0}userfeatures/{0}userfeature/[@name='{1}']".format(self.namespace, userfeature_name)):

            packages.extend(self.packages(xml_edition, filter))

        return packages


    def packages(self, xml_element, filter={}):
        """
            Determines packages found under the given element

            Elements which do contain an attrib with the same value as given in the filter are
            not added to the result list.

            the returned dict has the following fields:

            name - the name of the edition, a required field
            nm -
            dm -
            conflicts -
        """
        packages = []

        for xml_package in xml_element.findall("{0}pkgname".format(self.namespace)):
            package = self.map_package(xml_package, filter)

            if package:
                packages.append(package)

        return packages

    def map_package(self, xml_package, filter):
        """
            maps the given xml_package to a package dict.

            if the filter can be applied None is returned
        """
        package = {}

        for key in filter.keys():
            if key in xml_package.attrib:
                value = xml_package.get(key)
                if filter.get(key) not in value:
                    return None

        package['name'] = xml_package.text

        if 'nm' in xml_package.attrib:
            package['nm'] = xml_package.get('nm')

        if 'dm' in xml_package.attrib:
            package['dm'] = xml_package.get('dm')

        if 'conflicts' in xml_package.attrib:
            package['conflicts'] = xml_package.get('conflicts')

        if 'alias' in xml_package.attrib:
            package['alias'] = xml_package.get('alias')

        if 'lib' in xml_package.attrib:
            package['lib'] = xml_package.get('lib')

        return package


    def transform_to_boolean(self, element, attrib_name):
        return True if element.get(attrib_name, default='true') == 'true' else False
