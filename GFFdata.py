import pandas as pd
import numpy as np


class GFF():
    def __init__(self, fileName):
        self.GFFdata = self.loadGFF(fileName)
        self.currLabels = []
        return

    def loadGFF(self, fileName):

        tempData = pd.read_table(fileName, comment="#", header=None)
        tempData.columns = ["seqname", "source", "feature", "start", "end", "score", "strand", "frame", "attribute"]

        attributes = []

        for x in tempData["attribute"]:

            attributeSet = []
            attribute = x.split(";")

            for y in attribute:
                newAttribute = y.split("=")

                attributeSet.append(newAttribute)

            attrDict = dict(attributeSet)

            attributes.append(attrDict)

        tempData["attrDict"] = attributes

        return tempData

    def getChain(self, chainName):

        searchQuery = "feature=='" + chainName + "'"
        chainData = self.GFFdata.ix(searchQuery)[0]
        start = chainData["start"]
        end = chainData["end"]
        chain = [start, end]

        return chain

    def getFeature(self, featureName):

        searchQuery = "feature=='" + featureName + "'"
        featureData = self.GFFdata.query(searchQuery)

        return featureData

    def getData(self):
        return self.GFFdata

    def getDictValues(self, dictKey):

        labels = []
        for x in self.GFFdata["attrDict"]:
            labels.append(x.get(dictKey))

        return labels

    def setLabels(self, newLabels):
        self.currLabels = newLabels
        return
