# Cnchi

Graphical Installer for Antergos Linux (FKA Cinnarch Linux)

Usage: sudo -E cnchi.py

To create logs to help debug problems: sudo -E cnchi.py -dv

## Dependencies

 * gtk 3
 * python 3
 * python-gobject 3
 * python-dbus
 * python-cairo
 * python-mako
 * libtimezonemap
 * webkitgtk
 * parted (dosfstools, mtools, ntfs-3g, ntfsprogs)
 * py3parted (pyparted on python3) -> https://github.com/antergos/antergos-packages/tree/master/py3parted
 * pacman
 * pyalpm
 * hwinfo
 * hdparm
 * upower
 * python-nose (only needed for unit tests)
 * python-mock (only needed for unit tests)
 * python-lxml (only needed to validate the constructed editions.xml against its schema)

## Validation of editions.xml

The editions.xml file can be validated after modifications on it. This can be done by calling

```
python test/editions_xml_validate.py
```

It will print out errors which occur during the validation, and

```
Everything alright...
```

if the validation was successful.

For this to work, you will need the python-lxml package installed.

## Run Unit-tests

To run the included unit-tests, install the package python-nose and run the following
command:

```
nosetests3 --nocapture
```

## Translations

We manage our translations in transifex:

* https://www.transifex.com/projects/p/antergos/
