import os
import cv2
import sys
import time
import logging
from threading import Thread
from queue import Queue
from .. import transforms, visualizer

import PIL
import torch

LOG = logging.getLogger(__name__)

class DetectionLoader:
    def __init__(self, streams, animation, processor, model):
        self.streams = streams
        self.animation = animation
        self.processor = processor
        self.model = model
        self.detectors = []
    
    def loadDetectors(self):    
        for stream in self.streams.getStreams():
            ref_detectors = Detector(stream, self.animation, self.processor, self.model)
            self.detectors.append(ref_detectors)
    
    def getFrames(self):
        frames = []
        for detector in self.detectors:
            frame = detector.getFrame()
            
            if frame is None:
                frames.append(None)
            else:
                frames.append(frame) 
        
        return frames

class Detector:
    def __init__(self, stream, animation, processor, model):
        self.animation = animation
        self.processor = processor
        self.model = model
        self.stream = stream
        self.ID, self.scale = self.stream.getConfig()
        self.outframes = Queue(maxsize=0)
        
        self.infer()
        
    def infer(self):
        self.t = Thread(target=self.update, args=())
        self.t.daemon = True
        self.t.start()
        
    def update(self):
        for frame_i, (ax, ax_second) in enumerate(self.animation.iter()):
            image = self.stream.getFrame()
            
            if image is None:
                LOG.info('no more images captured')
                break

            if self.scale != 1.0:
                image = cv2.resize(image, None, fx=float(self.scale), fy=float(self.scale))
                LOG.debug('resized image size: %s', image.shape)
            
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            if ax is None:
                ax, ax_second = self.animation.frame_init(image)
            visualizer.BaseVisualizer.image(image)
            visualizer.BaseVisualizer.common_ax = ax_second

            start = time.time()
            image_pil = PIL.Image.fromarray(image)
            processed_image, _, __ = transforms.EVAL_TRANSFORM(image_pil, [], None)
            LOG.debug('preprocessing time %.3fs', time.time() - start)

            preds = self.processor.batch(self.model, torch.unsqueeze(processed_image, 0), device=torch.device('cuda'))[0]
            
            self.outframes.put((frame_i, ax, image, preds))
            
    def getFrame(self):
        if self.outframes.empty():
            return None
        else:
            return self.outframes.get()