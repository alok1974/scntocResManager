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

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

if __name__ == "__main__":
    from gui.mainWindow import run
    run()
