###########################################################################################
###########################################################################################
##                                                                                       ##
##  Scenetoc Resolution Manager V 1.02 (c) 2013 Alok Gandhi (alok.gandhi2002@gmail.com)  ##
##                                                                                       ##
##                                                                                       ##
##  This file is part of Scenetoc Res Manager.                                           ##
##                                                                                       ##
##  Scenetoc Res Manager is free software: you can redistribute it and/or modify         ##
##  it under the terms of the GNU General Public License, Version 3, 29 June 2007        ##
##  as published by the Free Software Foundation,                                        ##
##                                                                                       ##
##  Scenetoc Res Manager is distributed in the hope that it will be useful,              ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of                       ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                        ##
##  GNU General Public License for more details.                                         ##
##                                                                                       ##
##  You should have received a copy of the GNU General Public License                    ##
##  along with Scenetoc Res Manager.  If not, see <http://www.gnu.org/licenses/>.        ##
##                                                                                       ##
###########################################################################################
###########################################################################################

import os
import sys
from PyQt4 import QtCore, QtGui
from logger import Logger

TITLE = "SCNTOC RES MANAGER"
IS_MSG = 0
IS_QUESTION = 1
YES = QtGui.QMessageBox.Yes
NO = QtGui.QMessageBox.No
LEADING_SPACE = 7
PARA_WIDTH = 35

ENUM_CODE = {
                # Messages
                1: ('There are no changes from the original state.', IS_MSG),
                3: ('You need to have at least one res selected to apply the filer.', IS_MSG),
                4: ('No Models with %s combination of filters.', IS_MSG),
                5: ('There are no changes to save.', IS_MSG),
                6: ('The file path - %s does not exist !. This path will be removed from the recent files list.', IS_MSG),

                # Questions
                101: ('Do you want to offoad all models ?', IS_QUESTION),
                102: ('Do you want to revert all changes you made and go back to original file state?', IS_QUESTION),
                103: ('Do you want to write changes to the loaded file and close ?', IS_QUESTION),
                104: ('Do you want to exit without saving your changes ? ', IS_QUESTION),
            }


def _addArgs(inStr, inArgs=[]):
    p = inStr.split("%s")

    if len(inArgs)!=len(p) - 1:
        raise Exception("Need same numbers args and specifiers !!")

    f = ''
    for i in range(len(inArgs)):
        f += '%s%s'% (p[i], inArgs[i])

    f += p[-1]

    return f

def _makePara(inText):
    allWords = inText.split(" ")

    words = []
    for word in allWords:
        if '/' in word:
            allPWords = word.split('/')
            for index, pWord in enumerate(allPWords):
                if index==len(allPWords) - 1:
                    nWord = pWord
                else:
                    nWord = '%s/' % pWord

                words.append(nWord)
        else:
            words.append(word)

    finalStr = ''
    finalStr = '\n'
    finalStr += ' ' * LEADING_SPACE
    currLen = 0
    for index, word in enumerate(words):
        wordWithSpace = "%s " % word
        finalStr += wordWithSpace
        currLen += len(wordWithSpace)

        if currLen > PARA_WIDTH:
            finalStr += '\n'
            finalStr += ' ' * LEADING_SPACE
            currLen = 0

    finalStr += '\n\n'

    return finalStr

def _wrapMsg(inMsg, args=[]):
    msg = _addArgs(inMsg, inArgs=args)
    msg = _makePara(msg)

    return msg

def _pop(widget, code, extraArgs=[]):
    msg, type = ENUM_CODE.get(code)

    msg = _wrapMsg(msg, args=extraArgs)

    if type==IS_MSG:
        QtGui.QMessageBox.information(widget, TITLE, msg)

    elif type==IS_QUESTION:
        reply = QtGui.QMessageBox.question(widget, TITLE, msg, YES, NO)

        if reply==YES:
            return True

        return False
