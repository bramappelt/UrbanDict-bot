# Reddit Bot that provides urban dictionary definitions

# Table of contents

1. [Introduction](#intro)
2. [Setup & Usages](#par1)
    1. [Bot Setup](#subpar1)
    2. [Bot Usage](#subpar2)
    3. [Queries](#subpar3)
3. [Examples](#par2)

## Introduction <a name="intro"></a>

The goal of this project was to build a reddit bot without making use of the PRAW module. In `main.py` a single subreddit is monitored for specific comments. The bot will reply to these comments if they match a certain query. You can create your own `main.py` script to fulfil your needs, e.g. monitoring multiple subreddits.

![](https://github.com/bramappelt/UrbanDict-bot/blob/master/img/yeet.PNG)

## Usages <a name="par1"></a>

First, the bot needs a setup. For every user of the bot a reddit account is needed. Make sure that your account is more than 3 months old and has some positive post and comment karma. This will prevent you from having a 9 minutes, instead of 2 seconds, interval post rate.

- Assuming you have a reddit account, login and visit https://old.reddit.com/prefs/apps/. Here, you can create an app that provides you your app id and key. Choose type `script` and at least add values to the `name` and `redirect uri` fields. Thereafter, click `create app`. See the image below.

![](https://github.com/bramappelt/UrbanDict-bot/blob/master/img/script_app.PNG)

- Create a file called `reddit_creds.txt` and populate it as follows:\s\s
username=\<yourredditusername\>\s\s
password=\<yourredditpassword\>\s\s
app_id=\<yourappidd\>\s\s
app_key=\<yourappkey\>\s\s

### Bot Setup <a name='subpar1'></a>

- Clone this repository `git clone https://github.com/bramappelt/UrbanDict-bot.git`
- _Optional_ : Install requests if not installed yet `pip install -r requirements.txt`
- Change to the cloned directory `cd UrbanDict-bot`
- Create a new directory called 'private' `mkdir private`
- Store the file 'reddit_creds.txt' in the private directory

We are now ready to use the bot!

### Bot Usage <a name='subpar2'></a>

The bot can be run from the command line.

- This will run the bot with default arguments `python main.py` and is equivalent to `python main.py -s UrbanDict_Bot -l 5 -o new`
- _It is okay to use the default subreddit for your testing, however you can always create your own!_

Extra info on the available arguments:
![](https://github.com/bramappelt/UrbanDict-bot/blob/master/img/cmd_args.PNG)

- Log files are created in `UrbanDict-bot/data/`

### Queries <a name="subpar3"></a>
The bot will only reply to comments that match a certain query. This query should have the following format:

                        $$:<number>:<action> '<word>'

- **\<number>**: A positive integer that reflects the definition rank (when omitted the top definition is selected)
- **\<action>**: definition, permalink, thumbs_up,                            sound_urls, author, word, defid,                             current_vote, written_on, example, thumbs_down
- **\<word>**: The word you want the urban dictionary information from (do not forget the quotes!)

## Examples <a name="par2"></a>

The data is obtained from https://www.urbandictionary.com/

Some example queries are:
-   \$$::written_on 'cromulent'
-   \$$:1:thumbs_down '307'
-   \$$:2:thumbs_up 'broship'
-   \$$:3:sound_urls 'cromulent'
-   \$$:4:current_vote 'yeet'
-   \$$::example 'yeet'

![](https://github.com/bramappelt/UrbanDict-bot/blob/master/img/cromulent_example.PNG)
