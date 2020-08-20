import sys
import os
import io
import time
import re
import cv2
import logging
import numpy as np
from threading import Thread
from queue import Queue, LifoQueue

LOG = logging.getLogger(__name__)

class MultiStreamLoader:
    def __init__(self, RTSP_list):
        self.RTSP_list = RTSP_list
        self.streams = []
        
    def generateStreams(self):
        for RTSPdict in self.RTSP_list:
            ref_RTSPHandler = None
            str_RTSPURL = None
            ID = None
            scale = None
            
            if "RTSPURL" in RTSPdict:
                str_RTSPURL = RTSPdict["RTSPURL"]
            if "ID" in RTSPdict:
                ID = RTSPdict["ID"]
            if "Scale" in RTSPdict:
                scale = RTSPdict["Scale"]
            LOG.info("Loading stream: " + str_RTSPURL)
            
            ref_RTSPHandler = RTSPHandler(RTSPdict, str_RTSPURL, ID, scale)
            
            self.streams.append(ref_RTSPHandler)
            LOG.info("Loaded " + str_RTSPURL)
        
        return self.streams
    
    def getStreams(self):
        return self.streams


class RTSPHandler:
    def __init__(self, dict, RTSPURL=None, ID=None, scale=1.0):
        self.RTSPdict = dict
        self.RTSPURL = RTSPURL
        self.ID = ID
        self.scale = scale
        self.Q = Queue(maxsize=0)
        self.frame = None
        self.droppedFrames = 0
        
        self.online = True
        self.makeConnection()
    
    def makeConnection(self):
        try:
            self.stream = cv2.VideoCapture(self.RTSPURL, cv2.CAP_FFMPEG)
            
            if self.stream.isOpened():
                LOG.info("Loaded stream: " + self.RTSPURL)
                self.t = Thread(target=self.update, args=())
                self.t.daemon = True
                self.t.start()
                LOG.info("RTSP thread started")
                
        except:
            LOG.error("Cannot open stream: " + self.RTSPURL, exc_info=True)
    
    def reconnect(self):
        self.stream.release()
        self.frame = None
        self.droppedFrames = 0
        self.stream = cv2.VideoCapture(self.RTSPURL, cv2.CAP_FFMPEG)
        
        if self.stream.isOpened():
            LOG.info("Reconnected to stream: " + self.RTSPURL)
            self.online = True
            return True
        else:
            LOG.error("Cannot reconnect to stream: " + self.RTSPURL)
            time.sleep(10)
            return False
        
    def update(self):
        while True:
            if self.stream.isOpened():
                (self.grabbed, self.frame) = self.stream.read()

                if self.grabbed:
                    self.droppedFrames = 0
                    self.Q.put(self.frame)
                else:
                    self.droppedFrames += 1
                    
                    if self.droppedFrames > 60:
                        self.online = False
                        LOG.info("Reconnecting to stream: " + self.RTSPURL)
            
            while not self.stream.isOpened() or not self.online:
                self.online = self.reconnect()
    
    def getConfig(self):
        return (self.ID, self.scale)
    
    def getFrame(self):
        return self.Q.get()
    
    