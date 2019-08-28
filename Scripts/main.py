import time
import logging
import logging.config
import os.path

import tools
import apilogin
import listinghandler
from bot import UrbanDictBot


def registering(useragent, logins):
    # urbandict connection
    dict_name = 'urbandictapi'
    base_url = 'http://api.urbandictionary.com/v0/define?term='
    urbandictapi = apilogin.WebApi(dict_name, useragent, base_url=base_url)

    logger.info('Connection with {} is established'.format(urbandictapi))

    # redditapi oauth
    name = 'Reddit'
    token_url = 'https://www.reddit.com/api/v1/access_token'
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

    logger.info('Access token obtained for {}'.format(redditapi))

    # bot object
    udbot = UrbanDictBot(api_connection=redditapi,
                         dict_connection=urbandictapi,
                         database='../data/botreplies.db')

    logger.info('{} created succesfully'.format(udbot))
    return udbot


def botlogic(mybot, sub, **kwargs):
    # bot logic
    try:
        logger.info("Program's mainloop entered")
        n_iter = 0
        while True:
            logger.info('Iteration: {}'.format(n_iter))
            time.sleep(5)

            # select articles of given subreddit
            all_articles = mybot.get_articles(subreddit=sub, **kwargs)

            # get the comment trees associated with the selected articles
            for article in listinghandler.ChildScanner(all_articles):
                ctree = mybot.get_comments(article)

                # loop over the individual comments
                for c in listinghandler.CommentScanner(ctree):
                    # apply replier function(reply/remove/private_message)
                    mybot.replier(c)
            n_iter += 1

    except KeyboardInterrupt:
        logger.info("Program killed by KeyboardInterrupt")

    except Exception as e:
        logger.critical(e)

    finally:
        mybot.dbconnection.close()
        logger.info('Program is terminated, dbconnection succesfully closed')


def main(useragent, logins, sub, **kwargs):
    bot = registering(useragent, logins)
    botlogic(bot, sub=sub, **kwargs)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--sub', default='UrbanDict_Bot',
                        help='Select subreddit to monitor')
    parser.add_argument('-l', '--limit', default=5,
                        help='Number of post to select')
    parser.add_argument('-o', '--order', default='new',
                        help='post sort order')
    args = parser.parse_args()

    logins = tools.get_creds('../private/reddit_creds.txt')
    useragent = 'Replybot by ' + logins['username'] + '(v1.0)'

    # logger setup
    confpath = os.path.abspath('../data/botlog.conf')
    logging.config.fileConfig(confpath, disable_existing_loggers=False)
    logger = logging.getLogger(__name__)

    logger.info('________________________ NEW RUN ________________________')

    main(useragent, logins, args.sub, limit=args.limit, order=args.order)
