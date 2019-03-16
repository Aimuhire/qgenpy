# -*- coding: utf-8 -*-
import sys, textwrap, re, os
from random import randint
from urllib import request
import unicodedata
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# fonts
# quote: 56pt Calibri regular center
# author: 56pt adobe devanagari center grey italic
# water mark: 30pt  adobe devanagari left 


class QuoteGen:
    def __init__(self, quoteFile, extractorRegEx):

        self.credit = "aimateur quotes"
        self.extractorRegEx = extractorRegEx
        try:
            qf = open(quoteFile, encoding="utf8") 
            self.quotes = qf.readlines()
        except FileNotFoundError as e:
            raise

    def getQuoteList(self, maxQuotes=0, random=False):
        """Returns list of quotes as dict items
        if maxQuotes is not set or equals zero, returns all quotes in the quote file that satisfy length conditions.
        """
        print("## getting quote list and tag generation ###")
        quoteList = []
        rawList = []
        allQuotesCount = len(self.quotes)

        if maxQuotes == 0 or "maxQuotes" not in vars():
            maxQuotes = allQuotesCount
        if random == True:
            randomP = []
            # get random quotes
            # could shuffle? all do directly with self.quotes.
            # Thought this was faster on bigger lists
            # get random indices(randomP),use them to generate random quote list(rawList)
            while len(randomP) < maxQuotes:
                n = int(randint(0, (allQuotesCount - 1)))
                if n not in randomP:
                    randomP.append(n)
            for n in randomP:
                rawList.append(self.quotes[n])
        else:
            rawList = self.quotes[0:maxQuotes] 
        for quote in rawList: 
            quote = quote.strip()
            try:
                quote, author, category = re.search(self.extractorRegEx, quote).groups()
                if len(author) > 15:
                    authorDiss = re.split("\W", author)
                    author = ""
                    for name in authorDiss:
                        if len(author + name) < 30:
                            author += " " + name
                        else:
                            break
            except AttributeError as e:
                continue

            quoteDict = {} 
            if len(quote) > 500:
                continue
            quoteDict["quote"] = quote.strip()
            quoteDict["author"] = author.strip()
            quoteDict["category"] = category.strip()
            quoteList.append(quoteDict) 
        print("--total--", len(quoteList))

        return quoteList

    def getImgs(self, quoteD):
        """quoteD is a dictionary with quote,author,category and tags
        tags key has a list value
        returns img and logoimg kinda Pillow objects"""

        imgId = ""
        tags = "?" + (",".join(quoteD["tags"]))

        # has to be a loop cz, "?water,abstract" often returns abstract images. So, try option water, if it fails fall back to abstract images, if all fails fallback to full random

        while imgId == "" or imgId == "source-404.jpeg": 
            if imgId == "source-404.jpeg":
                print("## 404 image ##")
                tags = "?" + quoteD["category"]  # will add category over here
            print("Requesting image url...")
            tags= unicodedata.normalize("NFD", tags).encode("ascii", "ignore").decode("utf-8")
            res = request.urlopen(
                "https://source.unsplash.com/random/1080x1080/"+tags
            )
            imgUrl = res.geturl()
            print("...url received...")
            try:
                imgId = re.search("([\w\-. ]+(\.jpeg)+)+", imgUrl).group()
            except AttributeError as e:
                try:
                    imgId = re.search("([\w\-. ]+(\.jpg)+)+", imgUrl).group()
                except AttributeError as e:
                    try:
                        m = re.search(
                            "images\.unsplash\.com((\/\w\/)*\/([\w\-. ]+)+)+", imgUrl
                        ).groups()
                        imgId = m[len(m) - 1] + ".jpeg"
                    except AttributeError as e:
                        print("...exception url pattern mismatch")

        print("Downloading image...")
        imgName = os.path.join("imgs", imgId)
        (imfile, y) = request.urlretrieve(imgUrl, filename=imgName)
        imgName = os.path.join("imgs", imgId) 

        # width: number of max chars per line. depends on quote length, quote size and quote box
        # img = Image.open(imfile)
        img = Image.open(os.path.join("imgs", imgId))
        logoimg = Image.open(os.path.join("assets", "logo.png"))
        logoimg = logoimg.resize((int(img.size[1] / 10), int(img.size[1] / 10)))

        return (img, logoimg, imgId)

    def designQuote(self, quoteD, outputName, img, logoimg):
        """Does the actual quote image design.
        receives:
        quoteD dictionary with quote and author
        outputName a filename string
        img and logoimg are Pillow objects
        """
        ############################################################################
        # >> not implemented: support multiple mode kinda Gray scale / color output
        # >>not implemented diffelent designs
        #     1. lower half b/w quotebox : implemented
        #     2. center quotebox: not implemented
        #############################################################################

        print("Creating quote image...")
        quote = quoteD["quote"]
        author = quoteD["author"]
        wl, hl = logoimg.size
        pad = hl + hl / 3
        # looks weird: int(img.size[1]/54... I tried to make all sizes relative to the image height, so that I may support user uploaded images

        space = int(img.size[1] / 54)
        if len(quote) < 100:
            width = 35
            qfsize = 56
            authorPad = space 
        elif len(quote) < 300:
            width = 45
            qfsize = 46
            authorPad = 0 
        else:
            width = 70
            qfsize = 30
            authorPad = 0
            print("long quote", len(quote)) 

        quote = textwrap.wrap(quote, width=width)
        quoteLines = len(quote)
        quote = "\n".join(quote)

        lowerHalf = (0, int(img.size[1] / 2), img.size[0], img.size[1])
        lowerHalfBox = img.crop(lowerHalf)
        lowerHalfBox = lowerHalfBox.convert("L")
        img.paste(lowerHalfBox, lowerHalf)
        draw = ImageDraw.Draw(img, mode="RGBA")
        draw.rectangle(lowerHalf, fill=(0, 0, 0, 200), outline=None)

        qfont = ImageFont.truetype(
            os.path.join("assets", "Calibri.ttf"), qfsize
        )  # int(img.size[1]/19) )
        afont = ImageFont.truetype(
            os.path.join("assets", "adobe-devanagari_it.otf"), qfsize
        )
        cfont = ImageFont.truetype(
            os.path.join("assets", "adobe-devanagari_re.otf"), int(img.size[1] / 36)
        )
        W, H = img.size
        wq, hq = draw.textsize(quote, qfont)
        wa, ha = draw.textsize(author, qfont)
        wc, hc = draw.textsize(self.credit, cfont)
        draw.multiline_text(
            ((W - wq) / 2, (H + pad) / 2),
            quote,
            (255, 255, 255),
            font=qfont,
            spacing=space,
            align="center",
        )
        draw.multiline_text(
            (
                (W - wa) / 2,
                ((H + pad) / 2) + hq + (space * quoteLines) + (2 * authorPad),
            ),
            author,
            (125, 125, 125),
            font=afont,
            spacing=space,
            align="center",
        )
        draw.text((space, (H - 2 * hc)), self.credit, (100, 100, 100), font=cfont)
        # draw.rectangle(((W-wq)/2,(H+pad)/2,((W-wq)/2)+wq,((H+pad)/2)+hq+(space*quoteLines)),fill=(0,255,0,100),outline=None)
        # img =img.convert("RGBA")

        img.paste(logoimg, (space, int((H - hl) / 2)), mask=logoimg)
        # draw.rectangle((space,int((H-hl)/2),space+wl,hl+int((H-hl)/2)),fill=(0,230,255,100),outline=None)
        img = img.convert("RGB")
        img.save(os.path.join("output", outputName))
        # img.resize((540, 540)).show()
        print("success! imaged saved as " + outputName)
        os.unlink(os.path.join("imgs", re.search("(\-.*)",outputName).group(0)[1:]))
        return os.path.join("output", outputName)
