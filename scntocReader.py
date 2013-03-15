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
import xml.dom.minidom
from logger import Logger

ERROR_TYPES = {
                0 : 'No .scntoc file specified !',
                1 : 'File - %s does not exist',
                2 : '',
              }

class ScenetocReader(object):
    MODEL_ATTRS = {'name': 'resName', 'id': 'resID', 'href': 'resPath'}

    def __init__(self, file="", *args, **kwargs):
        super(ScenetocReader, self).__init__(*args, **kwargs)

        self._file = file
        self._data = None
        self._models = {}
        self._prettyData = ""
        self._dataRead = False
        self._hasError = False

        self._assert()

    def _assert(self):
        if self._file=="":
            self._hasError = True
            self._errorType = 0
            self._error = 'No .scntoc file specified !'

        if not os.path.exists(self._file):
            self._hasError = True
            self._errorType = 1
            self._error = 'File - %s does not exist' % self._file

        try:
            self._data = xml.dom.minidom.parse(self._file)
        except:
            self._hasError = True
            self._errorType = 2
            self._error = 'Unable to read data - invalid or corrupt data in file - %s!' % self._file

    def _setPrettyData(self, showAllRes=False):
        sepLength = 80
        if not self._dataRead:
            self.read()

        if not self._models:
            self._hasError = True
            raise Exception('No Models found in the Models Dict !')

        s = '\n'

        for modelName, data in self._models.iteritems():
            s += '%s\n' % ('-' * sepLength)
            s += '  %s' % modelName
            for modelAttrName, modelAttrValue in data.iteritems():
                if modelAttrName=='resData':
                    if showAllRes:
                        for index, resData in enumerate(modelAttrValue):
                            s += '\n  -> Resolution %s\n' % index
                            for resAttrName, resAttrValue in resData.iteritems():
                                s += '      %s: %s\n' % (resAttrName, resAttrValue)
                        s += '\n\n'
                elif modelAttrName=='activeRes':
                    s += '  -> Active Resolution: %s\n' % (data['activeResName'])
                    s += '%s\n' % ('-' * sepLength)
            s += '\n\n'

        self._prettyData = s

    def read(self):
        if self._hasError:
            raise Exception(self._error)

        modelData = self._data.getElementsByTagName("Models")[0].childNodes
        for model in modelData:
            if model.nodeType == model.ELEMENT_NODE and model.nodeName == "Model" :
               modelName = model.attributes["name"].value
               activeRes = model.attributes["active_resolution"].value
               self._models[modelName] = {'model': model, 'activeRes': activeRes, 'resData': []}

               for childNode in model.childNodes:
                if childNode.nodeType==childNode.ELEMENT_NODE:
                    self._models[modelName]['resData'].append(dict([(v, r'%s' % str(childNode.attributes[k].value)) for k, v in self.MODEL_ATTRS.iteritems()]))

        # Adding active res names
        for modelName, data in self._models.iteritems():
            if not self._models[modelName].has_key('activeResName'):
                self._models[modelName]['activeResName'] = [d['resName'] for d in data['resData'] if d['resID'] == data['activeRes']][0]

        self._dataRead = True


    def getPrettyData(self, showAllRes=False):
        self._setPrettyData(showAllRes=showAllRes)
        return self._prettyData

    def getModels(self):
        if not self._dataRead:
            self.read()

        return self._models

    def offLoadAll(self):
        if not self._dataRead:
            self.read()

        for _, data in self._models.iteritems():
            data['activeRes'] = '0'

    def write(self):
        if not self._dataRead:
            self.read()

        dataChanged = False
        for modelName, modelData in self._models.iteritems():
            modelNode = modelData['model']

            if modelNode.attributes["active_resolution"].value != modelData['activeRes']:
                modelNode.attributes["active_resolution"].value = modelData['activeRes']
                dataChanged = True

            for childNode in modelNode.childNodes:
                if childNode.nodeType==childNode.ELEMENT_NODE:
                    id = childNode.attributes['id'].value
                    path = childNode.attributes['href'].value

                    changedPath = [d['resPath'] for d in modelData['resData'] if d['resID']==id][0]
                    if path!=changedPath:
                        childNode.attributes['href'].value = changedPath
                        dataChanged = True

        if dataChanged:
            with open(self._file, 'w') as f:
                self._data.writexml(f)

if __name__ == '__main__':
    f = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sampleSceneTocFiles', 'sample.scntoc')
    sr = ScenetocReader(f)
    print sr.getModels()
    print sr.getPrettyData(showAllRes=False)