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

import helpers

APP_STYLE = ("WindowsVista" if sys.platform.startswith('win')  else "PLastique")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

class StyleSheet(object):

    STYLESHEET_PATHS = {
                            'dark': os.path.join(ROOT_DIR, 'styleSheets', 'dark_stylesheet.txt'),
                            'soft': os.path.join(ROOT_DIR, 'styleSheets', 'softimage_stylesheet.txt'),
                            'maya': os.path.join(ROOT_DIR, 'styleSheets', 'maya_stylesheet.txt'),
                            'nuke': os.path.join(ROOT_DIR, 'styleSheets', 'nuke_stylesheet.txt'),

                        }

    def __init__(self, *args, **kwargs):
        super(StyleSheet, self).__init__(*args, **kwargs)
        self.prefFile = os.path.join(ROOT_DIR, 'styleSheets', 'prefs')
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

        p = self.STYLESHEET_PATHS.get(self.style)

        if not p:
            raise Exception('"%s" type of stylesheet option does not exist !!' % STYLESHEET)

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

        self.setWindowTitle('Model Resolution Change Log')
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

        self._nbPages = 6

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
        self._addPath('about', 'html')
        self._addPath('license', 'txt', folder='license')

        self._addPath('about', 'jpg', isImage=True)
        self._addPath('bg', 'jpg', isImage=True)
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

        self.close()

        te = self.tw.textEdit
        p = te.palette()
        p.setColor(QtGui.QPalette.Base, QtGui.QColor(36, 36, 36))
        te.setPalette(p)
        te.setTextColor(QtGui.QColor(227, 227, 227))

        te.setText(self._codeCache['licenseTxt'])

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
        self._modelLabel = QtGui.QLabel(' Available Models')
        self._availableResLabel = QtGui.QLabel(' Available Res (Check Box to Set Active Res)')
        self._resPathLabel = QtGui.QLabel(' Res Path')
        self._resIDLabel = QtGui.QLabel(' Res ID')
        self._nbModelLabel = QtGui.QLabel('<b>  Total Models : </b>')
        self._nbModelLabel.setToolTip('Total number of models in the scntoc file.')

        # Buttons
        #btnHeight = 50

        self._offloadBtn  = QtGui.QPushButton('Offload All')
        #self._offloadBtn.setMinimumSize(300, btnHeight)
        self._offloadBtn.setToolTip('Offload All Models.')

        self._viewBtn  = QtGui.QPushButton('View Changes')
        #self._viewBtn.setMinimumSize(300, btnHeight)
        self._viewBtn.setToolTip('View the changes to be commited.')


        self._resetBtn  = QtGui.QPushButton('Reset All Res to Original')
        #self._resetBtn.setMinimumSize(300, btnHeight)
        self._resetBtn.setToolTip('Reset data to original file at open time.')

        self._applyBtn  = QtGui.QPushButton('Write and Close')
        #self._applyBtn.setMinimumSize(300, btnHeight)
        self._applyBtn.setToolTip('Apply the changes and write the scntoc file on disk.')

        self._cancelBtn  = QtGui.QPushButton('Cancel')
        #self._cancelBtn.setMinimumSize(300, btnHeight)
        self._cancelBtn.setToolTip('Close without saving any changes.')
        self._cancelBtn.clicked.connect(self._cancelBtnOnClickedBase)


        # QLists and QLines
        self._modelListWidget = QtGui.QListWidget()
        self._modelListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self._modelListWidget.setToolTip('Avalaiable reference models in the scntoc file.')
        self._modelListWidget.setMinimumSize(250, 300)

        self._avResListWidget = QtGui.QListWidget()
        self._avResListWidget.setMinimumWidth(150)
        self._avResListWidget.setToolTip('Avalaiable resolutions for the selected Model.')

        self._resPathLineEdit = QtGui.QLineEdit()
        self._resPathLineEdit.setMinimumSize(300, 30)
        self._resPathLineEdit.setReadOnly(True)
        self._resPathLineEdit.setToolTip('Path to the selected resolutions .emdl file.')

        self._resIDLineEdit = QtGui.QLineEdit()
        self._resIDLineEdit.setMinimumHeight(30)
        self._resIDLineEdit.setReadOnly(True)
        self._resIDLineEdit.setToolTip('ID of  the selected resolutions.')


        # Grid Layout Management
        self._grid = QtGui.QGridLayout()
        self._grid.setSpacing(10)

        self._grid.addWidget(self._modelLabel, 0, 0)
        self._grid.addWidget(self._modelListWidget, 1, 0, 9, 1)

        self._grid.addWidget(self._nbModelLabel, 10, 0, 1, 1)

        self._grid.addWidget(self._availableResLabel, 0, 2)
        self._grid.addWidget(self._avResListWidget, 1, 2, 9, 1)

        self._grid.addWidget(self._resPathLabel, 0, 3)
        self._grid.addWidget(self._resPathLineEdit, 1, 3, 1, 1, QtCore.Qt.AlignTop)

        self._grid.addWidget(self._resIDLabel, 2, 3, 1, 1, QtCore.Qt.AlignTop)
        self._grid.addWidget(self._resIDLineEdit, 3, 3, 1, 1, QtCore.Qt.AlignTop)

        self._grid.addWidget(self._offloadBtn, 5, 3, 1, 1, QtCore.Qt.AlignTop)
        self._grid.addWidget(self._viewBtn, 6, 3, 1, 1, QtCore.Qt.AlignTop)
        self._grid.addWidget(self._resetBtn, 7, 3, 1, 1, QtCore.Qt.AlignTop)
        self._grid.addWidget(self._applyBtn, 8, 3, 1, 1, QtCore.Qt.AlignTop)
        self._grid.addWidget(self._cancelBtn, 9, 3, 1, 1, QtCore.Qt.AlignTop)


        self._mainLayout = QtGui.QVBoxLayout(self)
        self._mainLayout.addLayout(self._grid)
        
        StyleSheet().setColor(self)

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
