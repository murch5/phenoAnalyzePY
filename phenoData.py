PATH = '/Users/Ryan/PycharmProjects/plot_managerPY'
import sys

print(sys.path)
if not PATH in sys.path:
    sys.path.append(PATH)

# Phenotype data loading and manipulation class object

import pandas as pd
import glob as glob
import os as os

from plot_manager import plot_manager
from violin import violin
from pie import pie
from scatter import scatter


def loadCSVtoPandas(fileName):
    dataFrame = pd.read_csv(fileName, sep=",")

    return dataFrame


class phenoData():
    def getFilesFromDir(self):
        files = glob.glob(os.path.join(self.directory, "*.csv"))

        return files

    def __init__(self, directory):
        self.directory = directory  # directory containing the phenoData to load
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

        return dataSet

    def extractData(self, dataSet, selection, columns, groupBy=0):

        slicedData = self.data[dataSet]
        slicedData = slicedData[columns]
        return slicedData


f = phenoData("test/")

c = plot_manager("test1")
c.setStyleSheet("seaborn-muted")
#c.addPlot(violin, f.extractData(0, 0, ["AffStatus", "AgeDxYrs",], 0), 211)
c.addPlot(scatter, f.extractData(0, 0, ["AgeDxYrs", "AgeDxYrs",], 0), 221)
c.addPlot(pie, (20, 50, 30), 223)
c.addPlot(pie, (1, 2, 2, 2, 1, 1, 1), 224)
c.drawPlots()
c.captureImage("")

print(f)
