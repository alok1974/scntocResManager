##########################################################################################
##########################################################################################
##                                                                                      ##
##  Scenetoc Resolution Manager V 1.02 (c) 2013 Alok Gandhi (alok.gandhi2002@gmail.com)  ##
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
import helpers
from logger import Logger

APP_STYLE = ("WindowsVista" if sys.platform.startswith('win')  else "Plastique")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class ResPathEditWidget(QtGui.QDialog):
    def __init__(self, widget=None, dataChangedWidget=None, multiSelected=False, selectedRes='', selectedModel='', selectedModels=[], resData={}, resDataOrig={}, *args, **kwargs):
        super(ResPathEditWidget, self).__init__(*args, **kwargs)
        self.setModal(True)
        self._widget = widget
        self._multiSelected = multiSelected
        self._selectedRes = selectedRes
        self._selectedModel = selectedModel
        self._dataChangedWidget = dataChangedWidget

        StyleSheet().setColor(self)

        if self._multiSelected:
            self._selectedModels = selectedModels
        else:
            self._selectedModels = [self._selectedModel]

        self._resData = resData
        self._resDataOrig = resDataOrig

        if self._widget:
            self._text = str(self._widget.text())
        else:
            self._text = r'just\a\path\to\a\folder\with\a\file.ext'

        # Set UI
        self._initUI()

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # Add Widgets
        self._pathLabel = QtGui.QLabel('Edit Path :')
        self._pathLineEdit = QtGui.QLineEdit()
        self._pathLineEdit.setText(self._text)
        self._pathLineEdit.setMinimumWidth(300)

        self._notFoundLabel = QtGui.QLineEdit('     Pattern not found!')
        self._notFoundLabel.setEnabled(False)
        self._notFoundLabel.setMinimumSize(100, 40)
        self._notFoundLabel.setFrame(False)
        self._notFoundLabel.setStyleSheet("QLineEdit {background-color : rgb(255, 255, 0); color : rgb(100, 0, 0)}")
        self._notFoundLabel.hide()

        self._findLabel = QtGui.QLabel('Find : ')
        self._findLineEdit = QtGui.QLineEdit()

        self._replaceLabel = QtGui.QLabel('Replace : ')
        self._replaceLineEdit = QtGui.QLineEdit()

        self._wordCheckBox = QtGui.QCheckBox('Word')
        self._ignoreCaseCheckBox = QtGui.QCheckBox('Ignore Case')

        self._replaceBtn = QtGui.QPushButton('Replace')
        self._okBtn = QtGui.QPushButton('Ok')

        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(10)

        self._grid.addWidget(self._pathLabel, 0, 0)
        self._grid.addWidget(self._pathLineEdit, 0, 1, 1, 2)

        self._grid.addWidget(self._findLabel, 1, 0)
        self._grid.addWidget(self._findLineEdit, 1, 1, 1, 2)

        self._grid.addWidget(self._replaceLabel, 2, 0)
        self._grid.addWidget(self._replaceLineEdit, 2, 1, 1, 2)

        self._hLayout = QtGui.QHBoxLayout()
        self._hLayout.addStretch(1)


        self._hLayout.addWidget(self._notFoundLabel)
        self._hLayout.addWidget(self._wordCheckBox)
        self._hLayout.addWidget(self._ignoreCaseCheckBox)
        self._hLayout.addWidget(self._replaceBtn)
        self._hLayout.addWidget(self._okBtn)

        self._grid.addLayout(self._hLayout, 3, 2, 1, 1)

        self.setGeometry(200, 200, 300, 120)

        self.setWindowTitle("Edit Resolution Path")

        self.setLayout(self._grid)

    def _connectSignals(self):
        self._okBtn.clicked.connect(self._okBtnOnClicked)
        self._replaceBtn.clicked.connect(self._replaceBtnOnClicked)


    def _replaceBtnOnClicked(self):
        if not str(self._findLineEdit.text()):
            return

        if not str(self._replaceLineEdit.text()):
            return

        pathStr = str(self._pathLineEdit.text())
        find = str(self._findLineEdit.text())
        replace = str(self._replaceLineEdit.text())
        ignoreCase = bool(self._ignoreCaseCheckBox.checkState())
        wholeWord = bool(self._wordCheckBox.checkState())

        replacedText = helpers._replaceWord(inString=pathStr, inFind=find,
                                            inReplace=replace, inIgnoreCase=ignoreCase,
                                            inWholeWord=wholeWord)

        if replacedText==pathStr:
            self._notFoundLabel.show()
            return
        else:
            self._notFoundLabel.hide()

        self._pathLineEdit.setText(replacedText)
        self._findLineEdit.setText("")
        self._replaceLineEdit.setText("")

    def _okBtnOnClicked(self):
        if not self._widget:
            return

        newPath = str(self._pathLineEdit.text())
        if not os.path.exists(newPath):
            r, g, b = 120, 0, 0
        else:
            r, g, b = 0, 120, 0

        self._widget.setStyleSheet("QLineEdit {background-color: rgb(230, 230, 230); color : rgb(%s, %s, %s)}" % (r, g, b))
        self._widget.setText(newPath)
        datachanged = self._setPath(newPath)
        self._dataChangedWidget.setText(datachanged)

        self.close()

    def _setPath(self, path):
        dataChanged = "0"
        for modelName in self._selectedModels:
            resData = [data for data in self._resData[modelName] if data['resName']==self._selectedRes][0]
            resData['resPath'] = "file://%s" % path

            resDataOrig = [data for data in self._resDataOrig[modelName] if data['resName']==self._selectedRes][0]
            resPathOrig = resDataOrig['resPath'][7:]

            if path!=resPathOrig:
                dataChanged="1"

        return dataChanged

