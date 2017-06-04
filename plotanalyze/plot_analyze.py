
import logging
import logging.config
import yaml

loggerconfig_stream = open("logger.ini", "r")
log_config = yaml.safe_load(loggerconfig_stream)
logging.config.dictConfig(log_config)

import getopt as getopt
import glob as glob
import os as os
import sys as sys
import xml.etree.ElementTree as et
import datetime as datetime
import copy as copy

import matplotlib.pyplot as plt
import data_manager.data_manager as dm
import data_manager.datatypes as dt
import plotanalyze.view as view

import io_util.xml_parse as xml_parser

# Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))

# Constant for version number
VERSION = "0.1.1"

# Dictionary containing encoding for data types
data_types = {}
data_types.update(dict.fromkeys(["csv","tsv"],dt.table.Table))
data_types.update(dict.fromkeys(["tif","png"],dt.image.Image))

class PlotAnalyze:

    def deploy_data(self, input="./input/"):
        # Deploy data function
        # Get the name of all directories in current working directory
        # Check if input directory already exists

        if os.path.isfile(input):
            extension = os.path.splitext(input)[1]
            if extension == ".txt" or extension == "":
                logging.info("Input file list detected")
                logging.debug("--- File extension: " + str(extension))
                # TODO
            elif extension == ".gz" or extension == ".tgz":
                logging.info("Input gzip tar ball detected")
                logging.debug("--- File extension: " + str(extension) )
                # TODO

                return

        elif os.path.exists(input):

            logging.info("Input path detected")
            logging.info("--- Compiling data file list...")

            self.data_filelist = glob.glob(input + "**/*.*",recursive=True)

            logging.debug("--- Data entries in file: " + str(len(self.data_filelist)))

        if self.data_filelist == None:
            logging.error("No input file or directory detected")

        logging.debug("--- File list: " + str(self.data_filelist))
        for file in self.data_filelist:

            filename, ext = os.path.splitext(os.path.basename(file))
            data_temp = data_types[ext[1:]]()
            data_temp.set_filename(file)
            data_temp.set_name(filename)
            self.data.append(data_temp)

        return

    def load_viewset(self, viewset):

        if os.path.isfile(viewset):
                logging.info("View set file detected")

                self.viewset_filelist = viewset
                self.viewset_xml = et.parse(viewset)

                logging.info("--- View set file name(s): " + str(self.viewset_filelist))


        elif os.path.exists(viewset):
            logging.info("View set directory detected")
            logging.info("--- Compiling view sets...")

            self.viewset_filelist = glob.glob(viewset + "**.xml")

            logging.info("--- View set file name(s): " + str(self.viewset_filelist))

            self.viewset_xml = et.ElementTree(et.Element("root"))
            viewset_root = self.viewset_xml.getroot()
            for viewset_iter in self.viewset_filelist:
                new_viewset = et.parse(viewset_iter)
                for viewsets in new_viewset.iter("viewset"):
                    viewset_root.append(viewsets)

            self.viewset_xml.write("combined_xml.xml")

        return

    def process_viewset(self):

        view_root = self.viewset_xml.getroot()

        for viewset in view_root.iter("viewset"):
            new_viewset = view.Viewset()
            new_viewset.set_title(viewset.findtext("title"))
            logging.debug("--- Current view set: " + str(viewset.findtext("title")))
            new_viewset.set_xml(viewset)

            for views in viewset.iter("view"):
                new_view = view.View()
                new_view.set_title(views.findtext("title"))
                logging.debug("------ Current view: " + str(views.findtext("title")))
                new_view.set_xml(views)
                new_view.set_viewset_style_XML(viewset)
                logging.debug("------ Initialize view subplot")
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

        logging.debug("--- Active data sets: " + str(self.data_active_list))

        for data in self.data:
            if data.get_name() in self.data_active_list:
                logging.debug("------ Loading data: " + str(data.get_name()))
                data.load()
                self.data_active.append(data)
                self.data_index_dict.update({data.get_name():(len(self.data_active)-1)})

        del self.data[:]

        return

    def process_data(self):
        for viewset in self.viewset:
            for view in viewset.views:
                plot_set = view.get_xml().findall(".//plot")
                for plot in plot_set:
                    subplots_set = plot.findall(".//subplot")
                    for subplot in subplots_set:
                        datasets = subplot.findall(".//data//dataset")
                        new_data_manager = dm.DataManager()
                        for data in datasets:
                            data_name = data.findtext("name")
                            index = self.data_index_dict[data_name]
                            new_data = copy.deepcopy(self.data_active[index])
                            new_data.processing(data.find(".//processing"))
                            new_data_manager.add_data(new_data)

                        view.figure.add_plot(new_data_manager,subplot.findtext("plottype"),xml_parser.xml_to_dict(subplot))

        return

    def show(self):

        for viewset in self.viewset:
            viewset.show_views()

        plt.show()

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
        self.data_index_dict = {}

        return

def main(argv):

    # Default argvs
    directory = "./"
    viewset = "./views/"
    input = "./input/"
    output = "./output/"
    silent = False

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["dir=","view="])
    except getopt.GetoptError:
        print("plotanalyze.py -i <input> -o <output> -v <viewdir> -s <silent>")
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
        elif opt in ("-s", "--silent"):
            silent = True


    logging.info("Plot Analyze v" + VERSION)
    logging.info("**********************************")

    logging.debug("args: " + str(argv))

    plotanalyze = PlotAnalyze(directory)

    logging.info("Deploying data...")

    plotanalyze.deploy_data(input)

    logging.info("Loading view set(s)...")

    plotanalyze.load_viewset(viewset)

    logging.info("Processing view set(s)...")

    plotanalyze.process_viewset()

    logging.info("Loading data...")

    plotanalyze.load_data()

    logging.info("Processing data...")

    plotanalyze.process_data()

    logging.info("Show plots...")

    plotanalyze.show()

if __name__ == "__main__":
    main(sys.argv[1:])


