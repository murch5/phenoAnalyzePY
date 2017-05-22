
#Imports
import csv
import getopt as getopt
import glob as glob
import os as os
import sys as sys
import pandas as pd
import numpy as np

import xml.etree.ElementTree as et
import datetime as datetime
import copy as copy

#Import plot manager
import plotmanager.plot_manager as pltmanager


#Import plot_analyze packages and modules
from plotanalyze import processingFunc as process, generateFrameSet as gfs
from plotanalyze.datatype.GFFdata import GFF

import datatypes as dt

import plotanalyze.view as view

#Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))

#Constant for version number
VERSION = "0.1.1"

#Dictionary containing encoding for data types
data_types = {}
data_types.update(dict.fromkeys(["csv","tsv"],dt.table.Table))
data_types.update(dict.fromkeys(["tif","png"],dt.image.Image))

#Dictionary containing keys for various log message types
msg_type = {}
msg_type.update(dict.fromkeys(["HEAD","H",0],"HEAD"))
msg_type.update(dict.fromkeys(["INFO","I",1],"INFO"))
msg_type.update(dict.fromkeys(["WARN","W",2],"WARN"))
msg_type.update(dict.fromkeys(["ERRO","E",3],"ERRO"))

def log(msg,indent,type="INFO"):
    ind = ""
    for steps in range(1,indent):
        ind = ind + "\t"
    print(msg_type[type] + "\t" + str(datetime.datetime.now()) + "\t" + ind + msg)

class PlotAnalyze:

    def deploy_data(self, input="./input/"):
        #Deploy data function
        #Get the name of all directories in current working directory
        #Check if input directory already exists

        if os.path.isfile(input):
            extension = os.path.splitext(input)[1]
            if extension == ".txt" or extension == "":
                log("Input file list detected",2,1)
            elif extension == ".gz" or extension == ".tgz":
                log("Input gzip tar ball detected",1,1)
                return
        elif os.path.exists(input):
            log("Input path detected",2,1)
            log("Compiling data file list...",3,1)
            self.data_filelist = glob.glob(input + "**/*.*",recursive=True)


        for file in self.data_filelist:
            filename, ext = os.path.splitext(os.path.basename(file))
            data_temp = data_types[ext[1:]]()
            data_temp.set_filename(file)
            data_temp.set_name(filename)
            self.data.append(data_temp)

        return

    def load_viewset(self, viewset):

        if os.path.isfile(viewset):
                log("View set file detected",2,1)
                self.viewset_filelist = viewset
                self.viewset_xml = et.parse(viewset)

        elif os.path.exists(viewset):
            log("View set directory detected",2,1)
            log("Compiling view sets...",3,1)
            self.viewset_filelist = glob.glob(viewset + "**/*.*")


        return


    def process_viewset(self):

        view_root = self.viewset_xml.getroot()

        for viewset in view_root.iter("viewset"):
            new_viewset = view.Viewset()
            new_viewset.set_title(viewset.findtext("title"))
            new_viewset.set_xml(viewset)

            for views in viewset.iter("view"):
                new_view = view.View()
                new_view.set_title(views.findtext("title"))
                new_view.set_xml(views)
                new_view.set_viewset_style_XML(viewset)
                new_view.init_plot()

                new_viewset.views.append(new_view)

            self.viewset.append(new_viewset)

        return

    def load_data(self):

        #Determine which data is active by which datasets are referenced in viewset.xml
        active_datasets = self.viewset_xml.findall(".//dataset/name")

        for active in active_datasets:
            self.data_active_list.append(active.text)

        self.data_active_list = set(self.data_active_list)

        for data in self.data:
            if data.get_name() in self.data_active_list:
                data.load()
                self.data_active.append(data)

        del self.data[:]

        return

    def process_data(self):

        index_dict = dict(zip(self.data_active_list,range(0,len(self.data_active_list))))

        for viewset in self.viewset:
            for view in viewset.views:
                plot_set = view.get_xml().findall(".//plot")
                for plot in plot_set:
                    subplots_set = plot.findall(".//subplot")
                    for subplot in subplots_set:
                        datasets = subplot.findall(".//data//dataset")
                        for data in datasets:
                            data_name = data.findtext("name")
                            index = index_dict[data_name]
                            new_data = copy.deepcopy(self.data_active[index])
                            new_data.processing(data.find(".//processing"))

                        view.figure.add_plot(new_data,subplot.findtext("plottype"),subplot)

        return

    def show(self):

        for viewset in self.viewset:
            viewset.show_views()

        return

    def cleanup(self):
        return

    def __init__(self, directory):
        self.directory = directory  # directory containing the phenoData to load

        self.data_filelist = None
        self.viewset_filelist = None
        self.viewset_xml = None
        self.data = []
        self.viewset = []
        self.data_active_list = []
        self.data_active = []

        return


def main(argv):

    directory = "./"
    viewset = "./views/venn2.xml"
    input = "./input/"
    output = "./output/"

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
            viewset = arg

    log("Plot Analyze v" + VERSION,0,0)
    log("**********************************", 0, 0)

    plotanalyze = PlotAnalyze(directory)

    log("Deploying data...", 1, 1)
    plotanalyze.deploy_data(input)

    log("Loading view set(s)...", 1, 1)
    plotanalyze.load_viewset(viewset)

    log("Processing view set(s)...", 1, 1)
    plotanalyze.process_viewset()

    log("Loading data...", 1, 1)
    plotanalyze.load_data()

    log("Processing data...", 1, 1)
    plotanalyze.process_data()

    log("Show plots...", 1, 1)
    plotanalyze.show()

if __name__ == "__main__":
    main(sys.argv[1:])


