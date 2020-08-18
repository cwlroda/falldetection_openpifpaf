import cv2
import logging
from threading import Thread
from queue import Queue

logger = logging.getLogger(__name__)

class RTSPHandler:
    def __init__(self, RTSPURL):
        self.frame = None
        self.RTSPURL = RTSPURL
        self.Q = Queue(maxsize=0)
        
    def start(self):
        try:
            self.stream = cv2.VideoCapture(self.RTSPURL, cv2.CAP_FFMPEG)
            
            if self.stream.isOpened():
                logger.info("Loaded stream: " + self.RTSPURL)
                self.t = Thread(target=self.update, args=())
                self.t.daemon = True
                self.t.start()
                logger.info("RTSP thread started")
                
        except:
            logger.error("Cannot open stream: " + self.RTSPURL, exc_info=True)
        
    def update(self):
        while self.stream.isOpened():
            (self.grabbed, self.frame) = self.stream.read()
            self.Q.put(self.frame)
    
    def getFrame(self):
        if not self.Q.empty():
            return self.Q.get()
        
        else:
            return None
    
    