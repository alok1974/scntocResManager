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
import re
import os
import itertools
from logger import Logger

BASE_COLOR = [170, 190, 210]
SEP1 = '     ('
SEP2 = ')'

def _getNumberFromString(s):
    l = [p for p in s]
    l.reverse()
    n = []
    for p in l:
        if unicode(p).isnumeric():
            n.append(int(p))
        else:
            break
    if not n:
        return

    return str(sum([(pow(10,i) * p) for i, p in enumerate(n)])).zfill(len(n))

def _sortNames(inNames):
    l = []
    for name in inNames:
        number = _getNumberFromString(name)

        if not number:
            number = 0

        try:
            number = int(number)
        except:
            raise Exception('cannot convert %s to a number !' % modelNumber)

        l.append((number, name))

    l.sort()

    return [t[1] for t in l]

def _extractRootAndSort(inNames):
    modelNames = []
    rootNames = []
    d = {}
    for modelName in inNames:
        modelNumber = _getNumberFromString(modelName)
        if modelNumber==None:
            rootName = modelName
        else:
            rootName = modelName[:len(str(modelNumber)) * -1]

        if not d.has_key(rootName):
            d[rootName] = []

        try:
            modelNumber = int(modelNumber)
        except:
            if modelNumber!=None:
                raise Exception('cannot convert %s to a number !' % modelNumber)

        d[rootName].append((modelNumber, modelName, rootName))


    for _, nameTuples in d.iteritems():
        nameTuples = sorted(nameTuples)
        modelNames.extend([t[1] for t in nameTuples])
        rootNames.extend([t[2] for t in nameTuples])

    return modelNames, rootNames

def _sortAndMakeColors(inModelNames):
    sortedNames, extractedRoots = _extractRootAndSort(inModelNames)
    rootNames = list(set(extractedRoots))
    colorComb = [(i, j, k)
                for i in BASE_COLOR
                for j in BASE_COLOR
                for k in BASE_COLOR
                if i!=j and i!=k and j!=k
             ]

    colorList = list(itertools.islice(itertools.cycle(colorComb), None, len(rootNames)))
    rootColors = dict([(rootName, colorList[index])   for index, rootName in enumerate(rootNames)])
    colorDict = {}
    for name in sortedNames:
        for rootName in rootColors:
            if rootName in name:
                colorDict[name] = rootColors[rootName]

    return sortedNames, colorDict

def _getCommonRes(inModelNameList, inModelAvResDict):
    return list(set.intersection(*map(set,[inModelAvResDict[modelName]
                                           for modelName in inModelNameList])))

def _flattenList(inListOfLists, returnUnique=False):
    l = list(itertools.chain(*(inListOfLists)))

    if returnUnique:
        return list(set(l))

    return l

def _reverseDict(inDict):
    d = {}
    for k, v in inDict.iteritems():
        if not d.has_key(v):
            d[v] = []

        d[v].append(k)

    return d

def _getContiguousParts(inList):
    listCopy = inList[:]
    listCopy.sort()
    iterList = listCopy[:]
    parts = []

    while len(iterList):
        c = []
        for index, e in enumerate(iterList):
            if index==0:
                c.append(e)
                listCopy.remove(e)
            else:
                lastElement = iterList[index-1]
                if e==lastElement + 1:
                    c.append(e)
                    listCopy.remove(e)
                else:
                    break
        iterList = listCopy[:]
        parts.append((c[0], c[-1]))

    return parts

def _writeModelNameParts(inModelName, inModelRes):
    return "%s%s%s%s" % (inModelName, SEP1, inModelRes, SEP2)

def _getModelNameParts(inModelNameStr):
    modelName, endPart = inModelNameStr.split(SEP1)
    modelRes, sep = endPart.split(SEP2)
    modelName = modelName.strip()
    modelRes = modelRes.strip()
    return modelName, modelRes

def _replaceWord(inString='', inFind='', inReplace='', inIgnoreCase=False, inWholeWord=False):
    flag = (re.IGNORECASE if inIgnoreCase else 0)
    find = (r'\b({0})\b'.format(inFind) if inWholeWord else inFind)
    pat = re.compile(find, flags=flag)

    return pat.sub(inReplace, inString)

def _getCommonPath(inSelectedModels, inSelectedRes, inResDataDict):
    paths = []
    for modelName in inSelectedModels:
        resData = [data for data in inResDataDict[modelName] if data['resName']==inSelectedRes][0]
        paths.append(resData['resPath'])

    if len(set(paths))==1:
        return paths[0]

    return '       <No Common Path>'