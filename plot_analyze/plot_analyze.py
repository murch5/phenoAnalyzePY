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
import process as process
import view as view
import factory_manager as fm
import io_util.xml_parse as xml_parser

# Set-up logging
loggerconfig_stream = open("logger.ini", "r")
log_config = yaml.safe_load(loggerconfig_stream)
logging.config.dictConfig(log_config)

# Append the plotanalyze path to sys for cmd line
sys.path.append(os.path.dirname(__file__))

data_types = {}
data_types.update(dict.fromkeys(["csv", "tsv"], "Table"))
data_types.update(dict.fromkeys(["tif", "png"], "Image"))

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
                        logging.error("Data file list " + input + " failed to load")

                logging.info("Input file list detected")
                logging.debug("--- File extension: " + str(extension))
                # TODO
            elif extension == ".gz" or extension == ".tgz":
                logging.info("Input gzip tar ball detected")
                logging.debug("--- File extension: " + str(extension))
                # TODO

                return

        elif os.path.exists(input):

            logging.info("Input path detected")
            logging.info("--- Compiling data file list...")

            self.data_filelist = glob.glob(input + "**/*.*", recursive=True)

            logging.debug("--- Data entries in file: " + str(len(self.data_filelist)))

        if self.data_filelist == None:
            logging.error("No input file or directory detected")

        logging.debug("--- File list: " + str(self.data_filelist))

        return

    def load_viewset(self, viewset):

        if os.path.isfile(viewset):
            logging.info("--- View set file detected")

            self.viewset_filelist = viewset
            self.viewset_xml = et.parse(viewset)

            logging.info("--- View set file name(s): " + str(self.viewset_filelist))


        elif os.path.exists(viewset):
            logging.info("--- View set directory detected")
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

        # Determine which data is active by which datasets are referenced in viewset.xml
        active_datasets = self.viewset_xml.findall(".//dataset/name")

        for active in active_datasets:
            self.data_active_list.append(active.text)

        self.data_active_list = set(self.data_active_list)

        logging.debug("--- Active data sets: " + str(self.data_active_list))

        for file in self.data_filelist:
            filename, ext = os.path.splitext(os.path.basename(file))
            if filename in self.data_active_list:
                self.master_data.add(data_types.get(ext[1:]),
                                     {"file_name": file, "name": filename, "file_ext": ext[1:]})

        self.master_data.call_all("load")

        return

    def process(self):

        self._create_viewset()

        return

    def _create_viewset(self):

        view_root = self.viewset_xml.getroot()

        for i, viewset in enumerate(view_root.iter("viewset")):
            new_viewset = self.view_factory_manager.add_factory_stack()
            t = xml_parser.xml_to_dict(viewset)
            r = xml_parser.dict_to_json(t,child_levels=["viewset","view","subplot","data"])
            logging.debug(t)
            logging.debug(r)

            q = xml_parser.rename_child_nodes(r,level_keys=["viewset","view","subplot","data"])
            print(q)
            logging.debug(q)
            z = xml_parser.dict_to_xml(q[0])

            z.write("booya.xml")
            print(et.tostring(z.getroot()))

            with open('data.json ', 'w') as outfile:
                json.dump(q, outfile)

            logging.debug(
                "--- Adding new viewset: " + str(viewset.findtext("title")) + " - " + str(i + 1) + " of " + str(
                    len(view_root.findall("viewset"))))

            self._create_view(viewset,new_viewset)

        pass

    def _create_view(self, viewset, view_manager):

        for j, view in enumerate(viewset.iter("view")):
            view_new = view_manager.add("View", {"view_XML": view})

            logging.debug(
                "------ Adding new view: " + str(view.findtext("title")) + " - " + str(j + 1) + " of " + str(
                    len(viewset.findall("view"))))

            plot_manager_new = self._create_plot(view)

            view_new.set("plot_manager", plot_manager_new)

        pass

    def _create_plot(self, view):

        plot_settings = xml_parser.xml_to_dict(view.find("view_settings"))

        plot_manager_new = self.plot_factory_manager.add_factory_stack(plot_settings.get("view_settings"))
        logging.debug("--------- Adding plot manager")

        plot_manager_new.setup_figure()

        self._create_subplot(view,plot_manager_new)

        plot_manager_new.push_all("grid_spec", plot_manager_new.get("grid_spec"))
        plot_manager_new.push_all("figure", plot_manager_new.get("figure"))
        plot_manager_new.call_all("setup_subplot")
        plot_manager_new.call_all("set_data")


        return plot_manager_new

    def _create_subplot(self,plot,plot_manager):

        for k, subplot in enumerate(plot.iter("subplot")):
            subplot_settings = xml_parser.xml_to_dict(subplot.find("subplot_settings")).get(
                "subplot_settings")

            logging.debug(
                "------------ Adding new subplot: " + str(subplot.findtext("title")) + " - Plot type: " +  str(subplot_settings.get("plot_type")) + " - " + str(
                    k + 1) + " of " + str(
                    len(plot.findall("subplot"))))

            data_manager_new = self._create_data_manager(subplot.find("data"))

            plot_settings = xml_parser.xml_to_dict(subplot.find("plot_style")).get("plot_style")

            subplot_settings.update(plot_settings)

            data_manager_new.call_all("process_data")
            subplot_new = plot_manager.add(subplot_settings.get("plot_type"), subplot_settings)
            subplot_new.set("data_manager", data_manager_new)

        pass

    def _create_data_manager(self, data_sets):

        data_manager_new = self.data_factory_manager.add_factory_stack()

        data_set_names = data_sets.findall(".//dataset/name")
        data_name_list = [element.text for element in data_set_names]

        data_manager_new = self.data_factory_manager.clone_subset(self.master_data, data_manager_new,
                                                                  data_name_list)
        for i, data in enumerate(data_sets.iter("dataset")):

            process_stack = data.find("processing")
            process_manager_new = self.process_factory_manager.add_factory_stack()

            for process in process_stack:
                process_step_dict = xml_parser.xml_to_dict(process)
                for d in process_step_dict.keys():
                    process_manager_new.add(d, process_step_dict.get(d))

            data_manager_new.get_obj_list()[i].set_process_manager(process_manager_new)

        return data_manager_new

    def show(self):

        self.view_factory_manager.call_all("show_views")

        plt.show()

        return

    def cleanup(self):
        return

    def __init__(self, directory):
        self.directory = directory  # directory containing the PhenoData to load

        self.data_filelist = None
        self.viewset_filelist = None
        self.viewset_xml = None

        self.data_active_list = []

        self.data_factory_manager = fm.FactoryManager(dm.DataManager, data_manager)
        self.process_factory_manager = fm.FactoryManager(process.ProcessManager, process)
        self.view_factory_manager = fm.FactoryManager(view.Viewset, view)
        self.plot_factory_manager = fm.FactoryManager(plot_manager.PlotManager, plot_manager)

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

    logging.info("Plot Analyze v" + version.__version__)
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

    logging.info("Show plots...")

    plotanalyze.show()

if __name__ == "__main__":
    main(sys.argv[1:])
