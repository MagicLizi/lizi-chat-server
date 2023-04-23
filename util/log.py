import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
fh = logging.FileHandler(filename='./server.log')
formatter = logging.Formatter(
    "%(levelname)s:     %(asctime)s - %(message)s - %(module)s - %(funcName)s - line:%(lineno)d"
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
logger.addHandler(ch)
logger.addHandler(fh)

