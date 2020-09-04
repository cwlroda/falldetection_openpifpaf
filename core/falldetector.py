import math
import logging
from collections import OrderedDict
from queue import Queue

LOG = logging.getLogger(__name__)


class FallDetector:
    def __init__(self):
        self.old_persons = OrderedDict()
    
    def update(self, persons, framecount, fps):
        self.falls = OrderedDict()
        
        for ID, (x, y, x_, y_, w_, h_) in persons.items():
            if framecount == 0:
                self.old_persons[ID] = (x, y, w_, h_, False)
                
            else:
                if ID in self.old_persons:
                    (old_x, old_y, old_w, old_h, fall) = self.old_persons[ID]

                    if w_ >= 1.2*h_:
                        if math.sqrt(pow(abs(x-old_x), 2)+pow((y-old_y), 2)) >= 0.7*math.sqrt(pow(old_w, 2)+pow(old_h, 2)):
                            LOG.info("FALL DETECTED")
                            self.falls[ID] = (x_, y_, w_, h_)
                            self.old_persons[ID] = (x, y, old_w, old_h, True)
                        
                        elif fall:
                            self.falls[ID] = (x_, y_, w_, h_)
                    
                    elif framecount % int(fps) == 0:
                        self.old_persons[ID] = (x, y, w_, h_, False)
                        
                    else:
                        self.old_persons[ID] = (old_x, old_y, old_w, old_h, False)
                
                else:
                    self.old_persons[ID] = (x, y, w_, h_, False)
                    
        return self.falls
                
                