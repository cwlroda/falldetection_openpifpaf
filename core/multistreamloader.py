import sys
import os
import io
import time
import re
import cv2
import logging
import numpy as np
import threading
from threading import Thread
from multiprocessing import Queue

LOG = logging.getLogger(__name__)

class MultiStreamLoader:
    def __init__(self, RTSP_list):
        self.RTSP_list = RTSP_list
        self.streams = []
        
    def generateStreams(self):
        for RTSPdict in self.RTSP_list:
            str_RTSPURL = None
            ID = None
            scale = None
            
            if "RTSPURL" in RTSPdict:
                str_RTSPURL = RTSPdict["RTSPURL"]
            if "ID" in RTSPdict:
                ID = RTSPdict["ID"]
            if "Scale" in RTSPdict:
                scale = RTSPdict["Scale"]
            
            LOG.info("Initialising stream: " + str_RTSPURL)    
            self.streams.append((str_RTSPURL, ID, scale))
    
        return self.streams

