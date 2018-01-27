import os
import urllib.parse
import urllib.request
import json
from zipfile import ZipFile
from wand.image import Image
import cssutils
import requests
from bs4 import BeautifulSoup


class TelegramBot:
    """TelegramBot class defined the basic way to communicate with the json API of the bot"""

    API_URL = 'https://api.telegram.org/bot%s/'

    def __init__(self, token):
        self.TOKEN = token
        self.URL = TelegramBot.API_URL % token
        self._last_update = 0

    def send_message(self, chat_id, message):
        """
        Messages the chat with the text message given
        :param chat_id: ID of chat
        :param message: Message to be delivered
        :return: self
        """
        requests.get(self.URL + 'sendMessage',
                     params={'chat_id': chat_id,
                             'text': message}
                             )
        return self

    def send_message_file(self, chat_id, file):
        """
        Sends to the chat the file
        :param chat_id: Id of chat
        :param file: File to be sent (String)
        :return: self
        """
        with open(file, 'rb') as msg_file:
            requests.post(
                self.URL + 'sendDocument',
                params={'chat_id': chat_id},
                files={'document': msg_file}
            )

        return self

    @property
    def last_update(self):
        """Public API for getting the last update.
        The value is zero when initialized, and it then marks the last message obtained form the TelegramBot"""
        return self._last_update



    def receive_updates(self):
        """
        Receive updates,

        :return: Updates sent to this bot, from the last one that was sent onwards
        """
        # TODO: only receive updates that are messages, ignore the rest.
        if self.last_update == 0:
            updates = \
                json.loads(
                    requests.get(
                        self.URL + 'getUpdates'
                    )
                ).content.decode()
        else:
            updates = \
                json.loads(
                    requests.get(
                        self.URL + 'getUpdates',
                        params={'offset': self.last_update}
                    ).content.decode()
                )
        for update in updates['result']:
            if self.last_update < update['update_id']:
                self._last_update = update['update_id']

        return updates


class StickerGetter:

    def __init__(self, folder="downloads", *args, **kwargs):
        self.folder = folder


    def download_stickers(self, page):
        """
        Downloads stickers from the page
        There should be a way to tell the program that no stickers were found and react to that
        :param page: page downloaded
        :return: None if it didn't load any picture, otherwise it lists the files in which the images were saved.
        """
        images = page.find_all('span', attrs={"style": not ""})
        index = 0
        # If the images is empty it should return an exception and send a message or something
        if 0 >= len(images):
            return None
        assert 0 < len(images)
        for image in images:
            index += 1
            imageurl = cssutils.parseStyle(image['style'])['background-image'].replace('url(', '').replace(')', '')
            imageurl = imageurl[1:-15]
            response = urllib.request.urlopen(imageurl)
            resize_and_save_sticker(response, imageurl, folder, index)
            print("Done saving the sticker with number " + str(index))

    def load_image(self, image_url):
        """

        :param image_url: Url from which to download image
        :return: Resize image to appropriate size
        """
        pass

    def save_image(self, name):
        """

        :param name: Saves in the folder/name.png file
        :return:
        """


