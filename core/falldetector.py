import logging
from collections import OrderedDict

LOG = logging.getLogger(__name__)


class FallDetector:
    def __init__(self):
        self.old_persons = OrderedDict()
    
    def update(self, persons, framecount, fps):
        self.falls = OrderedDict()
        
        for ID, (x, y, x_, y_, w_, h_) in persons.items():
            if framecount == 0:
                self.old_persons[ID] = (x, y, False)
                
            else:
                if ID in self.old_persons:
                    (old_x, old_y, fall) = self.old_persons[ID]
                    
                    if w_ >= h_:
                        if y - old_y >= h_:
                            LOG.info("FALL DETECTED")
                            self.falls[ID] = (x_, y_, w_, h_)
                            self.old_persons[ID] = (x, y, True)
                        
                        elif fall:
                            self.falls[ID] = (x_, y_, w_, h_)
                    
                    elif framecount % round(fps) == 0:
                        self.old_persons[ID] = (x, y, False)
                        
                    else:
                        self.old_persons[ID] = (old_x, old_y, False)
                
                else:
                    self.old_persons[ID] = (x, y, False)
                    
        return self.falls
                
                