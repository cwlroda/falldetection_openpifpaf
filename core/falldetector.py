import logging
from collections import OrderedDict

LOG = logging.getLogger(__name__)


class FallDetector:
    def __init__(self):
        self.old_persons = OrderedDict()
    
    def update(self, persons, framecount, fps):
        self.falls = OrderedDict()
        
        for ID, (x, y, x_, y_, w_, h_, l_ank, r_ank) in persons.items():
            if framecount == 0:
                self.old_persons[ID] = (x, y, h_, False)
                
            else:
                if ID in self.old_persons:
                    (old_x, old_y, old_h, fall) = self.old_persons[ID]
                    
                    if w_ >= h_:
                        if (l_ank != 0 or r_ank != 0) and y-old_y >= old_h/2:
                            LOG.info("FALL DETECTED")
                            self.falls[ID] = (x_, y_, w_, h_)
                            self.old_persons[ID] = (x, y, old_h, True)
                        
                        elif fall:
                            self.falls[ID] = (x_, y_, w_, h_)
                    
                    elif framecount % round(fps) == 0:
                        self.old_persons[ID] = (x, y, h_, False)
                        
                    else:
                        self.old_persons[ID] = (old_x, old_y, old_h, False)
                
                else:
                    self.old_persons[ID] = (x, y, h_, False)
                    
        return self.falls
                
                