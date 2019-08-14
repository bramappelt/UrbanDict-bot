''' module that provides helper tools for the UrbanDict_Bot '''


import logging
import logging.config
import os.path


# logger setup
confpath = os.path.abspath('..\\data\\botlog.conf')
logging.config.fileConfig(confpath, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def get_creds(filename):
    ''' parses credentials file to a dict '''
    with open(filename, 'r') as fr:
        data = {}
        for line in fr.readlines():
            key, value = [l.strip('\n') for l in line.split('=')]
            data[key] = value
    return data
