import logging
from logging.handlers import TimedRotatingFileHandler

class Logger:
    def __init__(self, name:str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Create a file handler
        #file_handler = TimedRotatingFileHandler("logs/"+name+".log", when='m', interval=0, backupCount=0)
        file_handler = logging.FileHandler("logs/"+name+".log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(file_handler)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        self.logger.addHandler(console_handler)
