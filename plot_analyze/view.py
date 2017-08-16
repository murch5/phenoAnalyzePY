
import plot_manager.plot_manager as pltmanager
import io_util.xml_parse as xml_parser
import factory_manager as fm

import logging
logger = logging.getLogger(__name__)

class View(fm.FactoryObject):

    def initialize(self):

        #self.title = ""
        self.view_style_XML = None
        self.viewset_style_XML = None
        self.figure = None
        self.plot_engine = "matplotlib"

    def show(self):
        self.plot_manager.call_all("draw")
        self.plot_manager.call_all("annotate")

    def save(self):
        figure_list = self.plot_manager.get_all("figure")

        for i, fig in enumerate(figure_list):
            fig.savefig("./output/" + self.get("title") + "_" + '{:d}'.format(i) + ".png", bbox_inches="tight", pad_inches=0, transparent=True)
        pass

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

    def save_views(self):
        self.call_all("save")


