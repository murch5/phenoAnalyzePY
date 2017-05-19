#PATH = '/Users/Ryan/PycharmProjects/plot_managerPY'
import sys
import csv
import generateFrameSet as gfs
import processingFunc as process

#if not PATH in sys.path:
   # sys.path.append(PATH)

# Phenotype data loading and manipulation class object

import pandas as pd
import glob as glob
import os as os

import plotmanager.plot_manager as pltmanager

from GFFdata import GFF


class phenoData:
    def getFilesFromDir(self, directory, ext):

        fileName = []
        self.dataDir = glob.glob("data/*/")

        for y in self.dataDir:
            dirFiles = glob.glob(os.path.join(y, "*"))
            self.dataDirNames.append(y)
            fileName.append(dirFiles)

        return fileName

    def getViewsFromDir(self, directory):

        dirFiles = glob.glob(os.path.join(directory, "*.viewSet"))

        return dirFiles

    def __init__(self, directory):
        self.directory = directory  # directory containing the phenoData to load
        self.dataDir = []
        self.dataDirNames = []
        self.fileNames = self.getFilesFromDir(self.directory, "*.csv")
        self.data = self.loadData()
        self.dfNames = self.getNames()
        self.figureArgList = []

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
            for x in q:
                r = os.path.basename(x)
                t = os.path.splitext(r)

                names.append(t[0])

        return names

    def getDFIndexFromName(self, name):

        index = self.dfNames.index(name)
        return index

    def loadViewSets(self, dir):

        viewFile = self.getViewsFromDir(dir)

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
        figureArgList = []

        for i in range(0, numViews):
            figureParam = self.viewSetRaw[viewIndices[i]][0][1:]
            figureParam = figureParam.split(",")
            self.viewNames.append(figureParam[0])
            self.figureArgList.append(figureParam[1:])

            entryList = []
            for q in range(viewIndices[i] + 1, (viewIndices[i + 1])):
                temp = [self.arrayCheck(self.viewSetRaw[q][0]), self.arrayCheck(self.viewSetRaw[q][1]),
                        self.arrayCheck(self.viewSetRaw[q][2]), self.arrayCheck(self.viewSetRaw[q][3]),
                        self.arrayCheck(self.viewSetRaw[q][4]), self.arrayCheck(self.viewSetRaw[q][5]),
                        self.arrayCheck(self.viewSetRaw[q][6]), self.arrayCheck(self.viewSetRaw[q][7]),
                        self.arrayCheck(self.viewSetRaw[q][8])]
                entry = pd.Series(temp, name=self.viewSetRaw[q][0],
                                  index=["title", "position", "plotType", "dataSet", "data", "func", "dataArgs",
                                         "plotArgs", "annotate"])
                entryList.append(entry)

            view = pd.DataFrame(entryList)
            self.viewSet.append(view)

        return

    def parseView(self):

        viewIndex = -1

        for x in self.viewSet:

            viewIndex += 1
            newplot = pltmanager.plot_manager(self.viewNames[viewIndex], self.figureArgList[viewIndex])

            for index, row in x.iterrows():
                dataTemp = self.extractData(row[3], row[4], row[6])

                processTemp = self.processData(dataTemp, row[5])

                newplot.addPlot(row[0], row[1], pltmanager.chartTypes[(row[2])], processTemp, row[7], row[8])

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

    def loadCSV(self, fileName):

        dataFrame = pd.read_csv(fileName, sep=",")

        return dataFrame

    def loadTIF(self, fileName):

        data = gfs.loadTIF(fileName)

        return data

    def loadDir(self, directory):

        files = glob.glob(os.path.join(directory, "*.*"))

        data = gfs.generateFrameSet(files)

        return data

    def loadGFF(self, fileName):

        data = GFF(fileName)

        return data

    fileTypes = {"csv": loadCSV, "tif": loadTIF, "": loadDir, "gff": loadGFF}

    def loadData(self):

        dataSet = []
        for i in self.fileNames:
            for q in i:
                extension = os.path.splitext(q)[1][1:]
                data = phenoData.fileTypes[extension](self, q)
                dataSet.append(data)

        return dataSet

    sortType = {"ascend": True, "descend": False}

    def sort(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_values(by=0, ascending=phenoData.sortType[direction], inplace=True)
        return newdata

    def sortIndex(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_index(ascending=phenoData.sortType[direction], inplace=True)
        return newdata

    def filterByVal(self, data, arg):

        newdata = pd.DataFrame(data)

        for x in arg:
            newdata = newdata.query(x)

        newdata.reset_index(drop=True, inplace=True)

        return newdata

    def filterNA(self, data, arg):

        newdata = pd.DataFrame(data)

        newdata = newdata.dropna(0, subset=[arg])

        return newdata

    def groupby(self, data, arg):

        newdata = data[:]

        newdata = newdata.groupby(by=arg).size()

        return newdata

    def groupbyval(self, data, arg):

        print(type(data))

        if isinstance(data, pd.DataFrame):
            print(data)
            newdata = data.ix[:, 0]

        else:
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

    dataFunc = {"filterByVal": filterByVal, "groupBy": groupby, "groupByVal": groupbyval, "sort": sort,
                "sortIndex": sortIndex, "filterNA": filterNA}
    processFunc = {"gaussian": process.gaussian, "variance": process.variance, "stddev": process.stddev}

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

    def evaluateProcess(self, data, arg):
        temp = data
        argList = arg[1].split("~")
        temp = phenoData.processFunc[arg[0]](temp, argList)

        return temp

    def extractData(self, dataSet, subset, args):

        pdArg = pd.Series(args)
        f = self.parseArgs(pdArg)

        # slicedData = self.data[int(dataSet)]

        slicedData = self.data[self.getDFIndexFromName(dataSet)]
        print(slicedData)
        print(subset)
        if (subset != "FULL"):
            df = slicedData[subset]
        else:
            df = slicedData

        for x in f:
            if x != ["0"]:
                df = self.evaluateArg(df, x)

        return df

    def processData(self, dataSet, args):

        tempData = dataSet
        pdArg = pd.Series(args)
        argList = self.parseArgs(pdArg)

        for x in argList:
            if x != ["0"]:
                tempData = self.evaluateProcess(tempData, x)

        return tempData

f = phenoData("test/")

f.loadViewSets("view/")

f.parseRawViewData()
f.parseView()
f.setView(0)
f.displayAllViews()
# f.plotManagers[0].startAnim()
