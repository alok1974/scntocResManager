##########################################################################################
##########################################################################################
##                                                                                      ##
##  Scenetoc Resolution Manager V 1.0 (c) 2013 Alok Gandhi (alok.gandhi2002@gmail.com)  ##
##                                                                                      ##
##                                                                                      ##
##  This program is free software: you can redistribute it and/or modify it             ##
##  under the terms of the GNU General Public License, Version 3, 29 June 2007          ##
##  as published by the Free Software Foundation   <http://fsf.org/>                    ##
##  TO view the full license, read license.txt in the folder ../license                 ##
##                                                                                      ##
##########################################################################################
##########################################################################################

import os
import sys
from PyQt4 import QtCore, QtGui

TITLE = "SCNTOC RES MANAGER"
IS_MSG = 0
IS_QUESTION = 1
YES = QtGui.QMessageBox.Yes
NO = QtGui.QMessageBox.No
LEADING_SPACE = 7
PARA_WIDTH = 80

ENUM_CODE = {
                # Messages
                1: ('There are no changes from the original state.', IS_MSG),
                3: ('You need to have at least one res selected to apply the filer.', IS_MSG),
                4: ('No Models with %s combination of filters.', IS_MSG),
                5: ('There are no changes to save.', IS_MSG),

                # Questions
                101: ('Do you want to offoad all models ?', IS_QUESTION),
                102: ('Do you want to revert all changes you made and go back to original file state ?', IS_QUESTION),
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
    words = inText.split(" ")
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
    msg = _makePara(inMsg)

    msg = _addArgs(msg, inArgs=args)

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