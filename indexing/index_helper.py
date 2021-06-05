import json
import re


def readwiki(wikiFile):
    re = []
    with open(wikiFile) as wiki:
        wikiLine = wiki.readline()
        while wikiLine:
            re.append(wikiLine)
            wikiLine = wiki.readline()
    return re


def parseWikiJsons(wikiFile, only_meta=False):
    jsonStrings = readwiki(wikiFile)
    articles = []
    for jstr in jsonStrings:
        article = json.loads(jstr)
        article["uid"] = int(article["url"][article["url"].find("=") + 1:])
        article["text"] = article["text"]
        article["title"] = article["title"]
        articles.append(article)

    return articles


def getStopwords(stopwordsFile):
    f = open(stopwordsFile, 'r')
    stopwords = [line.rstrip() for line in f]
    f.close()
    return stopwords


def getTerms(line):
    line = line.lower()
    line = re.sub(r'[^a-z0-9 ]', ' ', line)
    line = line.split()
    stopwords = getStopwords('indexing/stopwords.txt')
    line = [x for x in line if x not in stopwords]
    return line