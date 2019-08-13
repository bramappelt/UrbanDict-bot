import re


def urbandict_response(number, action, word, data):
    ''' select data value from urban dictionary response data '''

    reply = False
    data = data['list']

    # check if the word searched for is defined in the dictionary
    if data:
        # select definition number, defaults to zero if invalid
        if number and number != '0':
            number = abs(int(number.lstrip('0')) - 1)
            if number >= len(data):
                number = 0
            data = data[number]
        else:
            number = 0
            data = data[number]

        # check if action field exists
        try:
            message = data[action]
        except KeyError:
            fmt_str = '({}) Invalid action argument: {}'
            message = fmt_str.format(number, action)
            return reply, message

        # check if action field is empty
        if message:
            reply = True
            message = '({}) {}'.format(number, message)
            return reply, message
        else:
            fmt_str = '({}) empty {} field, try an other action.'
            message = fmt_str.format(number, action)
            return reply, message
    else:
        fmt_str = '({}) {} does not exist in the dictionary'
        message = fmt_str.format(number, word)
        return reply, message


class CommentParser:
    ''' Parse text and produce reply text '''

    query_pattern = r'''\$\$:([0-9]*):([a-z_]+)\s(["'])(.+?)\3'''

    def __init__(self, text, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.text = text
        self.matches = None
        self.compiled_pattern = re.compile(self.query_pattern)

    def is_query(self):
        ''' check if query has correct format '''
        matches = re.match(self.compiled_pattern, self.text)
        self.matches = matches
        if matches:
            return True
        else:
            return False

    def reply_text(self):
        ''' produce reply text from query '''
        number, action, _, word = self.matches.groups()
        word = word.strip(' ')
        url = self.api_connection.base_url + word

        # get response from api
        api_response = self.api_connection.request('get', url)
        self.api_response = api_response
        response_json = api_response.json()

        # apply query arguments to obtain data from the response json
        reply, text = urbandict_response(number, action, word, response_json)
        return reply, text


if __name__ == '__main__':
    import time

    import apilogin

    name = 'urbandictapi'
    user_agent = 'Urbandict reader by me'
    base_url = 'http://api.urbandictionary.com/v0/define?term='
    urbandictapi = apilogin.WebApi(name, user_agent, base_url=base_url)

    # do some test queries
    q_test = []
    with open('..\\data\\test_queries.txt', 'r') as fr:
        for l in fr.readlines():
            q_test.append(l.split('#')[0])

    for q in q_test:
        cp = CommentParser(q, api_connection=urbandictapi)

        if cp.is_query():
            reply, text = cp.reply_text()
            print(reply, text, q)
        else:
            print('NO QUERY', q)

        # decrease the request frequency
        time.sleep(1)
