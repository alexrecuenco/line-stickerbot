#The config file should include your token. should be config.py
# TODO: Remove the manual set-up, instead have a setup.py script to deal with setting everything up when installing it.

TOKEN = '<your bot token>'
# This is the url for communicating with your bot
URL = 'https://api.telegram.org/bot%s/' % TOKEN

# The Line store URL format.
LINE_URL = "https://store.line.me/stickershop/product/"

# The text to display when the sent URL doesn't match.
WRONG_URL_TEXT = ("That doesn't appear to be a valid URL. "
                  "To start, send me a URL that starts with " + LINE_URL)
