
# import linebot

#testurl = "https://store.line.me/stickershop/product/10073/en"


#MyBot = linebot.LineBot()

#StickerBot = linebot.StickerGetter()

#StickerBot.download_stickers(testurl)


class A:

    def __init__(self, arg, kind="A kind", folder="A none", *args, **kwargs):
        print("A", "arg=", arg)
        print("A", "kind=", kind)
        print("A", "folder=", folder)


class B(A):
    def __init__(self, kind, *args, **kwargs):
        print("B", "kind=", kind)
        super().__init__(*args, **kwargs)


class C(A):
    def __init__(self, *args, **kwargs):
        folder = kwargs.get("folder")
        print("C", "folder=", folder)
        super().__init__(*args, **kwargs)


class D(B, C):
    def __init__(self, *args, **kwargs):
        print("D")
        super().__init__(*args, **kwargs)


d = D(folder="ha", kind="nope", arg="yes")
