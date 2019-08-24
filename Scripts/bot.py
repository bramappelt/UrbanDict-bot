''' The Urban Dictionary Bot '''


import logging
import logging.config
import sqlite3
import pickle
import os.path

import parse
import listinghandler


# logger setup
confpath = os.path.abspath('../data/botlog.conf')
logging.config.fileConfig(confpath, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


class UrbanDictBot:
    ''' User code class from which a reply bot can be built '''

    reddit_base_url = 'https://oauth.reddit.com/'

    def __init__(self, api_connection, dict_connection,
                 database, verbose=True):
        self.api_connection = api_connection
        self.dict_connection = dict_connection
        self.databasefile = database
        self.verbose = verbose

        self.dbconnection = sqlite3.connect(database)
        self.initialize_db(database)

    def __repr__(self):
        return self.__class__.__name__

    def initialize_db(self, database):
        ''' connect to database creates one if not exists '''
        replies_table = 'CREATE TABLE IF NOT EXISTS replies (id text, \
                         created_utc text, resp_obj blob, status text)'
        private_table = 'CREATE TABLE IF NOT EXISTS private (id text, \
                         created_utc text, message text, to_redditor text, \
                         sub text, resp_obj blob)'
        self.sql_execution(sql_stmt=[replies_table, private_table])

    def sql_execution(self, sql_stmt, values=()):
        ''' executes a sql statement '''
        if isinstance(sql_stmt, str):
            sql_stmt = [sql_stmt]

        result = []
        with self.dbconnection as conn:
            for stmt in sql_stmt:
                r = conn.execute(stmt, values)
                result.append(r)

        if len(result) == 1:
            return result[0]
        return result

    def get_articles(self, subreddit='UrbanDict_Bot', order='new', **kwargs):
        ''' Provides thread with articles from given query '''
        url = '{}r/{}/{}'.format(self.reddit_base_url, subreddit, order)
        response = self.api_connection.request('get', url, params=kwargs)
        articles = response.json()
        return listinghandler.Thread(articles)

    def get_comments(self, article_thread, **kwargs):
        ''' provides a commenttree '''
        subname = article_thread.subreddit
        article_id = article_thread.id
        fmt_str = '{}r/{}/comments/{}'
        url = fmt_str.format(self.reddit_base_url, subname, article_id)
        response = self.api_connection.request('get', url, params=kwargs)
        comments = response.json()[1]
        return listinghandler.Thread(comments)

    def reply_to_comment(self, reply_id, rtext, created_utc):
        url = '{}api/comment'.format(self.reddit_base_url)
        payload = {'api_type': 'json', 'text': rtext, 'thing_id': reply_id}
        response = self.api_connection.request('post', url, params=payload)
        serialized_response = pickle.dumps(response)
        status = 'replied to'

        # update database with new comment
        sql_insert = 'INSERT INTO replies(id, created_utc, resp_obj, status) \
                      VALUES (?, ?, ?, ?)'
        sql_values = (reply_id, created_utc, serialized_response, status)
        self.sql_execution(sql_insert, sql_values)

    def send_private_message(self, name, created_utc, msg, to, sub):
        url = '{}api/compose'.format(self.reddit_base_url)
        subject = 'Automatic UrbanDict-Bot reply'
        payload = {'api_type': 'json', 'subject': subject,
                   'text': msg, 'to': to, 'from_sr': sub}

        # need more karma for this
        response = self.api_connection.request('post', url, params=payload)
        serialized_response = pickle.dumps(response)

        # save private message in database
        sql_insert = 'INSERT INTO private(id, created_utc, message, to_redditor, \
                      sub, resp_obj) VALUES (?, ?, ?, ?, ?, ?)'
        values = (name, created_utc, msg, to, sub, serialized_response)
        self.sql_execution(sql_insert, values)

    def remove_comment(self, name, author, parent_id):
        if author == self.api_connection.username:
            url = '{}api/del'.format(self.reddit_base_url)
            payload = {'id': name}
            response = self.api_connection.request('post', url, params=payload)
            serialized_response = pickle.dumps(response)

            # update sql row entry for status and response objects
            status = 'deleted'
            sql_update = 'UPDATE replies \
                            SET resp_obj = ?, status = ? WHERE id = ?'
            values = (serialized_response, status, parent_id)
            self.sql_execution(sql_update, values)

    def replier(self, comment, remove_threshold=-5):
        ''' replies to a new comment '''
        # reddit adds backslash before hyphens and underscores
        text = comment.body.replace('\\', '')
        reply_id = comment.name
        c_author = comment.author
        cparser = parse.CommentParser(text,
                                      api_connection=self.dict_connection)
        sql_select = "SELECT id FROM replies WHERE id=?"

        # remove if comment is below total vote threshold
        total_votes = comment.score
        if total_votes <= remove_threshold:
            parent_id = comment.parent_id
            self.remove_comment(reply_id, c_author, parent_id)

            msg = 'Comment {} ({}) removed'.format(reply_id, total_votes)
            logger.debug(msg)

        # skip if comment does not contain query
        elif not cparser.is_query():
            msg = 'No reply, comment {} is no query'.format(reply_id)
            logger.debug(msg)

        # skip if comment is already replied to
        elif self.sql_execution(sql_select, (reply_id, )).fetchall():
            msg = 'Comment already replied to: {}'.format(reply_id)
            logger.debug(msg)

        # reply to comment or send private message if query fails
        else:
            send_reply, rtext = cparser.reply_text()
            create_utc = comment.created_utc
            if send_reply:
                self.reply_to_comment(reply_id, rtext, create_utc)

                msg = 'Replied to {}, {}'.format(c_author, reply_id)
                logger.debug(msg)

            else:
                sql_select = "SELECT id FROM private WHERE id=?"
                if not self.sql_execution(sql_select, (reply_id,)).fetchall():
                    to = c_author
                    sub = comment.subreddit
                    self.send_private_message(reply_id, create_utc,
                                              rtext, to, sub)

                    msg = 'Private message sent to {}'.format(c_author)
                    logger.debug(msg)
                else:
                    msg = 'Private message already sent to {}'.format(c_author)
                    logger.debug(msg)


if __name__ == '__main__':
    import tools
    import apilogin

    useragent = 'Replybot by UrbanDict-bot (v1.0)'

    # urbandict connection
    dict_name = 'urbandictapi'
    base_url = 'http://api.urbandictionary.com/v0/define?term='
    urbandictapi = apilogin.WebApi(dict_name, useragent, base_url=base_url)

    # redditapi oauth
    name = 'Reddit'
    token_url = 'https://www.reddit.com/api/v1/access_token'
    call_url = 'https://oauth.reddit.com/api/v1/me'
    logins = tools.get_creds('../private/reddit_creds.txt')
    token_data = {'grant_type': 'password',
                  'password': logins['password'],
                  'username': logins['username']}
    # connection object
    redditapi = apilogin.TokenWebApi(name,
                                     useragent,
                                     token_url,
                                     token_data,
                                     request_frequency=2.5,
                                     **logins)

    udbot = UrbanDictBot(api_connection=redditapi,
                         dict_connection=urbandictapi,
                         database='../data/botreplies.db')

    # bot logic
    all_articles = udbot.get_articles()
    for article in listinghandler.ChildScanner(all_articles):
        ctree = udbot.get_comments(article)
        for c in listinghandler.CommentScanner(ctree):
            udbot.replier(c)

    udbot.dbconnection.close()
