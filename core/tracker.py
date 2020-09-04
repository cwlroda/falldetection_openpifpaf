from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np
import logging

LOG = logging.getLogger(__name__)


class CentroidTracker():
    def __init__(self):
        self.ID = 0
        self.objects = OrderedDict()
        self.disappeared = OrderedDict()
        
    def register(self, centroid):
        self.objects[self.ID] = centroid
        self.disappeared[self.ID] = 0
        self.ID += 1
        
    def deregister(self, ID):
        del self.objects[ID]
        del self.disappeared[ID]
        
    def update(self, inputCentroids, frame_threshold):
        if len(inputCentroids) == 0:
            for ID in list(self.disappeared.keys()):
                self.disappeared[ID] += 1
                
                if self.disappeared[ID] > 2*frame_threshold:
                    self.deregister(ID)
            
            return self.objects
        
        if len(self.objects) == 0:
            for centroid in inputCentroids:
                self.register(centroid)
                
        else:
            IDs = list(self.objects.keys())
            centroids = list(self.objects.values())
            
            D = dist.cdist(np.array(centroids), inputCentroids)
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            usedRows = set()
            usedCols = set()
            
            for(row, col) in zip(rows, cols):
                if row in usedRows or col in usedCols:
                    continue
                
                ID = IDs[row]
                self.objects[ID] = inputCentroids[col]
                self.disappeared[ID] = 0
                
                usedRows.add(row)
                usedCols.add(col)
                
            unusedRows = set(range(0, D.shape[0])).difference(usedRows)
            unusedCols = set(range(0, D.shape[1])).difference(usedCols)
            
            if D.shape[0] >= D.shape[1]:
                for row in unusedRows:
                    ID = IDs[row]
                    self.disappeared[ID] += 1
                    
                    if self.disappeared[ID] > 2*frame_threshold:
                        self.deregister(ID)
                        
            else:
                for col in unusedCols:
                    self.register(inputCentroids[col])
        
        return self.objects