#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  desktop.py
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

""" Desktop screen """

from gi.repository import Gtk, GLib
from operator import itemgetter

import os
import logging
import collections

_next_page = "features"
_prev_page = "keymap"

class DesktopAsk(Gtk.Box):
    """ Class to show the Desktop screen """
    def __init__(self, params):
        self.header = params['header']
        self.ui_dir = params['ui_dir']
        self.forward_button = params['forward_button']
        self.backwards_button = params['backwards_button']
        self.settings = params['settings']

        super().__init__()

        self.ui = Gtk.Builder()
        self.ui.add_from_file(os.path.join(self.ui_dir, "desktop.ui"))

        data_dir = self.settings.get('data')
        self.desktops_dir = os.path.join(data_dir, "images", "desktops")

        self.desktop_info = self.ui.get_object("desktop_info")
        #self.treeview_desktop = self.ui.get_object("treeview_desktop")
        # Set up list box
        self.listbox = self.ui.get_object("listbox_desktop")
        self.listbox.connect("row-selected", self.on_listbox_row_selected)
        self.listbox.set_selection_mode(Gtk.SelectionMode.BROWSE)

        self.ui.connect_signals(self)

        self.edition_choice = 0

        self.set_editions()
        self.set_desktop_list()

        super().add(self.ui.get_object("desktop"))

    def translate_ui(self, id_in_list):
        """ Translates all ui elements """
        print("translate {}".format(id_in_list))

        edition = self.enabled_editions[id_in_list]

        print("name: {}".format(edition['name']))
        print("title: {}".format(edition['title']))
        print("description: {}".format(edition['description']))

        label = self.ui.get_object("desktop_info")
        txt = "<span weight='bold'>%s</span>\n" % edition['title']
        description = edition['description']
        txt += _(description)
        label.set_markup(txt)

        image = self.ui.get_object("image_desktop")
        path = os.path.join(self.desktops_dir, edition['name'] + ".png")
        image.set_from_file(path)

        txt = _("Choose Your Desktop")
        self.header.set_subtitle(txt)

    def prepare(self, direction):
        """ Prepare screen """
        self.translate_ui(self.edition_choice)
        self.show_all()

    def set_desktop_list(self):
        """ Set desktop list in the ListBox """
        for idx, edition in enumerate(self.enabled_editions):
            box = Gtk.VBox()
            label = Gtk.Label()
            label.set_markup(edition['title'])
            label.set_alignment(0, 0.5)
            box.add(label)
            self.listbox.add(box)
            # gnome is always the default edition
            # TODO probably we could make this configurable
            if edition['name'] == 'gnome':
                self.select_default_row(idx)
                self.edition_choice = idx

    def select_default_row(self, id_in_list):
        row = self.listbox.get_row_at_index(id_in_list)
        self.listbox.select_row(row)
        return

    def set_desktop(self, row_id):
        """ Show desktop info """
        self.edition_choice = row_id
        self.translate_ui(row_id)

        return

    def on_listbox_row_selected(self, listbox, listbox_row):
        """ Someone selected a different row of the listbox """
        self.set_desktop(listbox_row.get_index())
    
    def store_values(self):
        """ Store desktop """
        edition = self.enabled_editions(self.edition_choice)
        self.settings.set('edition', edition['name'])
        logging.info(_("Cnchi will install Antergos with the '%s' edition"), edition['name'])
        return True
    
    def scroll_to_cell(self, treeview, path):
        """ Scrolls treeview to show the desired cell """
        treeview.scroll_to_cell(path)
        return False

    def get_prev_page(self):
        return _prev_page

    def get_next_page(self):
        return _next_page

    def set_editions(self):
        """
            returns a sorted dict with all editions associated

            key: name of the edition
            value: the edition itself
        """
        parser = self.settings.get('parser')

        # if we would like to show all editions, use a dummy filter ;-) (kind of crude)
        if self.settings.get('z_hidden'):
            editions = parser.show_editions()
        else:
            editions = parser.enabled_editions()

        self.enabled_editions = sorted(editions, key=itemgetter('title'))
