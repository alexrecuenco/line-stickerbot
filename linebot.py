import os
import urllib.parse
import urllib.request
from zipfile import ZipFile
from wand.image import Image
import cssutils
import requests
from bs4 import BeautifulSoup

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
    # TODO: Consider breaking up downloading and sending into two independent funcitons.
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
