# python3

import json
import logging

from time import sleep

import cssutils
import requests

import config
from linebot import send_stickers
cssutils.log.setLevel(logging.CRITICAL)

# This will mark the last update we've checked
with open('updatefile', 'r') as f:
    last_update = int(f.readline().strip())
# Here, insert the token BotFather gave you for your bot.
TOKEN = config.TOKEN
# This is the url for communicating with your bot
URL = config.URL

# The Line store URL format.
LINE_URL = config.LINE_URL

# The text to display when the sent URL doesn't match.
WRONG_URL_TEXT = config.WRONG_URL_TEXT

# We want to keep checking for updates. So this must be a never ending loop
while True:
    # My chat is up and running, I need to maintain it! Get me all chat updates
    get_updates = json.loads(
                        requests.get(
                            URL + 'getUpdates',
                            params={'offset': last_update}
                            ).content.decode()
    )
    # Ok, I've got 'em. Let's iterate through each one
    for update in get_updates['result']:
        # First make sure I haven't read this update yet
        if last_update < update['update_id']:
            last_update = update['update_id']
            with open('updatefile', "w") as updatefile:
                updatefile.write(str(last_update))
            # I've got a new update. Let's see what it is.
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                sticker_url = update['message']['text']

                if sticker_url[:42] == LINE_URL:
                    # Modify this requirement to be able to read any link sent to the bot??? Maybe?
                    # It's a message! Let's send it back :D
                    # request = requests.get(sticker_url).text
                    name = update['message']['from']['first_name']
                    print(name + " (" + str(chat_id) + ")" + " requested " + sticker_url)
                    send_stickers(sticker_url, URL, chatid = chat_id, remove = False)
                    # Send_stickers should have a try catch with proper error handling
                    # Maybe the send_stickers could be placed in another threat as well,
                    # to not get the bot stuck while following someone's request.
                else:
                    requests.get(URL + 'sendMessage',
                                 params = {'chat_id': chat_id,
                                           'text': WRONG_URL_TEXT}
                                 )
    # Let's wait a few seconds for new updates
    sleep(1)
