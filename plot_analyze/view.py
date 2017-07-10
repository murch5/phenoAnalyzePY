
import plot_manager.plot_manager as pltmanager
import io_util.xml_parse as xml_parser
import factory_manager as fm

import logging
logger = logging.getLogger(__name__)

class View(fm.FactoryObject):

    def initialize(self):

        self.title = ""
        self.view_style_XML = None
        self.viewset_style_XML = None
        self.figure = None
        self.plot_engine = "matplotlib"

    def show(self):
        self.plot_manager.call_all("draw")

    def do(self, data):
        self.show()
        pass

class Viewset(fm.FactoryStack):

    def initialize(self):
        self.title = None
        self.viewset_XML = None
        self.viewset_style_XML = None
        self.views = []

    def show_views(self):
        self.call_all("show")


