''' module that provides helper tools for the UrbanDict_Bot '''


import logging
import logging.config
import os.path
import sqlite3
import pickle


# logger setup
confpath = os.path.abspath('../data/botlog.conf')
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


def responses_from_table(file, table, column='*'):
    ''' fetches and unpickles response objects from sql table '''
    if not os.path.isfile(file):
        return None

    sql_stmt = 'SELECT {} FROM {}'.format(column, table)
    conn = sqlite3.connect(file)
    with conn:
        response = conn.execute(sql_stmt).fetchall()

    results = []
    for ir, row in enumerate(response):
        for ic, col in enumerate(row):
            if isinstance(col, bytes):
                results.append(pickle.loads(response[ir][ic]))

    return results


if __name__ == '__main__':
    replies_table = responses_from_table('../data/botreplies.db', 'replies')
    for reply in replies_table:
        errors = reply.json()['json']['errors']
        body = reply.json()['json']['data']['things'][0]['data']['body']
        print(errors, body)
