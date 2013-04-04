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
