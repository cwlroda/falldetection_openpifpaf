import os
import logging
import logging.handlers

class Logger:
    def __init__(self, name):
        self.name = name
        self.log_file = os.path.dirname(__file__)+"/debug.log"
        self.log_file_max_size = 1024 * 1024 * 20 # megabytes
        self.log_backups = 3
        self.log_format = "%(asctime)s [%(levelname)s]: %(filename)s(%(funcName)s:%(lineno)s) >> %(message)s"
        self.log_date_format = "%m/%d/%Y %I:%M:%S %p"
        self.log_filemode = "w" # w: overwrite; a: append
    
    def setup(self, log_level):
        logging.basicConfig(filename=self.log_file,
                            format=self.log_format,
                            filemode=self.log_filemode,
                            level=log_level)
        rotate_file = logging.handlers.RotatingFileHandler(self.log_file,
                                                           maxBytes=self.log_file_max_size,
                                                           backupCount=self.log_backups)
        self.logger = logging.getLogger(self.name)
        self.logger.addHandler(rotate_file)
        
        consoleHandler = logging.StreamHandler()
        logFormatter = logging.Formatter(self.log_format)
        consoleHandler.setFormatter(logFormatter)
        self.logger.addHandler(consoleHandler)
        
        return self.logger