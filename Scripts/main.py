import time

import tools
import apilogin
import listinghandler
from bot import UrbanDictBot

useragent = 'Replybot by UrbanDict-bot (v1.0)'

# urbandict connection
dict_name = 'urbandictapi'
base_url = 'http://api.urbandictionary.com/v0/define?term='
urbandictapi = apilogin.WebApi(dict_name, useragent, base_url=base_url)

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

# bot object
udbot = UrbanDictBot(api_connection=redditapi,
                     dict_connection=urbandictapi,
                     database='..\\data\\botreplies.db',
                     verbose=True)

# bot logic

while True:
    time.sleep(5)
    try:
        all_articles = udbot.get_articles()
        for article in listinghandler.ChildScanner(all_articles):
            ctree = udbot.get_comments(article)
            for c in listinghandler.CommentScanner(ctree):
                udbot.replier(c)

    except Exception as e:
        print(e)

    finally:
        udbot.dbconnection.close()
