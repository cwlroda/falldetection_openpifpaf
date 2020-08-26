import os
import logging
import matplotlib.pyplot as plt
from datetime import datetime
from .. import config

LOG = logging.getLogger(__name__)


class ImgWriter:
    def __init__(self):
        settings = config.ConfigParser().getConfig()
        
        self.ID = None
        self.output_dict = settings['FileOutput'][0]
        self.output_dir = os.path.abspath(__file__+"/../../")+"/output/img/"
        self.fileconv = self.output_dict["FileName"]
        self.filename = None
        
    def write(self, ID, fallcount):
        self.filename = self.getFileName(ID, fallcount)
        plt.savefig(self.filename)
        LOG.info("Frame written: {}".format(self.filename))
        
    def getFileName(self, ID, fallcount):
        str_filename = "".join(self.fileconv)
        str_datetime = datetime.today().strftime('%Y%m%d_%H%M%S')
        str_filename = str_filename.replace("{yyyymmdd}_{HHMMSS}", str_datetime)
        str_filename = str_filename.replace("{streamID}", str(ID))
        str_filename = str_filename.replace("{algoName}", "openpifpaf")
        str_filename = str_filename.replace("{fallcount}", str(fallcount))
        str_filename = os.path.join(self.output_dir, str_filename)
        
        return str_filename
    
    