def clickable(widget):
    # Re implementation of for the Res Path Double Click
    class MouseDoubleClickFilter(QtCore.QObject):
        _doubleClicked = QtCore.pyqtSignal()

        def eventFilter(self, obj, event):
            if obj==widget:
                if event.type()==QtCore.QEvent.MouseButtonDblClick:
                    self._doubleClicked.emit()
                    return True

            return False

    filter = MouseDoubleClickFilter(widget)
    widget.installEventFilter(filter)

    return filter._doubleClicked

class RecentFiles(object):
    def __init__(self, *args, **kwargs):
        super(RecentFiles, self).__init__(*args, **kwargs)
        self.recentFile = os.path.join(ROOT_DIR, 'prefs', 'recentfiles')
        self.files = []
        self.maxFiles = 5

    def _createRecent(self):
        with open(self.recentFile, 'w') as f:
            f.write('')

    def _fetchRecent(self):
        if not os.path.exists(self.recentFile):
            self._createRecent()

        t = ''
        with open(self.recentFile, 'r') as f:
            t = f.read()

        self.files = t.split('"')

        # Cleaning any empty values
        self.files = [f for f in self.files if f]

        return self.files

    def _writeRecent(self):
        with open(self.recentFile, 'w') as f:
            f.write('"'.join(self.files))

    def _addFile(self, toAdd):
        self._fetchRecent()

        if self.files:
            if len(self.files) > self.maxFiles:
                return

        if toAdd in self.files:
            self.files.remove(toAdd)

        self.files.insert(0, toAdd)
        self._writeRecent()


    def _removeFile(self, toRemove):
        files = self._fetchRecent()
        files.remove(toRemove)

        self._writeRecent()

class StyleSheet(object):
    STYLESHEET_OPTIONS = ['dark', 'soft', 'maya', 'nuke',]

    def __init__(self, *args, **kwargs):
        super(StyleSheet, self).__init__(*args, **kwargs)
        self.prefFile = os.path.join(ROOT_DIR, 'prefs', 'currStyle')
        self.style = ''

    def _createPrefs(self):
        with open(self.prefFile, 'w') as f:
            f.write('theme:')

    def _readPrefs(self):
        if not os.path.exists(self.prefFile):
            self._createPrefs()

        with open(self.prefFile, 'r') as f:
            s = f.readlines()

        self.style= s[0].split(':')[-1]

        return self.style

    def _writePrefs(self, pref=''):
        if not os.path.exists(self.prefFile):
            self._createPrefs()

        with open(self.prefFile, 'w') as f:
            f.write('theme:%s' % pref)

    def setColor(self, widget, app=None, init=False):
        self._readPrefs()

        if not self.style:
            if app:
                pass
                app.setStyle(QtGui.QStyleFactory.create(APP_STYLE))

            widget.setStyleSheet("")

            return

        if self.style not in self.STYLESHEET_OPTIONS:
            raise Exception('"%s" type of stylesheet option does not exist !!' % self.style)

        p = os.path.join(ROOT_DIR, 'styleSheets', str(self.style))

        if not os.path.exists(p):
            raise Exception('Style Path - %s does not exist !!' % p)

        with open(p, 'r') as f:
            s = f.read()

        if app:
            app.setStyle(QtGui.QStyleFactory.create("Plastique"))

        widget.setStyleSheet(s)

