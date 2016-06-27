#  Scenetoc Resolution Manager V 1.02 (c) 2013 Alok Gandhi (alok.gandhi2002@gmail.com)
#
#
#  This file is part of Scenetoc Res Manager.
#
#  Scenetoc Res Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License, Version 3, 29 June 2007
#  as published by the Free Software Foundation,
#
#  Scenetoc Res Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Scenetoc Res Manager.  If not, see <http://www.gnu.org/licenses/>.
import os
import sys


def _createShortcut():
    if not sys.platform.startswith('win'):
        print 'This script runs only on Windows !'
        return

    from win32com.client import Dispatch

    ROOT_DIR = os.path.abspath(os.path.dirname(__file__))

    desktop = os.path.abspath(os.path.join(os.path.expanduser('~'), 'Desktop'))
    path = os.path.join(desktop, "Scntoc Res Manager.lnk")
    target = os.path.abspath(os.path.join(ROOT_DIR, 'run.pyw'))
    wDir = ROOT_DIR
    icon = os.path.abspath(os.path.join(ROOT_DIR, 'icons', 'logo_srm.ico'))

    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(path)
    shortcut.Targetpath = target
    shortcut.WorkingDirectory = wDir
    shortcut.IconLocation = icon
    shortcut.save()


_createShortcut()
