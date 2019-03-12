# -*- coding: utf-8 -*-
import re,os

f=open(os.path.join("assets","tenkwordsbyfreq.txt"))
tenkWords=f.readlines() 
xxf=open(os.path.join("assets","profane.txt"), encoding="utf8")
profaneWords=xxf.readline().split(" ") 

class TagGen(object): 
    def __init__(self,sentence):
        self.sentence=sentence

    def getTags(self):
        
        
        rank=1
        tenkDict={}
        for w in tenkWords:
            tenkDict[w.rstrip()]=rank
            rank+=1

        
        self.sentence=self.sentence.replace(u"\u2019",u" ") 
        sentenceWords=re.split("\W",self.sentence)
        scoreDict={}
        for sWord in sentenceWords:
            try:
                scoreDict[sWord]=tenkDict[sWord]
            except KeyError as e: 
                scoreDict[sWord]=0 if sWord in profaneWords else 10001 

        sortedWords=sorted(scoreDict.items(),key=self.sortKey,reverse=True)
        tags=[]
        tagCount=3 #we want max 3 tags 
        print(sortedWords)
        # I have no idea why variable j is not visible inside the if statement
        for j in range(0,len(sortedWords)): 
            k=j #quick fix
            if not tagCount: 
                break 
                #tag length must be both greater than 3 chars and tag score greater than 100 (to avoid tags that are weak: i.e: #the #a #and )

            if (len(sortedWords[k][0])>3 and sortedWords[k][1]>100 and not re.search("\d",sortedWords[k][0]) ):
                tags.append(sortedWords[k][0]) 
                tagCount-=1

        
        return tags
        
    #custom sorting based on word score value
    def sortKey(self,item):
        return item[1]




