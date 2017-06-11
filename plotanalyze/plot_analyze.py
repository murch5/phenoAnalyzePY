
# Logging imports
import logging
import logging.config
import yaml

loggerconfig_stream = open("logger.ini", "r")
log_config = yaml.safe_load(loggerconfig_stream)
logging.config.dictConfig(log_config)

# System imports
import getopt as getopt
import glob as glob
import os as os
import sys as sys


# Add local package directories to path for dev work
sys.path.insert(0,"C:/Users/Ryan/PycharmProjects/datatypesPY")
sys.path.insert(1,"C:/Users/Ryan/PycharmProjects/plot_managerPY")
sys.path.insert(2,"C:/Users/Ryan/PycharmProjects/processPY")
sys.path.insert(3,"C:/Users/Ryan/PycharmProjects/factory_managerPY")

import xml.etree.ElementTree as et
import datetime as datetime
import copy as copy

import matplotlib.pyplot as plt
import data_manager.data_manager as dm
import data_manager as data_manager
import plotmanager as plotmanager
import process as process
import data_manager.datatypes as dt
import plotanalyze.view as view
import factory_manager as fm

import io_util.xml_parse as xml_parser
import process

# Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))


# Dictionary containing encoding for data types
data_types = {}
data_types.update(dict.fromkeys(["csv","tsv"],"Table"))
data_types.update(dict.fromkeys(["tif","png"],"Image"))

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

    def load_data(self):

        self.master_data = self.data_factory_manager.add_factory_stack()
        #Determine which data is active by which datasets are referenced in viewset.xml
        active_datasets = self.viewset_xml.findall(".//dataset/name")

        for active in active_datasets:
            self.data_active_list.append(active.text)

        self.data_active_list = set(self.data_active_list)

        logging.debug("--- Active data sets: " + str(self.data_active_list))

        for file in self.data_filelist:
            filename, ext = os.path.splitext(os.path.basename(file))
            if filename in self.data_active_list:
                self.master_data.add(data_types.get(ext[1:]),{"file_name": file, "name":filename, "file_ext":ext[1:]})

        return

    def process(self):

        view_root = self.viewset_xml.getroot()

        for viewset in view_root.iter("viewset"):
            new_viewset = self.view_factory_manager.add_factory_stack()

            for views in viewset.iter("view"):
                new_view = new_viewset.add("View", {"view_XML":views})

                new_view_engine = views.find("plot_engine")

                new_plot_manager = self.plot_factory_manager.add_factory_stack()
                new_plot_manager.set("engine",new_view_engine)
                new_plot_manager.setup_figure()

                plot_list = views.find(".//plot")

                for subplot in plot_list.iter("subplot"):

                    new_subplot_type = subplot.find("plottype").text

                    new_data_manager = self.data_factory_manager.add_factory_stack()
                    data_sets = subplot.find("data")
                    data_set_names = data_sets.findall(".//dataset/name")
                    data_name_list = [element.text for element in data_set_names]

                    new_data_manager = self.data_factory_manager.clone_subset(self.master_data,new_data_manager,data_name_list)

                    for i, data in enumerate(data_sets.iter("dataset")):

                        process_stack = data.find("processing")
                        new_process_manager = self.process_factory_manager.add_factory_stack()

                        for process in process_stack:
                            process_step_dict = xml_parser.xml_to_dict(process)
                            for d in process_step_dict.keys():
                                new_process_manager.add(d, process_step_dict.get(d),config=True)

                        new_data_manager.get_obj_list()[i].set_process_manager(new_process_manager)

                    plot_settings = subplot.find("plot_style")

                    plot_settings.update({"figure":new_plot_manager.figure})

                    new_plot_manager.add()

                logging.debug("------ Current view: " + str(views.findtext("title")))

        return



    def process_data(self):
        for viewset in self.viewset:
            for view in viewset.views:
                plot_set = view.get_xml().findall(".//plot")
                for plot in plot_set:
                    subplots_set = plot.findall(".//subplot")
                    for subplot in subplots_set:
                        datasets = subplot.findall(".//data//dataset")

                        new_dm = self.data_factory_manager.add_factory_stack()
                        data_list = []
                        processing_XML = []

                        for data in datasets:
                            data_name = data.findtext("name")
                            processing_XML.append(data.find(".//processing"))
                            data_list.append(data_name)

                        new_dm = self.data_factory_manager.clone_subset(self.master_data,new_dm,data_list)

                        new_dm.evaluate_stack()

                        print(type(new_dm))
                        #TODO Add new function to add new process_manager
                        #TODO Add func to extract list of processing steps contained in xml
                        #TODO Add func to pass new process stack to process_manager passing dict contents


                        for i, data in enumerate(new_dm.get_obj_list()):

                            new_processm = self.process_factory_manager.add_factory_stack()

                            currXML = processing_XML[i]
                            #process_manager = process.ProcessManager()
                            #process_manager.get_available_class_types()

                            for process_step in currXML:
                                process_step_dict = xml_parser.xml_to_dict(process_step)
                                print(process_step_dict)
                                for d in process_step_dict.keys():
                                    new_processm.add_class_object(d,process_step_dict.get(d))
                                    print(process_step)


                            data.set_process_manager(new_processm)

                            data.process_data()



                    view.figure.add_plot(new_dm,subplot.findtext("plottype"),xml_parser.xml_to_dict(subplot))

        return


    def show(self):

        for viewset in self.viewset:
            viewset.show_views()

        plt.show()

        return

    def cleanup(self):
        return

    def __init__(self, directory):
        self.directory = directory  # directory containing the PhenoData to load

        self.data_filelist = None
        self.viewset_filelist = None
        self.viewset_xml = None
        self.data = []
        self.viewset = []
        self.data_active_list = []
        self.data_active = []
        self.data_index_dict = {}

        self.data_factory_manager = fm.FactoryManager(dm.DataManager, data_manager)
        self.process_factory_manager = fm.FactoryManager(process.ProcessManager,process)
        self.view_factory_manager = fm.FactoryManager(view.Viewset,view)
        self.plot_factory_manager = fm.FactoryManager(plotmanager.PlotManager,plotmanager)

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

    logging.info("Loading data...")

    plotanalyze.load_data()

    logging.info("Processing ...")

    plotanalyze.process()

   # logging.info("Processing data...")

    #plotanalyze.process_data()

    logging.info("Show plots...")

    plotanalyze.show()

if __name__ == "__main__":
    main(sys.argv[1:])