class LineBot(TelegramBot, StickerGetter):

    LINE_URL = "https://store.line.me/stickershop/product/"
    WRONG_URL_TEXT = ("That doesn't appear to be a valid URL. "
                      "To start, send me a URL that starts with " + LINE_URL)

    def __init__(self, token, download - ):
        super().__init__(token)

    def send_stickers_from_updates(self, updates=None):
        """
        Gets the updates from an array and interacts with them to send the users stickers if they sent a correct URL
        :param updates: If an array of updates is not given explicitly, it will call self.receive_updates to receive them
         (This is done, so that various LineBots can interact asynchronously with chats if this was needed.
        :return:
        """
        if updates is None:
            updates = self.receive_updates()

        for update in updates['result']:
            if 'message' in update:
                chat_id = update['message']['chat']['id']
                message_text = update['message']['text']

                if message_text[:len(self.LINE_URL)] != self.LINE_URL:
                    self.send_message(chat_id, self.WRONG_URL_TEXT)
                else:
                    self.send_stickers_to_chat(message_text, chat_id)

        return self

    def send_stickers_to_chat(self, received_message, chat_id):
        """
        Find the url in received_message and tries to fecth the stickers and send them to the chat id as a zip.
        :param received_message: Text message received
        :param chat_id: chat ID
        :return: self
        """
        assert isinstance(received_message, str)
        url = received_message.split(" ")[0]
        page = BeautifulSoup(requests.get(url).text, "html.parser")
        title = page.title.text
        fetching_message = " ".join((
            "Fetching",
            title,
            "from",
            url
        ))
        self.send_message(chat_id, fetching_message) \
            .download_stickers(page) \
            .send_message(chat_id, "Fetched, sending") \
            .send_stickers(chat_id, title)

        return self

    def send_stickers(self, chat_id, name):
        """
        It should send the stickers to the chat_id named name
        :param chat_id: Id of the corresponding chat
        :param name: Name of the set of stickers to be sent
        :return: self
        """

        pass

def download_stickers(page, folder = "downloads/"):
    images = page.find_all('span', attrs={"style": not ""})
    index = 0
    # If the images is empty it should return an exception and send a message or something
    assert 0 < len(images)
    for image in images:
        index += 1
        imageurl = cssutils.parseStyle(image['style'])['background-image'].replace('url(', '').replace(')', '')
        imageurl = imageurl[1:-15]
        response = urllib.request.urlopen(imageurl)
        resize_and_save_sticker(response, imageurl, folder, index)
        print("Done saving the sticker with number " + str(index))



def resize_and_save_sticker(image, image_url, folder, index):
    # From the sticker telegram bot:
    #  The image file should be in PNG format with a transparent layer,
    # must fit into a 512x512 square (one of the sides must be 512px and the other 512px or less).

    filename = image_url[-7:-4] + str(index) + '.png'
    # Consider hassing the url into hexadecimal of 32 characters? this would probably be inconsistent...

    with Image(file=image) as img:
        # From the telegram
        if img.width > img.height:
            img.resize(512, int(512 * img.height / img.width), 'mitchell')
        else:
            img.resize(int(512 * img.width / img.height), 512, 'mitchell')
        img.save(filename=os.path.join("folder", filename))
        # Consider saving in downloads in a different folder depending on the product ID and keep them on a database.

    return filename


def send_stickers(page_url, URL, chat_id, remove=True):
    page = BeautifulSoup(requests.get(page_url).text, "html.parser")
    stickertitle = page.title.string
    # TODO: make sure that if the empty has no stickers, to simply not do anything
    # TODO: Consider breaking up downloading and sending into two independent functions.
    # Right now it is doing both in the same function... which is not very sound

    requests.get(URL + 'sendMessage',
                 params={'chat_id': chat_id,
                         'text': "Fetching \"" + stickertitle + "\""})
    # The URL already follows the convention written above, we should be able to identify the prduct ID easily
    try:
        download_stickers(page)
    except AssertionError:
        print("There were no stickers found on the page (maybe we are in the wrong region to see them)")
        requests.get(URL + 'sendMessage',
                     params={'chat_id': chat_id,
                             'text': "No stickers were downloaded from the url. Maybe the stickers are region locked?"}
                     )
        return False

    with ZipFile('stickers.zip', 'w') as stickerzip:
        for root, dirs, files in os.walk("downloads/"):
            for file in files:
                stickerzip.write(os.path.join(root, file))
                if remove:
                    os.remove(os.path.join(root, file))
    with open('stickers.zip', 'rb') as stickers_zipfile:
        requests.post(
            URL + 'sendDocument',
            params={'chat_id': chat_id},
            files={'document': stickers_zipfile}
        )
    print("Stickers sent")
    return True
