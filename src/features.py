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
import desktop_environments as desktops
import canonical.misc as misc

_next_page = "installation_ask"
_prev_page = "desktop"

class Features(Gtk.Box):
    """ Features screen class """
    def __init__(self, params):
        """ Initializes features ui """
        self.header = params['header']
        self.ui_dir = params['ui_dir']
        self.settings = params['settings']
        self.forward_button = params['forward_button']
        self.backwards_button = params['backwards_button']

        super().__init__()

        self.ui = Gtk.Builder()
        self.ui.add_from_file(os.path.join(self.ui_dir, "features.ui"))
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

        # The first time we load this screen, we try to guess some defaults
        self.defaults = True

        # Only show ufw rules and aur disclaimer info once
        self.info_already_shown = { "ufw":False, "aur":False }

        super().add(self.ui.get_object("features"))

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
            switch.props.valign = Gtk.Align.CENTER
            if 'tooltip' in feature:
                switch.set_tooltip_markup(txt)

            box.pack_end(switch, False, True, 0)

    def translate_ui(self):
        """ Translates features ui """
        edition_name = self.settings.get('edition')
        print('edition_name {}'.format(edition_name))
        edition = self.parser.edition(edition_name)

        # TODO we need to translate all userfeatures, not only those which to belong to the
        # TODO given edition.

        user_features = self.parser.enabled_userfeatures()

        for feature in user_features:
            tooltip = None
            if 'tooltip' in feature.keys:
                tooltip = feature['tooltip']

            self.translate_ui_from_data(feature['name'], feature['title'], feature['description'], tooltip)

        # Sort listbox items
        self.listbox.invalidate_sort()

    def translate_ui_from_data(self, name, title, description, tooltip):
        # Firewall
        txt = _(title)
        txt = "<span weight='bold' size='large'>%s</span>" % txt
        self.titles[name].set_markup(txt)
        txt = _(description)
        txt = "<span size='small'>%s</span>" % txt
        self.labels[name].set_markup(txt)

        if tooltip:
            txt = _(tooltip)
            self.titles[name].set_tooltip_markup(txt)
            self.switches[name].set_tooltip_markup(txt)
            self.labels[name].set_tooltip_markup(txt)


    def hide_features(self):
        """ Hide unused features """
        for feature in self.all_features:
            if feature not in self.features:
                name = feature + "-row"
                obj = self.ui.get_object(name)
                obj.hide()

    def enable_defaults(self):
        """ Enable some features by default """
        if 'bluetooth' in self.features:
            process1 = subprocess.Popen(["lsusb"], stdout=subprocess.PIPE)
            process2 = subprocess.Popen(["grep", "-i", "bluetooth"], stdin=process1.stdout, stdout=subprocess.PIPE)
            process1.stdout.close()
            out, err = process2.communicate()
            if out.decode() is not '':
                logging.debug(_("Detected bluetooth device. Enabling by default..."))
                self.switches['bluetooth'].set_active(True)

        if 'firewall' in self.features:
            self.switches['firewall'].set_active(True)

        if 'cups' in self.features:
            self.switches['cups'].set_active(True)

    def store_values(self):
        """ Get switches values and store them """
        for feature in self.features:
            isactive = self.switches[feature].get_active()
            self.settings.set("feature_" + feature, isactive)
            if isactive:
                logging.debug(_("Selected '%s' feature to install"), feature)

        # Show ufw info message if ufw is selected (only once)
        if self.settings.get("feature_firewall") and not self.info_already_shown["ufw"]:
            info = self.show_info_dialog("ufw")
            self.info_already_shown["ufw"] = True

        # Show AUR disclaimer if AUR is selected (only once)
        if self.settings.get("feature_aur") and not self.info_already_shown["aur"]:
            info = self.show_info_dialog("aur")
            self.info_already_shown["aur"] = True

        return True

    def show_info_dialog(self, feature):
        """ Some features show an information dialog when this screen is accepted """
        if feature == "aur":
            # Aur disclaimer
            txt1 = _("Arch User Repository - Disclaimer")
            txt2 = _("The Arch User Repository is a collection of user-submitted PKGBUILDs\n" \
                "that supplement software available from the official repositories.\n\n" \
                "The AUR is community driven and NOT supported by Arch or Antergos.\n")
        elif feature == "ufw":
            # Ufw rules info
            txt1 = _("Uncomplicated Firewall will be installed with these rules:")
            toallow = misc.get_network()
            txt2 = _("ufw default deny\nufw allow from %s\nufw allow Transmission\nufw allow SSH") % toallow

        txt1 = "<big>%s</big>" % txt1
        txt2 = "<i>%s</i>" % txt2

        info = Gtk.MessageDialog(transient_for=None,
                                 modal=True,
                                 destroy_with_parent=True,
                                 message_type=Gtk.MessageType.INFO,
                                 buttons=Gtk.ButtonsType.CLOSE)
        info.set_markup(txt1)                                        
        info.format_secondary_markup(txt2)
        info.run()
        info.destroy()

    def get_prev_page(self):
        return _prev_page

    def get_next_page(self):
        return _next_page

    def prepare(self, direction):
        """ Prepare features screen to get ready to show itself """
        edition = self.settings.get('edition')

        print("fetching userfeatures for {}".format(edition))

        self.features = self.parser.available_userfeatures(edition)

        print("fetched {} userfeatures".format(len(self.features)))

        self.set_features()

#        self.translate_ui()
        self.show_all()
#        self.hide_features()
#        if self.defaults:
#            self.enable_defaults()
#            self.defaults = False

