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
        self.plotManagers = []
        self.totalView = 0

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

    def extractData(self, dataSet, columns, filters=[], groupBySum=[], sizeFilter=[]):

        slicedData = self.data[dataSet]

        if filters != 0:
            for i in filters:
                # slicedData = slicedData.where(i)
                slicedData = slicedData.query(i)

        df = slicedData[columns]

        if groupBySum != 0:
            r = slicedData.groupby(groupBySum).size()
            df = r
            print(df)
            print(type(df))
            if sizeFilter!=0:
                for i in sizeFilter:
                    df = df[eval(i)]


        return df




f = phenoData("test/")

c = plot_manager("Classification by Dx")
d = plot_manager("Age by Severity")
e = plot_manager("Summary of EIM")
g = plot_manager("Summary of Co-morbidities")
e.setStyleSheet("seaborn-muted")
c.setStyleSheet("seaborn-muted")
d.setStyleSheet("seaborn-muted")


c.addPlot(violin, f.extractData(2, ["InitDx_Categorized", "AgeDxYrs", "Gender_Categorized"],
                                ["Gender_Categorized==\"Male\" | Gender_Categorized==\"Female\"",
                                 "InitDx_Categorized!=\"Await Dx\" & InitDx_Categorized!=\"Atypical CD\" "], 0), 311)
c.addPlot(violin, f.extractData(2, ["InitDx_Categorized", "aggregateMean_ByID", "Gender_Categorized"],
                               ["Gender_Categorized==\"Male\" | Gender_Categorized==\"Female\"",
                                "InitDx_Categorized!=\"Await Dx\" & InitDx_Categorized!=\"Atypical CD\" "], 0), 312)
c.addPlot(pie, f.extractData(2, ["InitDx_Categorized"], 0, groupBySum=["InitDx_Categorized"],sizeFilter=["df>2"]), 325, title="Initial Dx")
c.addPlot(pie, f.extractData(2, ["AffStatus"], 0, groupBySum=["AffStatus"],sizeFilter=["df>200"]), 326,title="Affection Status")

e.addPlot(pie, f.extractData(2, ["Data"], 0, groupBySum=["Data"],sizeFilter=["df>5"]),111,title="Autoimmune")
g.addPlot(pie, f.extractData(2, ["EIM"], 0, groupBySum=["EIM"],sizeFilter=["df>5"]),111,title="EIM")


# d.addView("Gender Type")
d.addPlot(scatter, f.extractData(2, ["AgeDxYrs","aggregateMean_ByID"],["AffStatus==2"],0), 111,title="Weights = 1.0")
# c.addPlot(pie, (20, 50, 30), 223)
# c.addPlot(pie, (1, 2, 2, 2, 1, 1, 1), 224)
# c.setView(0)
# d.setView(0)
#c.drawPlots()
c.drawPlots()
d.drawPlots()
e.drawPlots()
g.drawPlots()
# d.drawPlots()
d.showPlot()

# c.captureImage("")

print(f)
