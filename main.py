# python3

import json
import logging
import os
import urllib.parse
import urllib.request
from time import sleep
from zipfile import ZipFile

import cssutils
import requests
from bs4 import BeautifulSoup
from wand.image import Image

import config

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


def dl_stickers(page):
    images = page.find_all('span', attrs={"style": not ""})
    index = 0
    for image in images:
        index += 1
        imageurl = image['style']
        imageurl = cssutils.parseStyle(imageurl)
        imageurl = imageurl['background-image']
        imageurl = imageurl.replace('url(', '').replace(')', '')
        imageurl = imageurl[1:-15]
        response = urllib.request.urlopen(imageurl)
        resize_sticker(response, imageurl, index)


def resize_sticker(image, imageurl, index):
    filename = imageurl[-7:-4] + str(index) + '.png'
    # Consider hassing the url into hexadecimal of 32 characters? this would probably be inconsistent...

    with Image(file=image) as img:
        ratio = 512.0 / (max(img.width, img.height))
        img.resize(int(img.width * ratio), int(img.height * ratio), 'mitchell')
        # Consider if there is another method that doesn't relly on a ratio, this seems inneficcient
        img.save(filename=os.path.join("downloads", filename))
        # Consider saving in downloads in a different folder depending on the product ID and keep them on a database.


def send_stickers(page, remove=True):
    dl_stickers(page)
    with ZipFile('stickers.zip', 'w') as stickerzip:
        for root, dirs, files in os.walk("downloads/"):
            for file in files:
                stickerzip.write(os.path.join(root, file))
                if remove:
                    os.remove(os.path.join(root, file))
    with open('stickers.zip', 'r') as stickers_zipfile:
        requests.post(
            URL + 'sendDocument',
            params={'chat_id': update['message']['chat']['id']},
            files={'document': stickers_zipfile}
        )
    print("Stickers sent")


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
                if update['message']['text'][:42] == LINE_URL:
                    # It's a message! Let's send it back :D
                    sticker_url = update['message']['text']
                    user = update['message']['chat']['id']
                    request = requests.get(sticker_url).text
                    stickerpage = BeautifulSoup(request, "html.parser")
                    stickertitle = stickerpage.title.string
                    name = update['message']['from']['first_name']
                    requests.get(URL + 'sendMessage',
                                 params={'chat_id': update['message']['chat']['id'],
                                         'text': "Fetching \"" + stickertitle + "\""})
                    print(name + " (" + str(user) + ")" + " requested " + sticker_url)
                    send_stickers(stickerpage)
                    # Send_stickers should have a try catch with proper error handling
                    # Maybe the send_stickers could be placed in another threat as well, to not get the bot stuck while following someone's request.
                else:
                    requests.get(URL + 'sendMessage',
                                 params={'chat_id': update['message']['chat']['id'],
                                         'text': WRONG_URL_TEXT}
                                 )
    # Let's wait a few seconds for new updates
    sleep(1)
