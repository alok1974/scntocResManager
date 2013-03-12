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
import functools
from PyQt4 import QtCore, QtGui

from widgets import MainWidgetUI, TextWidget, HelpWidget, StyleSheet, RecentFiles
from scntocReader import ScenetocReader
import helpers
import msgHandler
WIN_TITLE = "Scenetoc Res Manager"

class MainWidget(MainWidgetUI):
    def __init__(self, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self._file = None
        self._dataChanged = False
        self._connected = False

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
            else:
                self.tw = None
                self.tw = TextWidget()

            errStr = ''
            errStr += 'There were following error/errors in opening file:\n\n'
            errStr += self._sr._error

            self.tw.textEdit.setText(errStr)
            self.tw.setWindowTitle('File Open Error')
            self.tw.setGeometry(100, 100, 500, 250)
            self.tw.show()

            return

        self._modelDict = self._sr.getModels()
        self._initData()
        self._initWidgets()
        self._hasFileloaded = True

        # Connect Signals
        if not self._connected:
            self._connectSignals()

    def _initData(self):
        self._selectedModelName = ''
        self._selectedModelNames = []
        self._selectedResName = ''
        self._mutliSelected = False
        self._modelNames, self._modelNameColors = helpers._sortAndMakeColors(self._modelDict.keys())
        self._nbModels = len(self._modelNames)
        self._modelNameIndices = dict([(modelName, index) for index, modelName in enumerate(self._modelNames)])
        self._modelActiveResNames = dict([(k, v['activeResName']) for k, v in self._modelDict.iteritems()])
        self._modelActiveResNamesOriginal = dict([(k, v['activeResName']) for k, v in self._modelDict.iteritems()])
        self._modelResData = dict([(k, v['resData']) for k, v in self._modelDict.iteritems()])
        self._modelAvailableResNames = dict([(modelName, [d['resName']for d in modelData['resData']]) for modelName, modelData in self._modelDict.iteritems()])
        self._allAvailableRes = helpers._flattenList([resNames for _, resNames in self._modelAvailableResNames.iteritems()], returnUnique=True)

    def _initWidgets(self):
        self._modelListWidget.clear()
        self._avResListWidget.clear()
        self._filterListWidget.clear()
        self._resIDLineEdit.setText('')
        self._resPathLineEdit.setText('')
        self._nbModelLabel.setText('')

        # Init Model Name List Widget
        self._updateModelListWidget()

        # Init Filter List Widget
        self._updateAllResListWidget()

        # Init Available Res Names List Widget
        self._updateAvailableResolution()

    def _updateModelListWidget(self, inModelNames=[]):
        self._modelListWidget.clear()

        if not inModelNames:
            inModelNames = self._modelNames

        for modelName in inModelNames:
            modelNameStr = helpers._writeModelNameParts(modelName, self._modelActiveResNames[modelName])
            w = QtGui.QListWidgetItem(modelNameStr)
            r, g, b = self._modelNameColors[modelName]
            w.setBackground(QtGui.QColor(r, g, b))
            w.setForeground(QtGui.QColor(0, 0, 0))
            self._modelListWidget.addItem(w)


        self._modelListWidget.setCurrentRow(0)
        modelName, modelRes = helpers._getModelNameParts(str(self._modelListWidget.currentItem().text()))
        self._selectedModelName = modelName
        self._activeResName = modelRes

        self._nbModelLabel.setText('<b>  <i>Total Models : %s</i></b>' % str(len(inModelNames)))
        self._nbSelectedModelLabel.setText('<b>  <i>Selected Models : 1</i></b>')
		
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

    def _updateAllResListWidget(self):
        w = QtGui.QListWidgetItem('All')
        w.setCheckState(2)
        self._filterListWidget.addItem(w)

        for resName in self._allAvailableRes:
            w = QtGui.QListWidgetItem(resName)
            w.setCheckState(2)
            self._filterListWidget.addItem(w)

    # Signal Connections
    def _connectSignals(self):
        self._avResListWidget.currentItemChanged.connect(self._resolutionOnChanged)
        self._avResListWidget.itemChanged.connect(self._checkBoxOnClicked)
        self._filterListWidget.itemChanged.connect(self._filterOnClicked)
        self._modelListWidget.itemSelectionChanged.connect(self._modelNameOnSelectionChange)
        self._offloadBtn.clicked.connect(self._offloadBtnOnClicked)
        self._viewBtn.clicked.connect(self._viewBtnOnClicked)
        self._resetBtn.clicked.connect(self._resetBtnOnClicked)
        self._applyBtn.clicked.connect(self._applyBtnOnClicked)
        self._cancelBtn.clicked.connect(self._cancelBtnOnClicked)
        self._applyFilterBtn.clicked.connect(self._applyFilterBtnOnClicked)
        self._resetFilterBtn.clicked.connect(self._resetFilterBtnOnClicked)
        self._connected = True

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
            dataChanged = False
            for modelName in self._selectedModelNames:
                dataChanged = self._setActiveResolution(item, modelName)
            self._dataChanged = dataChanged
        else:
            self._dataChanged = self._setActiveResolution(item, self._selectedModelName)

        self._updateModelNamesWithRes(newRes=str(item.text()))

    def _updateModelNamesWithRes(self, newRes=''):
        selectionModel = self._modelListWidget.selectionModel()

        indices = []
        for qModelIndex in selectionModel.selectedRows():
            index = qModelIndex.row()
            modelNameItem = self._modelListWidget.item(index)
            modelName, modelRes = helpers._getModelNameParts(str(modelNameItem.text()))
            modelNameStr = helpers._writeModelNameParts(modelName, newRes)
            modelNameItem.setText(modelNameStr)

    def _setActiveResolution(self, inItem, inModelName):
            clickedRes = str(inItem.text())
            currentRes = self._modelActiveResNamesOriginal[inModelName]
            if clickedRes==currentRes:
                return False
            else:
                self._modelActiveResNames[inModelName] = str(inItem.text())
                return True

    def _filterOnClicked(self, item):
        self._handleFilterClicks(item)

    def _handleFilterClicks(self, inItem, doubleClick=False):
        if str(inItem.text())=='All':
            for index in range(self._filterListWidget.count()):
                thisItem = self._filterListWidget.item(index)
                self._filterListWidget.blockSignals(True) # blocking signals so the func does not go in recursion
                thisItem.setCheckState(inItem.checkState())
                self._filterListWidget.blockSignals(False)

            return

        state = 2
        for index in range(1, self._filterListWidget.count()):
            thisItem = self._filterListWidget.item(index)
            if thisItem.checkState()!=2:
                state = 0

        self._filterListWidget.blockSignals(True) # blocking signals so the func does not go in recursion
        self._filterListWidget.item(0).setCheckState(state)
        self._filterListWidget.blockSignals(False)

    def _modelNameOnSelectionChange(self):
        nbSelectedModels = len(self._modelListWidget.selectedItems())
        if nbSelectedModels > 1:
            self._mutliSelected = True
            self._modelNameOnChangedMulti()
            self._resPathLineEdit.setText("<multiple selection>")
            self._resIDLineEdit.setText("<multiple selection>")
            self._nbSelectedModelLabel.setText('<b>  Selected Models : </b><b>%s</b>' % str(nbSelectedModels))

        else:
            self._mutliSelected = False
            self._modelNameOnChangedSingle()
            self._nbSelectedModelLabel.setText('<b>  Selected Models : 1</b>')

    def _modelNameOnChangedMulti(self):
        self._selectedModelNames = [helpers._getModelNameParts(str(item.text()))[0] for item in self._modelListWidget.selectedItems()]
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
        self._selectedModelName = helpers._getModelNameParts(str(self._modelListWidget.currentItem().text()))[0]

        # Updating Available Resolutions
        self._updateAvailableResolution()

    def _showDialog(self, title, msg):
        reply = QtGui.QMessageBox.question(self, title,
                         msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply==QtGui.QMessageBox.Yes:
            return True

        return False

    def _offloadBtnOnClicked(self):
        if not msgHandler._pop(self, 101):
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

        self._resetFilterBtnOnClicked()

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

        self.tw.setWindowTitle('Model Resolution Change Log')
        self.tw.textEdit.setText(viewLog)
        self.tw.show()

    def _resetBtnOnClicked(self):
        if not self._dataChanged:
            msgHandler._pop(self, 1)
            return

        if not msgHandler._pop(self, 102):
            return

        for modelName, res in self._modelActiveResNamesOriginal.iteritems():
            self._modelActiveResNames[modelName] = res

        self._dataChanged = False
        self._updateAvailableResolution()
        self._resetFilterBtnOnClicked()

    def _applyFilterBtnOnClicked(self):
        allState = 0
        selectedRes = []
        for i in range(self._filterListWidget.count()):
            item = self._filterListWidget.item(i)
            state = item.checkState()
            allState += state
            if state==2:
                selectedRes.append(str(item.text()))

        if not allState:
            msgHandler._pop(self, 3)
            return

        selectedResToModel = helpers._reverseDict(self._modelActiveResNames)

        modelNames = []
        for resName in selectedRes:
            modelsWithThisRes = selectedResToModel.get(resName)
            if modelsWithThisRes:
                modelNames.extend(modelsWithThisRes)

        modelNames = list(set(modelNames))

        modelNames, _ = helpers._sortAndMakeColors(modelNames)

        if not modelNames:
            msgHandler._pop(self, 4, extraArgs=[selectedRes])
            return

        self._updateModelListWidget(inModelNames=modelNames)

    def _resetFilterBtnOnClicked(self):
        self._filterListWidget.item(0).setCheckState(2)
        self._updateModelListWidget()

    def _applyBtnOnClicked(self):
        self._writeScntoc()

    def _cancelBtnOnClicked(self):
        if self._closeMsg()==1:
            return

        QtCore.QCoreApplication.instance().quit()

    def _writeScntoc(self, suppressMsg=False):
        if not self._file:
            return

        if not self._dataChanged:
            if not suppressMsg:
                msgHandler._pop(self, 5)

            return

        if not msgHandler._pop(self, 103):
            return

        for modelName, activeResName in self._modelActiveResNames.iteritems():
            self._modelDict[modelName]['activeRes'] = [  resDict['resID']
                                                       for resDict in self._modelResData[modelName]
                                                       if resDict['resName']==activeResName][0]

        # Writing changes to the scntoc file
        self._sr.write()

        self._dataChanged = False

        if not suppressMsg:
            QtCore.QCoreApplication.instance().quit()

    def _closeMsg(self):
        if self._file:
            if self._dataChanged:
                if not msgHandler._pop(self, 104):
                    return 1

class MainWindow(QtGui.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        mainWidget = QtGui.QFrame()

        self._mainWidget = MainWidget()
        self._recentFiles = RecentFiles()

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

        self._recentMenu = fileMenu.addMenu('&Recent Files')
        self._updateRecentMenu()

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

        self.setWindowTitle(WIN_TITLE)

        StyleSheet().setColor(self, app=QtCore.QCoreApplication.instance())
        StyleSheet().setColor(self._mainWidget)

    def _updateRecentMenu(self):
        self._recentMenu.clear()
        files = self._recentFiles._fetchRecent()

        for file in files:
            fileAction = QtGui.QAction(file, self)
            fileAction.triggered.connect(functools.partial(self._fileOpenMappedSlot, file))
            self._recentMenu.addAction(fileAction)

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

    def _fileOpenMappedSlot(self, inFile):
        if not os.path.exists(inFile):
            msgHandler._pop(self, 6, extraArgs=[inFile])
            self._recentFiles._removeFile(inFile)
            self._updateRecentMenu()
            return

        mw = self._mainWidget

        mw._writeScntoc(suppressMsg=True)

        mw._dataChanged = False
        mw._file = None
        mw._hasFileloaded = False

        mw.load(inFile)
        mw.run()

        self._recentFiles._addFile(inFile)
        self._updateRecentMenu()
        self.setWindowTitle("%s      %s" % (WIN_TITLE, inFile))

    def _onFileOpen(self, inFile=''):
        mw = self._mainWidget

        mw._writeScntoc(suppressMsg=True)

        mw._dataChanged = False
        mw._file = None
        mw._hasFileloaded = False

        if not inFile:
            fg = QtGui.QFileDialog()
            f = str(fg.getOpenFileName(self, 'Open file', '', "Scntoc File (*.scntoc)"))

        mw.load(f)
        mw.run()

        self._recentFiles._addFile(f)
        self._updateRecentMenu()
        self.setWindowTitle("%s      %s" % (WIN_TITLE, inFile))


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

    def closeEvent(self, event):
        mw = self._mainWidget
        if mw._file:
            if mw._dataChanged:
                if not msgHandler._pop(self, 104):
                    event.ignore()

def run():
    app = QtGui.QApplication(sys.argv)
    am = MainWindow()
    am.show()
    am.raise_()
    app.exec_()