class TextWidget(QtGui.QDialog):
    def __init__(self, *args, **kwargs):
        super(TextWidget, self).__init__(*args, **kwargs)
        self.setModal(True)

        # Set UI
        self._initUI()

        StyleSheet().setColor(self)

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # Add Widgets
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(True)

        self.okBtn = QtGui.QPushButton('Ok')
        self.okBtn.setMinimumSize(80, 25)

        # Add Layout
        self._vLayout = QtGui.QVBoxLayout()
        self._hLayout = QtGui.QHBoxLayout()
        self._hLayout.addStretch(1)

        # Add Widgets to Layouts
        self._hLayout.addWidget(self.okBtn)

        self._vLayout.addWidget(self.textEdit)
        self._vLayout.addLayout(self._hLayout)

        self.setGeometry(300, 100, 500, 600)

        self.setLayout(self._vLayout)

    def _connectSignals(self):
        self.okBtn.clicked.connect(self._okBtnOnClicked)

    def _okBtnOnClicked(self):
        self.textEdit.sizeHint()
        self.close()

class HelpWidget(QtGui.QDialog):
    def __init__(self, help=False, *args, **kwargs):
        super(HelpWidget, self).__init__(*args, **kwargs)

        self.setModal(True)

        self._help = help

        self._pg = 1

        self._nbPages = 8

        self._pathCache = {}

        self._codeCache = {}

        # Set UI
        self._initUI()

        StyleSheet().setColor(self)

        # Connect Signals
        self._connectSignals()

    def _initUI(self):
        # Add Widgets
        self.textEdit = QtGui.QTextEdit()
        self.textEdit.setReadOnly(True)
        self.textEdit.setAcceptRichText(True)
        self.textEdit.setAlignment(QtCore.Qt.AlignCenter)

        self.closeBtn = QtGui.QPushButton('Close')
        self.closeBtn.setMinimumSize(80, 25)

        self.licenseBtn = QtGui.QPushButton('View License')
        self.licenseBtn.setMinimumSize(80, 25)

        self.nextBtn = QtGui.QPushButton('Next >>')
        self.nextBtn.setMinimumSize(80, 25)

        self.prevBtn = QtGui.QPushButton('<< Prev')
        self.prevBtn.setMinimumSize(80, 25)

        self.homeBtn = QtGui.QPushButton('< Home >')
        self.homeBtn.setMinimumSize(80, 25)

        # Add Layout
        self._vLayout = QtGui.QVBoxLayout()
        self._hLayout = QtGui.QHBoxLayout()
        self._hLayout.addStretch(1)

        # Add Widgets to Layouts
        if self._help:
            self._hLayout.addWidget(self.prevBtn)
            self._hLayout.addWidget(self.homeBtn)
            self._hLayout.addWidget(self.nextBtn)
            self.setWindowTitle("Help")
            self.setGeometry(100, 50, 1000, 693)
        else:
            self._hLayout.addWidget(self.licenseBtn)
            self.setWindowTitle("About")
            self.setFixedSize(482, 245)
            self.move(100, 50)

        self._hLayout.addWidget(self.closeBtn)

        self._vLayout.addWidget(self.textEdit)
        self._vLayout.addLayout(self._hLayout)
        self.setLayout(self._vLayout)

        # Handle HTML Operations
        self._initPaths()
        self._initCode()
        self._initPage()

    def _initPaths(self):
        self._addPath('style', 'css')
        self._addPath('about', 'html')
        self._addPath('license', 'txt', folder='license')

        self._addPath('about', 'jpg', isImage=True)
        self._addPath('bg', 'jpg', isImage=True)

        for i in range(1, self._nbPages + 1):
            self._addPath('help%s' % str(i).zfill(2), 'html')
            self._addPath('help%s' % str(i).zfill(2), 'jpg', isImage=True)

    def _initCode(self):
        self._addCode('style', 'css')
        self._addCode('about', 'html')
        self._addCode('license', 'txt')

        for i in range(1, self._nbPages + 1):
            self._addCode('help%s' % str(i).zfill(2), 'html')

    def _addPath(self, keyName, ext, folder='html', isImage=False):
        paths = [ROOT_DIR, folder, '%s.%s' % (keyName, ext)]

        if isImage:
            paths.insert(2, 'images')

        self._pathCache['%s%s%s' % (keyName, ext[0].capitalize(), ext[1:])] = os.path.join(*paths)

    def _addCode(self, keyName, ext):
        with open(self._pathCache['%s%s%s' % (keyName, ext[0].capitalize(), ext[1:])], 'r') as f:
            self._codeCache['%s%s%s' % (keyName, ext[0].capitalize(), ext[1:])] = f.read()

    def _initPage(self):
        self._setHtml()

    def _connectSignals(self):
        self.closeBtn.clicked.connect(self._closeBtnOnClicked)
        self.licenseBtn.clicked.connect(self._licenseBtnOnClicked)
        self.nextBtn.clicked.connect(self._nextBtnOnClicked)
        self.prevBtn.clicked.connect(self._prevBtnOnClicked)
        self.homeBtn.clicked.connect(self._homeBtnOnClicked)

    def _okBtnOnClicked(self):
        self.textEdit.sizeHint()
        self.close()

    def _nextBtnOnClicked(self):
        if self._pg==self._nbPages:
            return

        self._setHtml(pageNo=(self._pg + 1))
        self._pg += 1

    def _prevBtnOnClicked(self):
        if self._pg==1:
            return

        self._setHtml(pageNo=(self._pg - 1))
        self._pg -= 1

    def _homeBtnOnClicked(self):
        self._setHtml(pageNo=1)
        self._pg = 1

    def _closeBtnOnClicked(self):
        self.textEdit.sizeHint()
        self.close()

    def _licenseBtnOnClicked(self):
        if not hasattr(self, 'tw'):
            self.tw = TextWidget()
        else:
            self.tw = None
            self.tw = TextWidget()

        self.close()

        te = self.tw.textEdit
        te.setStyleSheet("QTextEdit {background-color : rgb(36, 36, 36); color : rgb(227, 227, 227)}")


        te.setText(self._codeCache['licenseTxt'])

        self.tw.setWindowTitle('License')

        self.tw.show()


    def _setHtml(self, pageNo=1):
        html = ('help%sHtml' % (str(pageNo).zfill(2)) if self._help else 'aboutHtml')
        imgPath = ('help%sJpg' % (str(pageNo).zfill(2)) if self._help else 'aboutJpg')
        imgName = ('help%s.jpg' % (str(pageNo).zfill(2)) if self._help else 'about.jpg')

        doc = QtGui.QTextDocument()

        doc.addResource(QtGui.QTextDocument.ImageResource,
                        QtCore.QUrl('images/bg.jpg'),
                        QtCore.QVariant(QtGui.QImage(self._pathCache['bgJpg']))
                        )


        doc.addResource(QtGui.QTextDocument.StyleSheetResource,
                        QtCore.QUrl('style.css'),
                        self._codeCache['styleCss']
                        )


        doc.addResource(QtGui.QTextDocument.ImageResource,
                        QtCore.QUrl('images/%s' % imgName),
                        QtCore.QVariant(QtGui.QImage(self._pathCache[imgPath]))
                        )

        doc.setHtml(self._codeCache[html])

        self.textEdit.setDocument(doc)

