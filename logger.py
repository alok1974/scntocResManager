#!/usr/bin/env python

import os
import inspect
import logging


logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

TRACEBACK_INSPECTOR = inspect.currentframe

DEBUG = logging.DEBUG
INFO = logging.INFO
ERROR = logging.ERROR
WARNING = logging.WARN
CRITICAL = logging.CRITICAL


def debugFullTraceback(traceback=None):
    """"""
    for i in inspect.getouterframes(traceback):
        Logger.info(i)


def debugCaller(traceback=None):
    """ Function who return all the traceback of a call."""
    tracebackLog = inspect.getouterframes(traceback)
    moduleName = os.path.basename(tracebackLog[1][1]).replace(".py", "").replace('<Script Block >', 'stdin')
    methodName = tracebackLog[1][3]
    return [moduleName, methodName]


class Logger(object):
    """
    """

    level = INFO
    criticalFunc = None
    infoFunc = None
    warningFunc = None
    debugFunc = None
    errorFunc = None
    tracebackFunc = None
    separatorFunc = None
    spaceFunc = None

    @classmethod
    def onDebug(cls, func):
        """
        """

        cls.debugFunc = func

    @classmethod
    def onWarning(cls, func):
        """
        """

        cls.warningFunc = func

    @classmethod
    def onCritical(cls, func):
        """
        """

        cls.criticalFunc = func

    @classmethod
    def onError(cls, func):
        """
        """

        cls.errorFunc = func

    @classmethod
    def onInfo(cls, func):
        """
        """

        cls.infoFunc = func

    @classmethod
    def onTraceback(cls, func):
        """
        """

        cls.tracebackFunc = func

    @classmethod
    def onSeparator(cls, func):
        """
        """

        cls.separatorFunc = func

    @classmethod
    def onSpace(cls, func):
        """
        """

        cls.spaceFunc = func

    @classmethod
    def warning(cls, msg):
        """
        """

        if cls.level <= WARNING:
            msgComplete = cls._buildString(inspect.currentframe(), msg, WARNING)
            if cls.warningFunc:
                cls().warningFunc(msgComplete)
            else:
                logging.warning(msgComplete)

    @classmethod
    def info(cls, msg):
        """
        """

        if cls.level <= INFO:
            msgComplete = cls._buildString(inspect.currentframe(), msg, INFO)
            if cls.infoFunc:
                cls().infoFunc(msgComplete)
            else:
                logging.info(msgComplete)

    @classmethod
    def debug(cls, msg):
        """
        """

        if cls.level <= DEBUG:
            msgComplete = cls._buildString(inspect.currentframe(), msg, DEBUG)
            if cls.debugFunc:
                cls().debugFunc(msgComplete)
            else:
                logging.debug(msgComplete)

    @classmethod
    def error(cls, msg):
        """
        """

        if cls.level <= ERROR:
            msgComplete = cls._buildString(inspect.currentframe(), msg, ERROR)
            if cls.errorFunc:
                cls().errorFunc(msgComplete)
            else:
                logging.error(msgComplete)

    @classmethod
    def critical(cls, msg):
        """
        """

        if cls.level <= CRITICAL:
            msgComplete = cls._buildString(inspect.currentframe(), msg, CRITICAL)
            if cls.criticalFunc:
                cls().criticalFunc(msgComplete)
            else:
                logging.critical(msgComplete)

    def traceback(cls, msg):
        """
        """

        if cls.tracebackFunc:
            cls.tracebackFunc(msg)
        else:
            TracebackError(msg)

    @classmethod
    def _buildString(cls, input, msg, typeErr):
        """ Build the display error string by the type of error """

        debugAsString = debugCaller(input)
        if typeErr in [INFO, WARNING]:
            return "[%s] %s" % (debugAsString[0], msg)
        return "[%s::%s] %s" % (debugAsString[0], debugAsString[1], msg)

    @classmethod
    def getLogger(cls, loggerName):
        """ Return the given name of the logger """
        logging.getLogger(loggerName)

    @classmethod
    def setLevel(cls, level):
        """ set the level of debugging """
        cls.level = level

    @classmethod
    def getLevel(cls):
        """"""
        return cls.level

    @classmethod
    def addSeparator(cls, separator="-", length=75):
        """ Create a line of separator to help viewable displaying of an error """

        if cls.separatorFunc:
            cls().separatorFunc(separator * length)
        else:
            logging.info(separator * length)

    @classmethod
    def addSpace(cls):
        if cls.spaceFunc:
            cls().spaceFunc()
        else:
            logging.info("")


class TracebackError(object):
    """Output the whole traceback instead of only the last message and Log it as Critical"""
    def __init__(self, e):
        """TracebackError Constructor"""
        super(TracebackError, self).__init__()
        import StringIO
        import traceback

        fileHandler = StringIO.StringIO()
        traceback.print_exc(file=fileHandler)
        self.trace = fileHandler.getvalue()

        Logger.critical(self.trace)

    def asString(self):
        """"""
        return self.trace


if __name__ == "__main__":
    class Test(object):
        def __init__(self):
            pass

        def runTest(self):
            Logger.setLevel(DEBUG)
            Logger.info("info")
            Logger.critical("critical")
            Logger.debug("debug")
            Logger.warning("warning")
            Logger.error("error")

    aTest = Test()
    aTest.runTest()
