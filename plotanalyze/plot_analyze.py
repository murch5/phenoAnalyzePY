
#Imports
import csv
import getopt as getopt
import glob as glob
import os as os
import sys as sys
import pandas as pd

#Import plot manager
import plotmanager.plot_manager as pltmanager


#Import plot_analyze packages and modules
from plotanalyze import processingFunc as process, generateFrameSet as gfs
from plotanalyze.datatype.GFFdata import GFF

import datatypes as dt

#Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))

#Constant for version number
VERSION = "0.1.1"

#Dictionary containing encoding for data types
data_types = {}
data_types.update(dict.fromkeys(["csv","tsv"],dt.table.Table))
data_types.update(dict.fromkeys(["tif","png"],dt.image.Image))


class PlotAnalyze:

    def deploy_data(self, input="./input/"):
        #Deploy data function
        print("INFO     Deploying data...")
        #Get the name of all directories in current working directory
        #Check if input directory already exists

        if os.path.isfile(input):
            extension = os.path.splitext(input)[1]
            if extension == ".txt" or extension == "":
                print("INFO         Input file list detected")
            elif extension == ".gz" or extension == ".tgz":
                print("INFO         Input gzip tar ball detected")
                return
        elif os.path.exists(input):
            print("INFO         Input path detected")
            print("INFO         Compiling data file list...")
            self.data_filelist = glob.glob(input + "**/*.*",recursive=True)
            print(self.data_filelist)

        for file in self.data_filelist:
            ext = os.path.splitext(file)[1][1:]
            data_temp = data_types[ext]()
            data_temp.set_filename(file)
            self.data.append(data_temp)

            #self.data.append(

            print(ext)

        return

    def load_viewset(self):
        return
    def process_viewset(self):
        return
    def load_data(self):
        return
    def process_data(self):
        return
    def show(self):
        return

    def cleanup(self):
        return
    def getFilesFromDir(self, directory):

        fileName = []
        self.dataDir = glob.glob("./input/*")

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
        self.fileNames = self.getFilesFromDir(self.directory)
        self.data = self.loadData()
        self.dfNames = self.getNames()
        self.figureArgList = []

        self.data_filelist = None

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
                data = PlotAnalyze.fileTypes[extension](self, q)
                dataSet.append(data)

        return dataSet

    sortType = {"ascend": True, "descend": False}

    def sort(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_values(by=0, ascending=PlotAnalyze.sortType[direction], inplace=True)
        return newdata

    def sortIndex(self, data, arg):

        newdata = pd.DataFrame(data)
        direction = arg[0]
        newdata.sort_index(ascending=PlotAnalyze.sortType[direction], inplace=True)
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

        if isinstance(data, pd.DataFrame):

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
        temp = PlotAnalyze.dataFunc[arg[0]](self, temp, argList)

        return temp

    def evaluateProcess(self, data, arg):
        temp = data
        argList = arg[1].split("~")
        temp = PlotAnalyze.processFunc[arg[0]](temp, argList)

        return temp

    def extractData(self, dataSet, subset, args):

        pdArg = pd.Series(args)
        f = self.parseArgs(pdArg)

        # slicedData = self.data[int(dataSet)]

        slicedData = self.data[self.getDFIndexFromName(dataSet)]

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


def main(argv):

    directory = "./"
    viewSetDir = "./views"
    input = "./input/"

    output = 0

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["dir=","view="])
    except getopt.GetoptError:
        print("plotanalyze.py -i <input> -o <output> -v <viewdir>")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print("test.py -i <inputfile>")
            sys.exit()
        elif opt in ("-i", "--input"):
            input = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-v", "--view"):
            viewSetDir = arg



    print("INFO     Plot Analyze v" + VERSION)

    plotanalyze = PlotAnalyze(directory)

    plotanalyze.deploy_data(input)

    plotanalyze.loadViewSets(viewSetDir)

    plotanalyze.parseRawViewData()
    plotanalyze.parseView()
    plotanalyze.setView(0)
    plotanalyze.displayAllViews()


if __name__ == "__main__":
    main(sys.argv[1:])


