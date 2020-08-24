import logging
from collections import OrderedDict

LOG = logging.getLogger(__name__)


class FallDetector:
    def __init__(self):
        self.old_persons = OrderedDict()   
    
    def update(self, persons, framecount):
        self.falls = OrderedDict()
        
        for ID, (x, y, x_, y_, w_, h_) in persons.items():
            if framecount == 0:
                self.old_persons[ID] = (x, y)
                
            elif framecount % 30 == 0:
                if ID in self.old_persons:
                    (old_x, old_y) = self.old_persons[ID]
                    
                    if y - old_y > h_:
                        LOG.info("FALL DETECTED")
                        self.falls[ID] = (x_, y_, w_, h_)
                
                    self.old_persons[ID] = (x, y)
                    
        return self.falls            
                