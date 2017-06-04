#Import plot manager
import plotmanager.plot_manager as pltmanager
import matplotlib.pyplot as plt
import io_util.xml_parse as xml_parser

import logging
logger = logging.getLogger(__name__)

class View():

    def __init__(self):
        self.title = ""
        self.view_XML = None
        self.view_style_XML = None
        self.viewset_style_XML = None
        self.figure = None
        self.plot_engine = "matplotlib"

        return

    def set_xml(self,xml):
        self.view_XML = xml
        self.view_style_XML = self.view_XML.find(".//view_style")

    def set_title(self,title):
        self.title = title

    def get_xml(self):
        return self.view_XML

    def set_viewset_style_XML(self, xml):
        self.viewset_style_XML = xml

    def init_plot(self):
        self.plot_engine = self.view_XML.find(".//plot_engine").text
        plot_title = self.view_XML.find(".//title").text
        logger.debug("Initializing plot manager")
        self.figure = pltmanager.plot_manager(plot_title,self.viewset_style_XML,xml_parser.xml_to_dict(self.view_XML))

    def show(self):
        self.figure.draw_plots()

class Viewset():

    def __init__(self):
        self.title = None
        self.viewset_XML = None
        self.viewset_style_XML = None
        self.views = []

    def set_title(self,name):
        self.title = name

    def set_xml(self,xml):
        self.viewset_XML = xml
        self.viewset_style_XML = self.viewset_XML.find(".//viewset_style")

    def show_views(self):
        for view in self.views:
            view.show()
