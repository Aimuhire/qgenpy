

# -*- coding: utf-8 -*-
import sys,textwrap,re,os
from urllib import request
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from TagGen import TagGen
#fonts 
# quote: 56pt Calibri regular center
# author: 56pt adobe devanagari center grey italic
# water mark: 30pt  adobe devanagari left 
 

class QuoteGen:
  def __init__(self,quoteFile,extractorRegEx): 

      self.credit="aimateur quotes" 
      qf=open(os.path.join("assets","quotes.txt"), encoding="utf8")
      self.quotes=qf.readlines()  
      self.extractorRegEx=extractorRegEx 


  def getQuoteList(self):
    quoteList=[]
    for quote in self.quotes: 
      quote=quote.strip()
      try:
        quote,author=re.search(self.extractorRegEx,quote).groups()  
        
        if len(author)>15:
          authorDiss=re.split("\W",author)
          author=""
          for name in authorDiss:
            if len(author+name)<30:
              author+=" "+name
            else:
              break 
      except AttributeError as e:
        continue
        
      T=TagGen(quote.lower()) 
      TAGS=T.getTags() 
      quoteList.append((quote,author,TAGS))   
      print(TAGS)
    print("--total--",len(quoteList))
    return quoteList

  def getImgs(self,quoteT):
    """quoteT is a turple with (quote,author,tags)
        tags is a list
        returns img and logoimg kinda pillow objects"""

    imgId=""
    tags="?"+(",".join(quoteT[2])) 

    #has to be a loop cz, "?water,abstract" often returns abstract images. So, try option water, if it fails fall back to abstract images, if all fails fallback to full random
    while imgId =="" or imgId == "source-404":
      if imgId == "source-404":
        tags="?abstract" #will add category over here
      res=request.urlopen("https://source.unsplash.com/random/1080x1080/"+tags)

      imgUrl=res.geturl()   
      print("...url received...")
      try:
        imgId=re.search("([\w\-. ]+(\.jpeg)+)+",imgUrl).group()       
      except AttributeError as e: 
        try:
          imgId=re.search("([\w\-. ]+(\.jpg)+)+",imgUrl).group()
        except AttributeError as e: 
          try:
            m=re.search("images\.unsplash\.com((\/\w\/)*\/([\w\-. ]+)+)+",imgUrl).groups()
            imgId=m[len(m)-1]+".jpeg"
          except AttributeError as e:
            print("...exception url pattern mismatch") 

    print("..downloading image...")  
    imgName=os.path.join("imgs",imgId)
    (imfile,y)=request.urlretrieve(imgUrl,filename=imgName)  
    imgName=os.path.join("imgs",imgId)
    (imfile,y)=request.urlretrieve(imgUrl,filename=imgName) 

    # width: number of max chars per line. depends on quote length, quote size and quote box
    # img = Image.open(imfile)
    img = Image.open(os.path.join("imgs",imgId))
    logoimg=Image.open(os.path.join("assets","logo.png")) 
    logoimg=logoimg.resize((int(img.size[1]/10), int(img.size[1]/10)))

    return (img,logoimg,imgId)



  def designQuote(self,quoteT,imgId,img,logoimg): 
    quote=quoteT[0]
    author=quoteT[1]

    wl,hl=logoimg.size 
    pad=hl+hl/3
    # looks weird: int(img.size[1]/54... I tried to make all sizes relative to the image height, so that I may support user uploaded images

    space=int(img.size[1]/54) 
    if len(quote) < 100 :
      width=35
      qfsize=56
      authorPad=space
      print("less 100",len(quote))
    elif len(quote) < 300:
      width=45
      qfsize=46
      authorPad=0
      print("less 300",len(quote)) 
    else:
      print("too long",len(quote))
      

    quote=textwrap.wrap(quote,width=width)
    quoteLines=len(quote) 
    quote="\n".join(quote)

    lowerHalf=(0,int(img.size[1]/2),img.size[0],img.size[1])
    lowerHalfBox=img.crop(lowerHalf)
    lowerHalfBox=lowerHalfBox.convert("L") 
    print(lowerHalfBox,lowerHalf)
    img.paste(lowerHalfBox,lowerHalf)
    draw = ImageDraw.Draw(img,mode="RGBA")  
    draw.rectangle(lowerHalf,fill=(0,0,0,200),outline=None)
    
    qfont = ImageFont.truetype(os.path.join("assets","Calibri.ttf"), qfsize)#int(img.size[1]/19) )  
    afont = ImageFont.truetype(os.path.join("assets","adobe-devanagari_it.otf"),qfsize)   
    cfont = ImageFont.truetype(os.path.join("assets","adobe-devanagari_re.otf"),int(img.size[1]/36) )  
    W,H=img.size
    wq,hq=draw.textsize(quote,qfont) 
    wa,ha=draw.textsize(author,qfont)
    wc,hc=draw.textsize(self.credit,cfont)
    draw.multiline_text(((W-wq)/2,(H+pad)/2),quote,(255,255,255),font=qfont,spacing=space,align="center")  
    draw.multiline_text(((W-wa)/2,((H+pad)/2)+hq+(space*quoteLines)+(2*authorPad)),author,(125,125,125),font=afont,spacing=space,align="center")  
    draw.text((space,(H-2*hc)),self.credit,(100,100,100),font=cfont) 
    # draw.rectangle(((W-wq)/2,(H+pad)/2,((W-wq)/2)+wq,((H+pad)/2)+hq+(space*quoteLines)),fill=(0,255,0,100),outline=None)
    # img =img.convert("RGBA") 


    img.paste(logoimg,(space,int((H-hl)/2)),mask=logoimg)
    # draw.rectangle((space,int((H-hl)/2),space+wl,hl+int((H-hl)/2)),fill=(0,230,255,100),outline=None)
    print((space,int((H-hl)/2),space+wl,hl+int((H-hl)/2)))
    img =img.convert("RGB")  
    img.save(os.path.join("output",str(len(quoteT[0]))+imgId)) 
    img.show()
    print("success! imaged saved at :output\\"+imgId)
    return os.path.join("output",str(len(quoteT[0]))+imgId)



extractorRegEx=u"(\u201c.*)\u2013 *(.*)"
QuotesGenerator = QuoteGen(os.path.join("assets","quotes.txt"),extractorRegEx)

quoteList=QuotesGenerator.getQuoteList()
MAX_QUOTES_COUNT=len(quoteList)
for i in range(0,MAX_QUOTES_COUNT):
  (img,logoimg,imgId)=QuotesGenerator.getImgs(quoteList[i])
  outputImagePath=QuotesGenerator.designQuote(quoteList[i],imgId,img,logoimg)
  print("Completed: "+str(i)+ "of "+str(MAX_QUOTES_COUNT)+" saved file at "+outputImagePath)