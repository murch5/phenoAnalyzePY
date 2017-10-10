import data_manager as dm
import os as os
import xml.etree.ElementTree as et

import logging as logging
logger = logging.getLogger(__name__)

class DataCollection():
    def __init__(self):
        self.data_handler = dm.DataManager(dm)
        self.data_XML = None
        self.data_file_list = None

        pass

    def load_data(self, xml, file_list):

        self.base_XML = xml
        self.data_file_list = file_list

        active_datasets = self.base_XML.iterfind(".//dataset")

        self.data_XML = et.ElementTree(et.Element("Data"))
        data_XML_root = self.data_XML.getroot()

        for active in active_datasets:
            data_XML_root.append(active)

        ## Call function to decorate master xml with file path, type, and uid -- for subsequent loading

        self.data_XML = self.add_path_to_xml(self.data_XML, self.data_file_list)

        self.data_XML.write("data_master.xml")

        self.data_handler.populate_from_xml(self.data_XML.iterfind(".//dataset"), nested_type="./type")


        logger.debug("Lazy loading data structures from XML...")
        self.data_handler.call_all("load")

        logger.debug("Build processing stack...")
        self.data_handler.call_all("build_process_stack")

        logger.debug("Build processing stack...")
        self.data_handler.call_all("process_data")

        pass

    def get_data_dict(self):

        data_dict = {}

        name_datasets = self.data_handler.get_all("name")
        data_datasets = self.data_handler.get_all("data")

        data_dict = dict(zip(name_datasets, data_datasets))

        return data_dict

    def add_path_to_xml(self, xml, file_list):

        file_list_dict = {}

        for file in file_list:
            filename, ext = os.path.splitext(os.path.basename(file))
            file_list_dict.update({filename: [ext, file]})


        for dataset in xml.iterfind("dataset"):
            dataset_name = dataset.findtext("name")
            file_path = et.Element("path")
            file_path.text = file_list_dict.get(dataset_name)[1]
            file_ext = et.Element("ext")
            file_ext.text = file_list_dict.get(dataset_name)[0][1:]
            dataset.insert(0, file_path)
            dataset.insert(0, file_ext)

        return xml
