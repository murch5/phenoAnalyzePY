#Phenotype data loading and manipulation class object

import pandas as pd
import glob as glob
import os as os



def loadCSVtoPandas(fileName):
    dataFrame = pd.read_csv(fileName, sep=",")

    return dataFrame

class phenoData():

    def getFilesFromDir(self):
        files = glob.glob(os.path.join(self.directory,"*.csv"))
        print(files)
        return files

    def __init__(self, directory):
        self.directory = directory #directory containing the phenoData to load
        self.fileNames = self.getFilesFromDir()
        self.data = self.loadData()
        self.dfNames = self.getNames()

        print(self.dfNames)
        return

    def getNames(self):

        names = []
        for q in self.fileNames:
            t = os.path.split(q)
            names.append(t[1][:-4])
        return names
    def loadData(self):

        dataSet = []
        for i in self.fileNames:
            data = loadCSVtoPandas(i)
            dataSet.append(data)
            print(dataSet)
        return dataSet

    def extractData(self,dataSet,selection,columns,groupBy):

        slicedData = self.data[dataSet]
        slicedData = slicedData[columns]
        return slicedData

f = phenoData("test/")

f.extractData(0,0,["MuiseLabID","FamilyStatus"],0)
print(f)