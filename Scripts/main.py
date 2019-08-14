import time
import logging
import logging.config
import os.path

import tools
import apilogin
import listinghandler
from bot import UrbanDictBot


# logger setup
confpath = os.path.abspath('..\\data\\botlog.conf')
logging.config.fileConfig(confpath, disable_existing_loggers=False)
logger = logging.getLogger(__name__)


useragent = 'Replybot by UrbanDict-bot (v1.0)'

# urbandict connection
dict_name = 'urbandictapi'
base_url = 'http://api.urbandictionary.com/v0/define?term='
urbandictapi = apilogin.WebApi(dict_name, useragent, base_url=base_url)

logger.info('Connection with {} is established'.format(urbandictapi))

# redditapi oauth
name = 'Reddit'
token_url = 'https://www.reddit.com/api/v1/access_token'
call_url = 'https://oauth.reddit.com/api/v1/me'
logins = tools.get_creds('..\\private\\reddit_creds.txt')
token_data = {'grant_type': 'password',
              'password': logins['password'],
              'username': logins['username']}

# connection object
redditapi = apilogin.TokenWebApi(name,
                                 useragent,
                                 token_url,
                                 token_data,
                                 **logins)

logger.info('Login succesful, access token obtained for {}'.format(redditapi))

# bot object
udbot = UrbanDictBot(api_connection=redditapi,
                     dict_connection=urbandictapi,
                     database='..\\data\\botreplies.db')

logger.info('{} created succesfully'.format(udbot))

# bot logic
try:
    logger.info("Program's mainloop entered")
    n_iter = 0
    while True:
        logger.debug('Iteration: {}'.format(n_iter))
        time.sleep(5)

        # select articles of given subreddit
        all_articles = udbot.get_articles(subreddit='UrbanDict_Bot',
                                          order='new', limit=5)

        # get the comment trees associated with the selected articles
        for article in listinghandler.ChildScanner(all_articles):
            ctree = udbot.get_comments(article)

            # loop over the individual comments
            for c in listinghandler.CommentScanner(ctree):
                # apply replier function(reply/remove/private_message)
                udbot.replier(c)
        n_iter += 1

except KeyboardInterrupt:
    logger.info("Program killed by KeyboardInterrupt")

except Exception as e:
    logger.critical(e)

finally:
    udbot.dbconnection.close()
    logger.info('Program is terminated, dbconnection succesfully closed')
