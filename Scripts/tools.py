''' module that provides helper tools for the UrbanDict_Bot '''


def get_creds(filename):
    ''' parses credentials file to a dict '''
    with open(filename, 'r') as fr:
        data = {}
        for line in fr.readlines():
            key, value = [l.strip('\n') for l in line.split('=')]
            data[key] = value
    return data
