import os
import urllib.parse
import urllib.request
from zipfile import ZipFile
from wand.image import Image
import cssutils
import requests
from bs4 import BeautifulSoup

def download_stickers(page):
    images = page.find_all('span', attrs={"style": not ""})
    index = 0
    # If the images is empty it should return an exception and send a message or something
    for image in images:
        index += 1
        imageurl = image['style']
        imageurl = cssutils.parseStyle(imageurl)
        imageurl = imageurl['background-image']
        imageurl = imageurl.replace('url(', '').replace(')', '')
        imageurl = imageurl[1:-15]
        response = urllib.request.urlopen(imageurl)
        resize_sticker(response, imageurl, index)
        print("Done with the sticker number " + str(index))



def resize_sticker(image, imageurl, index):
    # From the sticker telegram bot:
    #  The image file should be in PNG format with a transparent layer,
    # must fit into a 512x512 square (one of the sides must be 512px and the other 512px or less).

    filename = imageurl[-7:-4] + str(index) + '.png'
    # Consider hassing the url into hexadecimal of 32 characters? this would probably be inconsistent...

    with Image(file=image) as img:
        # From the telegram
        if img.width > img.height:
            img.resize(512, int(512 * img.height / img.width), 'mitchell')
        else:
            img.resize(int(512 * img.width / img.height), 512, 'mitchell')
        img.save(filename=os.path.join("downloads", filename))
        # Consider saving in downloads in a different folder depending on the product ID and keep them on a database.

    return filename


def send_stickers(page_url, URL, chatid, remove=True):
    page = BeautifulSoup(requests.get(page_url).text, "html.parser")
    stickertitle = page.title.string
    #TODO: make sure that if the empty has no stickers, to simply not do anything
    # TODO: Consider breaking up downloading and sending into two independent funcitons.
    # Right now it is doing both in the same function... which is not very sound
    
    requests.get(URL + 'sendMessage',
                 params={'chat_id': chat_id,
                         'text': "Fetching \"" + stickertitle + "\""})
    try:
        download_stickers(page)
        with ZipFile('stickers.zip', 'w') as stickerzip:
            for root, dirs, files in os.walk("downloads/"):
                for file in files:
                    stickerzip.write(os.path.join(root, file))
                    if remove:
                        os.remove(os.path.join(root, file))
        with open('stickers.zip', 'r') as stickers_zipfile:
            requests.post(
                URL + 'sendDocument',
                params={'chat_id': chatid},
                files={'document': stickers_zipfile}
            )
        print("Stickers sent")
        return True
    except:
        print("Unexpected error")
        requests.get(URL + 'sendMessage',
                     params={'chat_id': chatid,
                             'text': "An unexpected error occurred, please try again"}
                     )
        return False
