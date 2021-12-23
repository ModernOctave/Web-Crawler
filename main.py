from web_crawler import crawler
import json

if __name__ == '__main__':
    myCrawler = crawler('mongodb://localhost:27017/')
    
    f = open("urls.json", "r")
    urls = json.loads(f.read())

    for url in urls:
        myCrawler.crawlWebsite(url,url)
        myCrawler.scrapeWebsite(url,url)