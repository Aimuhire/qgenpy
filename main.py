import os
import mysql.connector
from QuoteGen import QuoteGen
from TagGen import TagGen
import time

try:
    myDB = mysql.connector.connect(
        host="localhost",
        user="mars",
        passwd="dGHSN8u3**9(99009$%$%%%mysql",
        database="qpydb",
    )
except Exception as e:
    raise
    print("Failed to connect to db", e)


myCursor = myDB.cursor()

myCursor.execute(
    "CREATE TABLE IF NOT EXISTS quotes (id INT AUTO_INCREMENT PRIMARY KEY,quote VARCHAR(500) NOT NULL UNIQUE KEY,author VARCHAR(255),category VARCHAR(255),tags VARCHAR(255),imgFileName VARCHAR(255) NOT NULL)"
)

insertQuoteSqlFormula = (
    "INSERT INTO quotes (quote,author,category,tags,imgFileName) values(%s,%s,%s,%s,%s)"
)
# checkQuoteSqlFormula='SELECT * FROM quotes WHERE quote="%s"'

# extractorRegEx=u"(\u201c.*)\u2013 *(.*)"
# my csv extractor ^([\w\W]+)\;([\w\W]+)\;([\w\W]+)$
extractorRegEx = "^([\w\W]+)\;([\w\W]+)\;([\w\W]+)$"
QuotesGenerator = QuoteGen(os.path.join("assets", "Quotes.csv"), extractorRegEx)

quoteList = QuotesGenerator.getQuoteList()
MAX_QUOTES_COUNT = len(quoteList)
progressCount = 0
for quoteDict in quoteList:
    # break
    progressCount += 1

    T = TagGen(quoteDict["quote"].lower())
    TAGS = T.getTags()
    quoteDict["tags"] = TAGS
    checkQuoteSqlFormula = (
        "SELECT * FROM quotes WHERE quote='"
        + myDB.converter.escape(quoteDict["quote"])
        + "'"
    )
    myCursor.execute(checkQuoteSqlFormula)
    quoteResult = myCursor.fetchall()
    if not quoteResult:
        (img, logoimg, imgId) = QuotesGenerator.getImgs(quoteDict)
    else:
        MAX_QUOTES_COUNT-=1
        print("--new total-- "+str(MAX_QUOTES_COUNT))
        continue

    print(quoteDict["quote"])
    outputName = str(int(time.time())) + "-" + imgId

    outputImagePath = QuotesGenerator.designQuote(quoteDict, outputName, img, logoimg)
    myCursor.execute(
        insertQuoteSqlFormula,
        (
            quoteDict["quote"],
            quoteDict["author"],
            quoteDict["category"],
            " ".join(quoteDict["tags"]),
            outputName,
        ),
    )
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

myResults = myCursor.fetchall()
 