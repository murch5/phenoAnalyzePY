PATH = '/Users/Ryan/PycharmProjects/plot_managerPY'
import sys
import csv


if not PATH in sys.path:
    sys.path.append(PATH)

# Phenotype data loading and manipulation class object

import pandas as pd
import glob as glob
import os as os

import plot_manager as plot_manager
from violin import violin
from pie import pie
from scatter import scatter


def loadCSVtoPandas(fileName):
    dataFrame = pd.read_csv(fileName, sep=",")

    return dataFrame


class phenoData:
    def getFilesFromDir(self, directory, ext):
        files = glob.glob(os.path.join(directory, ext))

        return files

    def __init__(self, directory):
        self.directory = directory  # directory containing the phenoData to load
        self.fileNames = self.getFilesFromDir(self.directory, "*.csv")
        self.data = self.loadData()
        self.dfNames = self.getNames()

        # View specific variables
        self.viewSetRaw = []
        self.viewSet = []
        self.plotManagers = []
        self.viewNames = []

        self.currView = 0
        self.totalView = 0

        return

    def getNames(self):

        names = []
        for q in self.fileNames:
            t = os.path.split(q)
            names.append(t[1][:-4])
        return names

    def getDFIndexFromName(self, name):

        index = self.dfNames.index(name)
        return index

    def loadViewSets(self, dir):

        viewFile = self.getFilesFromDir(dir, "*.viewSet")

        for i in viewFile:
            with open(i, 'r') as csvfile:
                viewSetFile = csv.reader(csvfile, delimiter=",")
                for row in viewSetFile:
                    self.viewSetRaw.append(row)

        return

    def arrayCheck(self, entry):
        if ";" in entry:
            entry = entry.split(";")

        return entry

    def parseRawViewData(self):

        viewIndices = []
        line = -1

        for q in self.viewSetRaw:
            line += 1
            if q[0][0] == ">":
                viewIndices.append(line)

        numViews = len(viewIndices)

        viewIndices.append(len(self.viewSetRaw))

        for i in range(0, numViews):
            title = self.viewSetRaw[viewIndices[i]][0][1:]
            self.viewNames.append(title)
            entryList = []
            for q in range(viewIndices[i] + 1, (viewIndices[i + 1])):
                temp = [self.arrayCheck(self.viewSetRaw[q][0]), self.arrayCheck(self.viewSetRaw[q][1]),
                        self.arrayCheck(self.viewSetRaw[q][2]), self.arrayCheck(self.viewSetRaw[q][3]),
                        self.arrayCheck(self.viewSetRaw[q][4]), self.arrayCheck(self.viewSetRaw[q][5]),
                        self.arrayCheck(self.viewSetRaw[q][6]), self.arrayCheck(self.viewSetRaw[q][7])]
                entry = pd.Series(temp, name=self.viewSetRaw[q][0],
                                  index=["title", "position", "plotType", "dataSet", "data", "func", "dataArgs",
                                         "plotArgs"])
                entryList.append(entry)

            view = pd.DataFrame(entryList)
            self.viewSet.append(view)

        return

    def parseView(self):

        viewIndex = -1

        for x in self.viewSet:

            viewIndex += 1
            newplot = plot_manager.plot_manager(self.viewNames[viewIndex])

            for index, row in x.iterrows():
                dataTemp = self.extractData(row[3], row[4], row[6])

                newplot.addPlot(row[0], row[1], plot_manager.chartTypes[(row[2])], dataTemp, row[7])

            self.plotManagers.append(newplot)

        return

    def setView(self, view):
        self.currView = view
        return

    def displayAllViews(self):

        for plots in self.plotManagers:
            plots.drawPlots()

        self.plotManagers[0].showPlot()

        return

    def loadData(self):

        dataSet = []
        for i in self.fileNames:
            data = loadCSVtoPandas(i)
            dataSet.append(data)

        return dataSet

    sortType = {"ascend":True,"descend":False}

    def sort(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_values(by=0,ascending=phenoData.sortType[direction],inplace=True)
        return newdata

    def sortIndex(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_index(ascending=phenoData.sortType[direction],inplace=True)
        return newdata


    def filterByVal(self, data, arg):

        newdata = pd.DataFrame(data)

        for x in arg:
            newdata = newdata.query(x)

        newdata.reset_index(drop=True,inplace=True)

        return newdata

    def groupby(self, data, arg):

        newdata = data[:]

        newdata = newdata.groupby(by=arg).size()

        return newdata

    def groupbyval(self, data, arg):

        newdata = data[:]

        if "inclNA" in arg:
            newdata.fillna("n/a", inplace=True)

        if "Delim" in arg:
            newDatasplit = newdata.str.split(";").apply(pd.Series, 1).stack()

            newdata = newDatasplit

        newdata = newdata.groupby(newdata).size()
        newdata.columns = ["Index", "GroupedCounts"]

        return newdata

    def filterByID(self):
        return

    dataFunc = {"filterByVal": filterByVal, "groupBy": groupby, "groupByVal": groupbyval, "sort":sort, "sortIndex":sortIndex}

    def parseArgs(self, args):
        argList = []
        if args.any():
            for i in args:
                q = i.split("=", 1)
                argList.append(q)

        return argList

    def evaluateArg(self, data, arg):
        temp = data
        argList = arg[1].split("~")
        temp = phenoData.dataFunc[arg[0]](self, temp, argList)

        return temp

    def extractData(self, dataSet, subset, args):

        pdArg = pd.Series(args)
        f = self.parseArgs(pdArg)

        # slicedData = self.data[int(dataSet)]

        slicedData = self.data[self.getDFIndexFromName(dataSet)]

        df = slicedData[subset]

        for x in f:
            if x != ["0"]:
                df = self.evaluateArg(df, x)

        return df


f = phenoData("test/")

f.loadViewSets("view/")
f.parseRawViewData()
f.parseView()
f.setView(0)
f.displayAllViews()