class MainWidgetUI(QtGui.QWidget):
    def __init__(self, *args, **kwargs):
        super(MainWidgetUI, self).__init__(*args, **kwargs)
        self._hasFileloaded = False

    def _setupUI(self):
        # Labels
        self._modelLabel = QtGui.QLabel(' <b>Available Models</b>  <i>ModelName    (Active Res)</i>')
        self._availableResLabel = QtGui.QLabel(' <b>Available Res</b> <i>(Check Box to Set Active Res)</i>')
        self._filterLabel = QtGui.QLabel('<b>Filter Model List by Active Res</b>')
        self._resPathLabel = QtGui.QLabel(' <b>Res Path</b> <i>(Double Click to edit)</i>')
        self._resIDLabel = QtGui.QLabel(' <b>Res ID</b>')
        self._emptyLabel = QtGui.QLabel('')

        self._nbModelLabel = QtGui.QLabel('<b><i>Total Models : </i></b>')
        self._nbModelLabel.setToolTip('Total number of models in the scntoc file.')

        self._nbSelectedModelLabel = QtGui.QLabel('<b>  <i>Selected Models : </i></b>')
        self._nbSelectedModelLabel.setToolTip('Total number of selected models.')


        # Buttons
        #btnHeight = 50

        self._applyFilterBtn  = QtGui.QPushButton('Apply Filter')
        self._applyFilterBtn.setToolTip('Apply filter on the Model List.')

        self._resetFilterBtn  = QtGui.QPushButton('Reset Filter')
        self._resetFilterBtn.setToolTip('Reset filters.')

        self._offloadBtn  = QtGui.QPushButton('Offload All')
        self._offloadBtn.setToolTip('Offload All Models.')

        self._viewBtn  = QtGui.QPushButton('View Changes')
        self._viewBtn.setToolTip('View the changes to be commited.')

        self._resetBtn  = QtGui.QPushButton('Reset All Res to Original')
        self._resetBtn.setToolTip('Reset data to original file at open time.')

        self._selectBtn  = QtGui.QPushButton('Res to Model Lookup')
        self._selectBtn.setToolTip('Select all models based on a particular resolution.')

        self._applyBtn  = QtGui.QPushButton('Write and Close')
        self._applyBtn.setToolTip('Apply the changes and write the scntoc file on disk.')

        self._cancelBtn  = QtGui.QPushButton('Cancel')
        self._cancelBtn.setToolTip('Close without saving any changes.')
        self._cancelBtn.clicked.connect(self._cancelBtnOnClickedBase)


        # QLists and QLines
        self._modelListWidget = QtGui.QListWidget()
        self._modelListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self._modelListWidget.setToolTip('Avalaiable reference models in the scntoc file.')
        self._modelListWidget.setMinimumSize(250, 300)

        self._avResListWidget = QtGui.QListWidget()
        self._avResListWidget.setMinimumSize(150, 150)
        self._avResListWidget.setToolTip('Avalaiable resolutions for the selected Model.')

        self._filterListWidget = QtGui.QListWidget()
        self._filterListWidget.setMinimumSize(150, 150)
        self._filterListWidget.setToolTip('Filter model list by selecting a res.')

        self._resPathLineEdit = QtGui.QLineEdit()
        self._resPathLineEdit.setMinimumSize(300, 30)
        self._resPathLineEdit.setReadOnly(True)
        self._resPathLineEdit.setToolTip('Path to the selected resolutions .emdl file.')

        self._resIDLineEdit = QtGui.QLineEdit()
        self._resIDLineEdit.setMinimumHeight(30)
        self._resIDLineEdit.setReadOnly(True)
        self._resIDLineEdit.setToolTip('ID of  the selected resolutions.')

        # Creating Hidden Data Changed Line Edit
        self._dataChangedLineEdit = QtGui.QLineEdit()
        self._dataChangedLineEdit.setText("0")
        self._dataChangedLineEdit.hide()

        # Grid Layout Management
        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(10)

        # Adding Hidden Data Changed Line Edit
        self._grid.addWidget(self._dataChangedLineEdit, 0, 0)

        self._grid.addWidget(self._modelLabel, 0, 0)
        self._grid.addWidget(self._modelListWidget, 1, 0, 10, 1)

        self._grid.addWidget(self._nbModelLabel, 11, 0, 1, 1)

        self._grid.addWidget(self._availableResLabel, 0, 2)
        self._grid.addWidget(self._avResListWidget, 1, 2)

        self._grid.addWidget(self._filterLabel, 3, 2)
        self._grid.addWidget(self._filterListWidget, 4, 2, 4, 4)

        self._grid.addWidget(self._applyFilterBtn, 9, 2, 1, 4)

        self._grid.addWidget(self._resetFilterBtn, 10, 2, 1, 4)

        self._grid.addWidget(self._nbSelectedModelLabel, 11, 2)

        self._vLayout = QtGui.QVBoxLayout()
        self._vLayout.addStretch(100)

        self._grid.addWidget(self._resPathLabel, 0, 3, 1, 1)
        self._vLayout.addWidget(self._resPathLineEdit)

        self._vLayout.addWidget(self._resIDLabel)
        self._vLayout.addWidget(self._resIDLineEdit)

        self._vLayout.addWidget(self._offloadBtn)
        self._vLayout.addWidget(self._viewBtn)
        self._vLayout.addWidget(self._resetBtn)
        self._vLayout.addWidget(self._applyBtn)
        self._vLayout.addWidget(self._cancelBtn)

        self._grid.addLayout(self._vLayout, 1, 3)

        self._mainLayout = QtGui.QVBoxLayout(self)
        self._mainLayout.addLayout(self._grid)


    def _cancelBtnOnClickedBase(self):
        if self._hasFileloaded:
            return

        QtCore.QCoreApplication.instance().quit()


class TestWidget(HelpWidget):
    def __init__(self, *args, **kwargs):
        super(TestWidget, self).__init__(help=False, *args, **kwargs)
        #self._setupUI()

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    w = TestWidget()
    w.show()
    w.raise_()
    app.exec_()
