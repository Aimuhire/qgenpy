import os
import mysql.connector
from QuoteGen import QuoteGen

try:
    myDB = mysql.connector.connect(
        host="localhost",
        user="mars",
        passwd="",
        database="qpydb",
    )
except Exception as e:
    raise
    print("Failed to connect to db", e)



myCursor = myDB.cursor() 

myCursor.execute(
    "CREATE TABLE IF NOT EXISTS quotes (id INT AUTO_INCREMENT PRIMARY KEY,quote VARCHAR(500) NOT NULL,author VARCHAR(255),category VARCHAR(255),tags VARCHAR(255),imgFileName VARCHAR(255) NOT NULL)"
)

insertQuoteSqlFormula="INSERT INTO quotes (quote,author,category,tags,imgFileName) values(%s,%s,%s,%s,%s)"


# extractorRegEx=u"(\u201c.*)\u2013 *(.*)"
# my csv extractor ^([\w\W]+)\;([\w\W]+)\;([\w\W]+)$
extractorRegEx = "^([\w\W]+)\;([\w\W]+)\;([\w\W]+)$"
QuotesGenerator = QuoteGen(os.path.join("assets", "Quotes.csv"), extractorRegEx)

quoteList = QuotesGenerator.getQuoteList(maxQuotes=1000,random=True)
MAX_QUOTES_COUNT = len(quoteList)
progressCount=0
for quoteDict in quoteList: 
    # break
    progressCount+=1
    (img, logoimg, imgId) = QuotesGenerator.getImgs(quoteDict)
    outputImagePath = QuotesGenerator.designQuote(quoteDict, imgId, img, logoimg)
    myCursor.execute(insertQuoteSqlFormula,(quoteDict["quote"],quoteDict["author"],quoteDict["category"]," ".join(quoteDict["tags"]),imgId))
    print("commit to db")
    myDB.commit() 
    print(
        "Completed: "
        + str(progressCount)
        + " of "
        + str(MAX_QUOTES_COUNT)
        + " saved file at "
        + outputImagePath
    )


myCursor.execute("SELECT * FROM quotes")

myResults=myCursor.fetchall()

for a in myResults:
  print(a[1])