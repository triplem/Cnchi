#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  features.py
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

""" Features screen """

from gi.repository import Gtk
import subprocess
import os
import logging
#import canonical.misc as misc


from gtkbasebox import GtkBaseBox

class Features(GtkBaseBox):
    """ Features screen class """
    def __init__(self, params):
        """ Initializes features ui """
        self.next_page = "installation_ask"
        self.prev_page = "desktop"

        super().__init__(params, "features")

        self.ui.connect_signals(self)

        # Set up list box
        self.listbox = self.ui.get_object("listbox")
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
#        self.listbox.set_sort_func(self.listbox_sort_by_name, None)

        self.parser = self.settings.get('parser')

        # Available features (for reference)
        self.all_features = self.parser.enabled_userfeatures()

        # This is initialized each time this screen is shown in prepare()
        self.features = None

        # All switches
        self.switches = {}

        # The first time we load this screen, we try to guess some defaults
        self.defaults = True

        # Only show disclaimers once, set the name of the feature to True, if it is
        # shown already
        self.info_already_shown = { }

        self.add(self.ui.get_object("features"))

    def listbox_sort_by_name(self, row1, row2, user_data):
        """ Sort function for listbox
            Returns : < 0 if row1 should be before row2, 0 if they are equal and > 0 otherwise
            WARNING: IF LAYOUT IS CHANGED IN features.ui THEN THIS SHOULD BE CHANGED ACCORDINGLY. """
        label1 = row1.get_children()[0].get_children()[1].get_children()[0]
        label2 = row2.get_children()[0].get_children()[1].get_children()[0]

        text = [label1.get_text(), label2.get_text()]
        sorted_text = misc.sort_list(text, self.settings.get("locale"))

        # If strings are already well sorted return < 0
        if text[0] == sorted_text[0]:
            return -1

        # Strings must be swaped, return > 0
        return 1

    def set_features(self):
        """
            Adds all features to the listbox
        """
        edition_name = self.settings.get('edition')
        edition = self.parser.edition(edition_name)

        txt = edition['title'] + " - " + _("Feature Selection")
        self.header.set_subtitle(txt)

        for idx, feature in enumerate(self.features):
            if 'tooltip' in feature:
                txt = _(feature['tooltip'])

            row = Gtk.ListBoxRow()
            self.listbox.add(row)

            box = Gtk.Box()
            row.add(box)

            image = Gtk.Image()
            image.set_property("icon-name", feature['icon-name'])
            image.set_pixel_size(48)
            box.pack_start(image, False, False, 0)

            vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            box.add(vbox)

            title = _(feature['title'])
            title = "<span weight='bold' size='large'>%s</span>" % title
            titleLabel = Gtk.Label(xalign=0, xpad=20)
            titleLabel.set_markup(title)
            if 'tooltip' in feature:
                titleLabel.set_tooltip_markup(txt)
            vbox.add(titleLabel)

            description = _(feature['description'])
            description = "<span size='small'>%s</span>" % description
            descriptionLabel = Gtk.Label(xalign=0, xpad=20)
            descriptionLabel.set_markup(description)
            if 'tooltip' in feature:
                descriptionLabel.set_tooltip_markup(txt)
            vbox.add(descriptionLabel)

            switch = Gtk.Switch()
            switch.set_active(feature['active'])
            self.switches[feature['name']] = feature['active']
            switch.connect("notify::active", self.on_switch_activated, feature['name'])
            switch.props.valign = Gtk.Align.CENTER
            if 'tooltip' in feature:
                switch.set_tooltip_markup(txt)

            box.pack_end(switch, False, True, 0)

    def on_switch_activated(self, switch, active, name):
        if switch.get_active():
            self.switches[name] = True
        else:
            self.switches[name] = False

    def enable_defaults(self):
        """ Enable some features by default """
        # TODO could we put a method name in the active attrib?
        if 'bluetooth' in self.features:
            process1 = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
            process2 = subprocess.Popen(["grep", "-i", "bluetooth"], stdin=process1.stdout, stdout=subprocess.PIPE)
            process1.stdout.close()
            out, err = process2.communicate()
            if out.decode() is not '':
                logging.debug(_("Detected bluetooth device. Enabling by default..."))
                self.switches['bluetooth'].set_active(True)

    def store_values(self):
        """ Get switches values and store them """

        features = []
        for feature_name in self.switches:
            if self.switches[feature_name]:
                features.append(feature_name)
                logging.debug(_("Selected '%s' feature to install"), feature_name)

        self.settings.set("selected_user_features", features)

        self.show_info_dialogs()

        return True

    def show_info_dialogs(self):
        """ Some features show an information dialog when this screen is accepted """
        for feature_name in self.switches:
            if self.switches[feature_name]:
                feature = self.parser.userfeature(feature_name)

                print(feature)

                if feature and 'infobox' in feature.keys() \
                    and ( feature_name not in self.info_already_shown.keys() \
                    or not self.info_already_shown[feature_name]):
                    self.show_info_dialog(feature)

    def show_info_dialog(self, feature):
        infodialog = feature['infobox']
        feature_name = feature['name']

        txt1 = _(infodialog['title'])

        if 'info_method' in infodialog.keys():
            # this import should be made more dynamic as well...
            import hook.feature_hook as feature_hook
            method_to_call = getattr(feature_hook, infodialog['info_method'])

            kwargs = { 'settings': self.settings }

            additional_info = method_to_call(**kwargs)
        else:
            addtional_info = ""

        txt2 = _(infodialog['text']) % additional_info

        txt1 = "<big>%s</big>" % txt1
        txt2 = "<i>%s</i>" % txt2

        self.info_already_shown[feature_name] = True

        info = Gtk.MessageDialog(transient_for=None,
                                 modal=True,
                                 destroy_with_parent=True,
                                 message_type=Gtk.MessageType.INFO,
                                 buttons=Gtk.ButtonsType.CLOSE)
        info.set_markup(txt1)                                        
        info.format_secondary_markup(txt2)
        info.run()
        info.destroy()

    def prepare(self, direction):
        """ Prepare features screen to get ready to show itself """
        edition = self.settings.get('edition')

        self.features = self.parser.available_userfeatures(edition)
        self.set_features()

        self.show_all()

# When testing, no _() is available
try:
    _("")
except NameError as err:
    def _(message): return message

if __name__ == '__main__':
    from test_screen import _,run
    run('Features')
