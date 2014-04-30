#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  welcome.py
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

from gi.repository import Gtk, Gdk
import subprocess, sys, os
import gettext
import os
import logging
import sys

from show_message import warning

from gtkbasebox import GtkBaseBox

# Import functions
import src.canonical.utils as utils

try:
    import src.info as info
except ImportError:
    import info


class Welcome(GtkBaseBox):
    def __init__(self, params):
        self.disable_tryit = params['disable_tryit']

        self.next_page = "language"
        self.prev_page = None

        super().__init__(params, "welcome")

        self.ui.connect_signals(self)

        data_dir = self.settings.get('data')
        welcome_dir = os.path.join(data_dir, "images", "welcome")

        self.label = {}
        self.label['welcome'] = self.ui.get_object("welcome_label")
        self.label['info'] = self.ui.get_object("infowelcome_label")

        self.button = {}
        self.button['tryit'] = self.ui.get_object("tryit_button")
        self.button['cli'] = self.ui.get_object("cli_button")
        self.button['graph'] = self.ui.get_object("graph_button")

        self.image = {}
        self.image['tryit'] = self.ui.get_object("tryit_image")
        self.image['cli'] = self.ui.get_object("cli_image")
        self.image['graph'] = self.ui.get_object("graph_image")

        self.filename = {}
        self.filename['tryit'] = os.path.join(welcome_dir, "tryit-icon.png")
        self.filename['cli'] = os.path.join(welcome_dir, "cliinstaller-icon.png")
        self.filename['graph'] = os.path.join(welcome_dir, "installer-icon.png")

        for key in self.image:
            self.image[key].set_from_file(self.filename[key])

        self.translate_ui()

        self.set_name("welcome")

        self.add(self.ui.get_object("welcome"))

    def translate_ui(self):
        txt = ""
        if not self.disable_tryit:
            txt = _("You can try Antergos without making any changes to your system by selecting 'Try It'.\n")

        txt += _("When you are ready to install Antergos simply choose which installer you prefer.")            
        txt = '<span weight="bold">%s</span>' % txt
        self.label['info'].set_markup(txt)

        txt = _("Try It")
        self.button['tryit'].set_label(txt)

        txt = _("CLI Installer")
        self.button['cli'].set_label(txt)

        txt = _("Graphical Installer")
        self.button['graph'].set_label(txt)

        txt = _("Welcome to Antergos!")
        self.header.set_subtitle(txt)

    def quit_cnchi(self):
        utils.remove_temp_files(False)
        logging.info(_("Quiting installer..."))
        self.settings.set('stop_all_threads', True)
        logging.shutdown()
        sys.exit(0)
        
    def on_tryit_button_clicked(self, widget, data=None):
        self.quit_cnchi()

    def on_cli_button_clicked(self, widget, data=None):
        try:
            subprocess.Popen(["antergos-setup"])
            self.quit_cnchi()
        except:
            warning(_("Can't load the CLI installer"))

    def on_graph_button_clicked(self, widget, data=None):
        # Tell timezone thread to start searching now
        self.settings.set('timezone_start', True)
        # Simulate a forward button click
        self.forward_button.emit("clicked")

    def store_values(self):
        self.forward_button.show()
        return True

    def prepare(self, direction):
        self.translate_ui()
        self.show_all()
        self.forward_button.hide()
        if self.disable_tryit:
            self.button['tryit'].set_sensitive(False)
        #if info.CNCHI_VERSION is not "0.4.3":
        #    self.button['cli'].set_sensitive(False)


    def start_auto_timezone_thread(self):
        import timezone
        self.auto_timezone_thread = timezone.AutoTimezoneThread(self.auto_timezone_coords, self.settings)
        self.auto_timezone_thread.start()

# When testing, no _() is available
try:
    _("")
except NameError as err:
    def _(message): return message

if __name__ == '__main__':
    from test_screen import _,run
    run('Welcome')
