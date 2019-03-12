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
# for imfile in ["imgs/8.jpeg"]:
# imfile="imgs/alfonso.jpg"  

credit="aimateur quotes"
rootDir=os.path.join("D:\\","apps","qgenpy","imgs","")
print(rootDir)
qf=open(os.path.join("assets","quotes.txt"), encoding="utf8")
quotes=qf.readlines()  


for quote in quotes: 
    quote=quote.strip()
    try:
      quote,author=re.search(u"(\u201c.*)\u2013 *(.*)",quote).groups()  
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
    listed.append((quote,author,TAGS))  
    print("######################################")
print("--total--",len(listed))
for quoteT in listed:   
  imgId=""
  tags="?"+(",".join(quoteT[2])) 
  quote=quoteT[0]
  author=quoteT[1]

  print("Generating quote "+str(listed.index(quoteT)+1)+" of "+str(len(listed))+"\nUsing tags: "+tags)
  #has to be a loop cz, "?water,abstract" often returns abstract images. So, try option water, if it fails fall back to abstract images, if all fails fallback to full random
  while imgId =="" or imgId == "source-404":
    if imgId == "source-404":
      tags="?abstract"
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
  imgName=rootDir+imgId 

  imgName=os.path.join("imgs",imgId)
  (imfile,y)=request.urlretrieve(imgUrl,filename=imgName) 
  print("..manufacturing image...") 
  # width: number of max chars per line. depends on quote length, quote size and quote box
  # img = Image.open(imfile)
  img = Image.open(os.path.join("imgs",imgId))
  logoimg=Image.open(os.path.join("assets","logo.png")) 
  logoimg=logoimg.resize((int(img.size[1]/10), int(img.size[1]/10)))
  wl,hl=logoimg.size 
  pad=hl+hl/3
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
    continue
     

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
  wc,hc=draw.textsize(credit,cfont)
  draw.multiline_text(((W-wq)/2,(H+pad)/2),quote,(255,255,255),font=qfont,spacing=space,align="center")  
  draw.multiline_text(((W-wa)/2,((H+pad)/2)+hq+(space*quoteLines)+(2*authorPad)),author,(125,125,125),font=afont,spacing=space,align="center")  
  draw.text((space,(H-2*hc)),credit,(100,100,100),font=cfont) 
  # draw.rectangle(((W-wq)/2,(H+pad)/2,((W-wq)/2)+wq,((H+pad)/2)+hq+(space*quoteLines)),fill=(0,255,0,100),outline=None)
  # img = img.convert("RGBA")  
  img.paste(logoimg,(space,int((H-hl)/2)),mask=logoimg)
  # draw.rectangle((space,int((H-hl)/2),space+wl,hl+int((H-hl)/2)),fill=(0,230,255,100),outline=None)
  print((space,int((H-hl)/2),space+wl,hl+int((H-hl)/2)))
  img =img.convert("RGB")  
  img.save(os.path.join("output",str(len(quoteT[0]))+imgId)) 
  img.show()
  print("success! imaged saved at :output\\"+imgId)