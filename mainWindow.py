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

import sys
import os

from PyQt4 import QtCore, QtGui

from scntocReader import ScenetocReader
import helpers
from widgets import MainWidgetUI, TextWidget, HelpWidget, StyleSheet

class MainWidget(MainWidgetUI):
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self._file = None
        self._dataChanged = False

        # Setup Layout
        self._initUI()

    def _initUI(self):
        self._setupUI()
        self.setLayout(self._mainLayout)

    def load(self, file):
        self._file = file


    def run(self):
        if not self._file:
            return

        self._sr = ScenetocReader(self._file)

        if self._sr._hasError:
            if not hasattr(self, 'tw'):
                self.tw = TextWidget()

            errStr = ''
            errStr += 'There were following error/errors in opening file:\n\n'
            errStr += self._sr._error

            self.tw.textEdit.setText(errStr)
            self.tw.setGeometry(100, 100, 500, 250)
            self.tw.show()

            return

        self._modelDict = self._sr.getModels()
        self._initData()
        self._initWidgets()
        self._hasFileloaded = True

        # Connect Signals
        self._connectSignals()
        
    def _initData(self):
        self._modelListWidget.clear()
        self._avResListWidget.clear()
        self._resIDLineEdit.setText('')
        self._resPathLineEdit.setText('')
        self._nbModelLabel.setText('')

        self._selectedModelName = ''
        self._selectedModelNames = []
        self._selectedResName = ''
        self._mutliSelected = False

        self._modelNames, self._modelNameColors = helpers._sortAndMakeColors(self._modelDict.keys())
        self._nbModels = len(self._modelNames)
        self._modelActiveResNames = dict([(k, v['activeResName']) for k, v in self._modelDict.iteritems()])
        self._modelActiveResNamesOriginal = dict([(k, v['activeResName']) for k, v in self._modelDict.iteritems()])
        self._modelResData = dict([(k, v['resData']) for k, v in self._modelDict.iteritems()])
        self._modelAvailableResNames = dict([(modelName, [d['resName']for d in modelData['resData']]) for modelName, modelData in self._modelDict.iteritems()])

    def _initWidgets(self):
        # Init Model Name List Widget
        for modelName in self._modelNames:
            w = QtGui.QListWidgetItem(modelName)
            r, g, b = self._modelNameColors[modelName]
            w.setBackground(QtGui.QColor(r, g, b))
            w.setForeground(QtGui.QColor(0, 0, 0))
            self._modelListWidget.addItem(w)

        self._modelListWidget.setCurrentRow(0)
        self._selectedModelName = str(self._modelListWidget.currentItem().text())
        self._activeResName = str(self._modelActiveResNames[self._selectedModelName])
        self._nbModelLabel.setText('<b>  Total Models : </b><b>%s</b>' % str(self._nbModels))

        # Init Available Res Names List Widget
        self._updateAvailableResolution()

    def _updateAvailableResolution(self):
        self._avResListWidget.clear()
        avRes = self._modelAvailableResNames[self._selectedModelName]
        activeRes = self._modelActiveResNames[self._selectedModelName]

        activeResIndex = 0
        for index, res in enumerate(avRes):
            w = QtGui.QListWidgetItem(res)

            if str(res)==str(activeRes):
                w.setCheckState(2)
                activeResIndex = index
            else:
                pass
                w.setCheckState(0)

            self._avResListWidget.addItem(w)

        self._avResListWidget.setCurrentRow(activeResIndex)
        self._selectedResName = str(self._avResListWidget.currentItem().text())
        self._resolutionOnChanged()

    # Signal Connections
    def _connectSignals(self):
        self._avResListWidget.currentItemChanged.connect(self._resolutionOnChanged)
        self._avResListWidget.itemChanged.connect(self._checkBoxOnClicked)
        self._modelListWidget.itemSelectionChanged.connect(self._modelNameOnSelectionChange)
        self._offloadBtn.clicked.connect(self._offloadBtnOnClicked)
        self._viewBtn.clicked.connect(self._viewBtnOnClicked)
        self._resetBtn.clicked.connect(self._resetBtnOnClicked)
        self._applyBtn.clicked.connect(self._applyBtnOnClicked)
        self._cancelBtn.clicked.connect(self._cancelBtnOnClicked)

    def _resolutionOnChanged(self):
        if not self._avResListWidget.currentItem():
            return

        if self._mutliSelected:
            self._resPathLineEdit.setText("<multiple selection>")
            self._resIDLineEdit.setText("<multiple selection>")
            return


        self._selectedResName = str(self._avResListWidget.currentItem().text())

        resData = self._modelResData[self._selectedModelName]
        resPath = str([d['resPath'] for d in resData if d['resName']==self._selectedResName][0])
        if resPath=='':
            resPath="<Empty>"
        else:
            resPath = resPath[7:]
        resID = str([d['resID'] for d in resData if d['resName']==self._selectedResName][0])

        # Updating Selected  Res Path
        self._resPathLineEdit.setText(resPath)
        self._resPathLineEdit.setCursorPosition(0)

        # Updating Selected  Res ID
        self._resIDLineEdit.setText(resID)

    def _checkBoxOnClicked(self, item):
        self._avResListWidget.setCurrentItem(item)

        if item.checkState()==0:
            self._avResListWidget.blockSignals(True) # blocking signals so the func does not go in recursion
            item.setCheckState(2)
            self._avResListWidget.blockSignals(False)
            return

        for index in range(self._avResListWidget.count()):
            thisItem = self._avResListWidget.item(index)
            if thisItem!=item:
                self._avResListWidget.blockSignals(True) # blocking signals so the func does not go in recursion
                thisItem.setCheckState(0)
                self._avResListWidget.blockSignals(False)

        if self._mutliSelected:
            for modelName in self._selectedModelNames:
                clickedRes = item.text()
                currentRes = self._modelActiveResNamesOriginal[modelName]

                if str(clickedRes)!=str(currentRes):
                    self._dataChanged = True
                else:
                    self._dataChanged = False

                self._modelActiveResNames[modelName] = item.text()

        else:
            clickedRes = item.text()
            currentRes = self._modelActiveResNamesOriginal[self._selectedModelName]

            if str(clickedRes)!=str(currentRes):
                self._dataChanged = True
            else:
                self._dataChanged = False

            self._modelActiveResNames[self._selectedModelName] = item.text()

    def _modelNameOnSelectionChange(self):
        if len(self._modelListWidget.selectedItems()) > 1:
            self._mutliSelected = True
            self._modelNameOnChangedMulti()
            self._resPathLineEdit.setText("<multiple selection>")
            self._resIDLineEdit.setText("<multiple selection>")

        else:
            self._mutliSelected = False
            self._modelNameOnChangedSingle()

    def _modelNameOnChangedMulti(self):
        self._selectedModelNames = [str(item.text()) for item in self._modelListWidget.selectedItems()]
        commonRes = helpers._getCommonRes(self._selectedModelNames, self._modelAvailableResNames)

        if not commonRes:
            self._avResListWidget.clear()
            self._avResListWidget.addItems(['  <No Common Res>  '])
            return

        commonActiveResList = helpers._getCommonRes(self._selectedModelNames, dict([(k, [v]) for k, v in self._modelActiveResNames.iteritems()])) # just converting commong active res dict to have list as values which the helpers function needs.
        commonActiveRes = (str(commonActiveResList[0]) if commonActiveResList else '')

        self._avResListWidget.clear()
        for index, res in enumerate(commonRes):
                res = str(res)
                w = QtGui.QListWidgetItem(res)

                if commonActiveRes=='':
                    state = 1
                elif res==commonActiveRes:
                    state = 2
                else:
                    state = 0

                w.setCheckState(state)
                self._avResListWidget.addItem(w)

    def _modelNameOnChangedSingle(self):
        # Getting Selected Model Name
        self._selectedModelName = str(self._modelListWidget.currentItem().text())

        # Updating Available Resolutions
        self._updateAvailableResolution()

    def _showDialog(self, title, msg):
        reply = QtGui.QMessageBox.question(self, title,
                         msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            return True

        return False

    def _offloadBtnOnClicked(self):
        msg = '\n'
        msg += '        Do you want to offoad all models ?           '
        msg += '\n\n'
        title = 'Offload All Models ?'
        if not self._showDialog(title, msg):
            return


        for modelName in self._modelActiveResNames.keys():
            self._modelActiveResNames[modelName] = 'Offloaded'

        for index in range(self._avResListWidget.count()):
            item = self._avResListWidget.item(index)
            if item.text()=='Offloaded':
                self._avResListWidget.setCurrentRow(index)
                item.setCheckState(2)
            else:
                item.setCheckState(0)

    def _viewBtnOnClicked(self):
        viewLogHeader = ''
        viewLogHeader += '-' * 80
        viewLogHeader += '\n'
        viewLogHeader += 'Following changes were made to the Reference Model Resolutions:\n'
        viewLogHeader += '-' * 80
        viewLogHeader += '\n'

        noChange = True
        ctr = 0
        resLog = ''
        for modelName, res in self._modelActiveResNamesOriginal.iteritems():
            commitRes = self._modelActiveResNames[modelName]
            if res!=commitRes:
                noChange = False
                resLog += '%s\n%s  -->  %s\n\n\n\n' % (modelName, res, commitRes)
                ctr += 1

        viewLog = ''

        if noChange:
            viewLog = viewLogHeader + 'No changes to view.'
        else:
            nbChangeLog = '\nTotal Models Changed: %s\n\n\n' % (str(ctr))
            viewLog = viewLogHeader + nbChangeLog + resLog

        if not hasattr(self, 'tw'):
            self.tw = TextWidget()
        else:
            self.tw = None
            self.tw = TextWidget()
        
        self.tw.textEdit.setText(viewLog)
        self.tw.show()

    def _resetBtnOnClicked(self):
        for modelName, res in self._modelActiveResNamesOriginal.iteritems():
            self._modelActiveResNames[modelName] = res

        self._dataChanged = False

        self._updateAvailableResolution()


    def _applyBtnOnClicked(self):
        self._writeScntoc()
        QtCore.QCoreApplication.instance().quit()

    def _cancelBtnOnClicked(self):
        msg = '\n'
        msg += '        Do you want to exit without saving your changes ?           '
        msg += '\n\n'
        title = 'Exit without save ?'

        if self._file:
            if self._dataChanged:
                if not self._showDialog(title, msg):
                    return

        QtCore.QCoreApplication.instance().quit()
        
    def _writeScntoc(self):
        if not self._file:
            return
        
        if not self._dataChanged:
            return
        
        msg = '\n'
        msg += '        Do you want to write changes to the loaded file ?           '
        msg += '\n\n'
        title = 'Save current file ?'
        
        if not self._showDialog(title, msg):
            return
        
        for modelName, activeResName in self._modelActiveResNames.iteritems():
            self._modelDict[modelName]['activeRes'] = [  resDict['resID']
                                                       for resDict in self._modelResData[modelName]
                                                       if resDict['resName']==activeResName][0]

        # Writing changes to the scntoc file
        self._sr.write()     

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        mainWidget = QtGui.QFrame()

        self._mainWidget = MainWidget()
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self._mainWidget, 100)
        mainWidget.setLayout(mainLayout)
        self.setCentralWidget(mainWidget)

        fileOpenAction = QtGui.QAction('&Open', self)
        fileOpenAction.setShortcut('Ctrl+O')
        fileOpenAction.setStatusTip('Open File')
        fileOpenAction.triggered.connect(self._onFileOpen)

        helpAction = QtGui.QAction('Help', self)
        helpAction.setShortcut('F1')
        helpAction.setStatusTip('Help')
        helpAction.triggered.connect(self._onHelpAction)
        
        defaultStyleAction = QtGui.QAction('Default', self)
        defaultStyleAction.setShortcut('Ctrl+1')
        defaultStyleAction.setStatusTip('Default Style Theme : Windowsvista on Windows OS else Plastique')
        defaultStyleAction.triggered.connect(self._onDefaultStyleAction)

        darkStyleAction = QtGui.QAction('Dark', self)
        darkStyleAction.setShortcut('Ctrl+2')
        darkStyleAction.setStatusTip('Generic Dark Style Theme')
        darkStyleAction.triggered.connect(self._onDarkStyleAction)
        
        softStyleAction = QtGui.QAction('Softimage', self)
        softStyleAction.setShortcut('Ctrl+3')
        softStyleAction.setStatusTip('Softimage Style Theme')
        softStyleAction.triggered.connect(self._onSoftStyleAction)
        
        mayaStyleAction = QtGui.QAction('Maya', self)
        mayaStyleAction.setShortcut('Ctrl+4')
        mayaStyleAction.setStatusTip('Maya Style Theme')
        mayaStyleAction.triggered.connect(self._onMayaStyleAction)        

        nukeStyleAction = QtGui.QAction('Nuke', self)
        nukeStyleAction.setShortcut('Ctrl+5')
        nukeStyleAction.setStatusTip('Nuke Style Theme')
        nukeStyleAction.triggered.connect(self._onNukeStyleAction)        

        aboutAction = QtGui.QAction('&About', self)
        aboutAction.setStatusTip('About Resolution Manager')
        aboutAction.triggered.connect(self._onAboutAction)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(fileOpenAction)
        
        editMenu = menubar.addMenu('&Edit')
        themeMenu = editMenu.addMenu('A&pply Themes')
        themeMenu.addAction(defaultStyleAction)
        themeMenu.addAction(darkStyleAction)
        themeMenu.addAction(softStyleAction)
        themeMenu.addAction(mayaStyleAction)
        themeMenu.addAction(nukeStyleAction)

        helpMenu = menubar.addMenu('&Help')
        helpMenu.addAction(helpAction)
        helpMenu.addAction(aboutAction)

        self.move(100, 100)

        self.setWindowTitle("Scenetoc Res Manager v 1.0")

        StyleSheet().setColor(self, app=QtCore.QCoreApplication.instance())
        StyleSheet().setColor(self._mainWidget)
    
    def _onDefaultStyleAction(self):
        self._setTheme('')
 
    def _onDarkStyleAction(self):
        self._setTheme('dark')       

    def _onSoftStyleAction(self):
        self._setTheme('soft')        

    def _onMayaStyleAction(self):
        self._setTheme('maya')

    def _onNukeStyleAction(self):
        self._setTheme('nuke')

    def _setTheme(self, theme=''):
        ss = StyleSheet()
        ss._writePrefs(pref=theme)
        ss.setColor(self._mainWidget)
        ss.setColor(self, app= QtCore.QCoreApplication.instance())        

    def _onFileOpen(self):
        mw = self._mainWidget
        
        mw._writeScntoc()
        
        #if mw._file!=None:
        #    if mw._dataChanged:
        #        msg = '\n'
        #        msg += '        Do you want to save changes in the current file ?           '
        #        msg += '\n\n'
        #        title = 'Save current file ?'
        #        if mw._showDialog(title, msg):
        #            for modelName, activeResName in mw._modelActiveResNames.iteritems():
        #                mw._modelDict[modelName]['activeRes'] = [  resDict['resID']
        #                                                           for resDict in mw._modelResData[modelName]
        #                                                           if resDict['resName']==activeResName][0]
        #
        #            # Writing changes to the scntoc file
        #            mw._sr.write()

        mw._dataChanged = False
        mw._file = None
        mw._hasFileloaded = False


        fg = QtGui.QFileDialog()
        f = str(fg.getOpenFileName(self, 'Open file', '', "Scntoc File (*.scntoc)"))

        mw.load(f)
        mw.run()

    def _onAboutAction(self):
        self._showHelpWidget()

    def _onHelpAction(self):
        self._showHelpWidget(help=True)

    def _showHelpWidget(self, help=False):
        if not hasattr(self, 'hw'):
            self.hw = HelpWidget(help=help)
        else:
            self.hw = None
            self.hw = HelpWidget(help=help)

        self.hw.show()

def run():
    app = QtGui.QApplication(sys.argv)
    am = MainWindow()
    am.show()
    am.raise_()
    app.exec_()
