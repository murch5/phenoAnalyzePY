# Logging imports
import logging
import logging.config
import yaml
import json

# System imports
import getopt as getopt
import glob as glob
import os as os
import sys as sys
import io as io
import traceback as traceback

import xml.etree.ElementTree as et
import matplotlib.pyplot as plt


# Import version number from __init__.py

import __init__ as version

#sys.path.insert(5, "C:/Users/Ryan/PycharmProjects/plot_analyzePY")
sys.path.insert(0, "C:/Users/Ryan/PycharmProjects/datatypesPY")
sys.path.insert(1, "C:/Users/Ryan/PycharmProjects/plot_managerPY")
sys.path.insert(2, "C:/Users/Ryan/PycharmProjects/processPY")
sys.path.insert(3, "C:/Users/Ryan/PycharmProjects/factory_managerPY")
sys.path.insert(4, "C:/Users/Ryan/PycharmProjects/ioPY")


import data_manager.data_manager as dm
import data_manager as data_manager
import plot_manager as plot_manager
import plot_manager.annotation_manager as annotation
import process as process
import view as view
import data as data
import factory_manager as fm
import io_util.xml_parse as xml_parser

# Set-up logging
loggerconfig_stream = open("logger.ini", "r")
log_config = yaml.safe_load(loggerconfig_stream)
logging.config.dictConfig(log_config)

logger = logging.getLogger(__name__)

# Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))

class PlotAnalyze:

    def deploy_data(self, input="./input/"):
        # Deploy data function
        # Get the name of all directories in current working directory
        # Check if input directory already exists

        if os.path.isfile(input):
            extension = os.path.splitext(input)[1]
            if extension == ".txt" or extension == "":
                self.data_filelist = []
                with io.open(os.path.abspath(input),"r") as input_list:
                    try:
                       for data_source in input_list:
                           if os.path.isfile(data_source):
                            self.data_filelist.append(data_source)
                           elif os.path.exists(data_source):
                            new_data_files = glob.glob(data_source + "/*.*")
                            self.data_filelist.extend(new_data_files)
                    except AttributeError:
                        traceback.print_exc()
                        logger.error("Data file list " + input + " failed to load")

                logger.info("Input file list detected")
                logger.debug("--- File extension: " + str(extension))
                # TODO
            elif extension == ".gz" or extension == ".tgz":
                logger.info("Input gzip tar ball detected")
                logger.debug("--- File extension: " + str(extension))
                # TODO

                return

        elif os.path.exists(input):

            logger.info("Input path detected")
            logger.info("--- Compiling data file list...")

            self.data_filelist = glob.glob(input + "**/*.*", recursive=True)

            logger.debug("--- Data entries in file: " + str(len(self.data_filelist)))

        if self.data_filelist == None:
            logger.error("No input file or directory detected")

        logger.debug("--- File list: " + str(self.data_filelist))

        return

    def load_viewset(self, viewset):

        if os.path.isfile(viewset):
            logger.info("--- View set file detected")

            self.viewset_filelist = viewset
            self.viewset_xml = et.parse(viewset)

            logger.info("--- View set file name(s): " + str(self.viewset_filelist))


        elif os.path.exists(viewset):
            logger.info("--- View set directory detected")
            logger.info("--- Compiling view sets...")

            self.viewset_filelist = glob.glob(viewset + "**.xml")

            logger.info("--- View set file name(s): " + str(self.viewset_filelist))

            self.viewset_xml = et.ElementTree(et.Element("root"))
            viewset_root = self.viewset_xml.getroot()
            for viewset_iter in self.viewset_filelist:
                new_viewset = et.parse(viewset_iter)
                for viewsets in new_viewset.iter("ViewSet"):

                    viewset_root.append(viewsets)

            self.viewset_xml.write("combined_xml.xml")

        return

    def load_data(self):

        self.data_collection.load_data(self.viewset_xml, self.data_filelist)

        return

    def process(self):

        view_root = self.viewset_xml.getroot()

        #Design func to prioritize call order to processing steps to ensure no race conditions


        #Extract output data and extract to dict to pass to plot_manager for creation
        # -- create list and convert to dict with dataset name as key

        self.view_collection.build_view_sets(view_root, self.data_collection.get_data_dict())

        return

    def show(self):

        self.view_collection.show_all_views()

        plt.show()

        return

    def cleanup(self):
        return

    def __init__(self, directory):
        self.directory = directory  # directory containing the PhenoData to load

        self.data_filelist = None
        self.viewset_filelist = None
        self.viewset_xml = None

        self.view_collection = view.ViewCollection()
        self.data_collection = data.DataCollection()
        self.data_active_list = []

        return

def main(argv):
    # Default argvs
    directory = "./"
    viewset = "./views/"
    input = "./input/"
    output = "./output/"
    silent = False

    try:
        opts, args = getopt.getopt(argv, "hi:o:", ["dir=", "view="])
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

    logger.info("Plot Analyze v" + version.__version__)
    logger.info("**********************************")

    logger.debug("args: " + str(argv))

    plotanalyze = PlotAnalyze(directory)

    logger.info("Deploying data...")

    plotanalyze.deploy_data(input)

    logger.info("Loading view set(s)...")

    plotanalyze.load_viewset(viewset)

    logger.info("Loading data...")

    plotanalyze.load_data()

    logger.info("Processing ...")

    plotanalyze.process()

    logger.info("Show plots...")

    plotanalyze.show()

if __name__ == "__main__":
    main(sys.argv[1:])
