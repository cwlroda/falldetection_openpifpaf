import os
import logging
import xmltodict
from xml.dom import minidom

LOG = logging.getLogger(__name__)

class ConfigParser:
    def __init__(self):
        self.config = {}
        base_path = os.path.dirname(os.path.realpath(__file__))
        xml_file = os.path.join(base_path, "config.xml")
        
        try:
            self.doc = xmltodict.parse(open(xml_file).read())
            LOG.debug("config file loaded")
        except:
            import traceback
            LOG.exception("failed to open config file")
            traceback.print_exc()
        
    def getConfig(self):
        self.extractConfig("config.Source.RTSPAPI")
        self.extractConfig("config.Output.FileOutput")

        return self.config
    
    def getDictValue(self, dict, keyName):
        return dict[keyName]
    
    def extractConfig(self, configItemName):
        configItemList = []
        
        pathItems = configItemName.split(".")
        refDict = self.doc
        
        for path in pathItems:
            refDict = self.getDictValue(refDict, path)
        
        if isinstance(refDict, list):
            configItemList = refDict
        else:
            configItemList.append(refDict)
            
        self.config[pathItems[-1]] = configItemList