####################################################################################
####################################################################################
##                                                                                ##
##  Scenetoc Resolution Manager (c) 2013 Alok Gandhi (alok.gandhi2002@gmail.com)  ##
##                                                                                ##
##                                                                                ##
##  This program is free software: you can redistribute it and/or modify it       ##
##  under the terms of the GNU General Public License, Version 3, 29 June 2007    ##
##  as published by the Free Software Foundation   <http://fsf.org/>              ##
##  TO view the full license, read license.txt in the folder ../license           ##
##                                                                                ##
####################################################################################
####################################################################################




import os
import itertools

BASE_COLOR = [170, 190, 210]

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

    return sum([(pow(10,i) * p) for i, p in enumerate(n)])

def _makeDisplayGridDataFromModelDict(inNames):
    modelNames = []
    rootNames = []
    d = {}
    for modelName in inNames:
        modelNumber = _getNumberFromString(modelName)
        if modelNumber==None:
            rootName = modelName
        else:
            rootName = modelName[:len(str(modelNumber)) * -1]

        if rootName is str("NM7"):
            print modelName
        #print rootName

        if not d.has_key(rootName):
            d[rootName] = []

        try:
            modelNumber = int(modelNumber)
        except:
            pass

        d[rootName].append((modelNumber, modelName, rootName))


    for _, nameTuples in d.iteritems():
        nameTuples = sorted(nameTuples)
        modelNames.extend([t[1] for t in nameTuples])
        rootNames.extend([t[2] for t in nameTuples])

    return modelNames, rootNames

def _sortAndMakeColors(inModelNames):
    sortedNames, extractedRoots = _makeDisplayGridDataFromModelDict(inModelNames)
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