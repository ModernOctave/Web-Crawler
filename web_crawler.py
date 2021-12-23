import mechanicalsoup
import json
from urllib.parse import urlsplit
import datetime
import pymongo
import sys, getopt
from index import Index

class crawler:
    def __init__(self,MONGODB_URL):
        self.myclient = pymongo.MongoClient(MONGODB_URL, serverSelectionTimeoutMS=1000)

    # Crawl a given website
    def crawlWebsite(self,website,url):
        # Crawl starting from given url
        def crawl(url):
            print("Media URLs: "+str(len(media_urls))+"   Crawled Pages: "+str(len(crawled_urls))+"   Crawling: "+url)

            # Open the url
            browser.open(url)

            # Get all links
            links = browser.links()

            # Strip any whitespace
            links = list(link['href'].strip() for link in links)

            # Ensure they are from the same website
            links = list(link for link in links if (len(urlsplit(link).netloc) == 0) or (urlsplit(link).netloc == urlsplit(url).netloc))

            # Only take http links
            links = list(link for link in links if (urlsplit(link).scheme == '') or (urlsplit(link).scheme == 'https') or (urlsplit(link) == 'http'))

            # Parse to get correct paths
            for i in range(len(links)):
                link = urlsplit(links[i]).path
                if not link:
                    links[i] = link
                elif link[0] == '/':
                    links[i] = link.strip('/')
                elif link[0:2] == './':
                    root = urlsplit(url).path.strip("/")
                    if root:
                        links[i] = root+link.strip('.')
                    else:
                        links[i] = link.strip('./')
                else:
                    url_split = urlsplit(url).path.split('/')
                    url_split = list(x for x in url_split if x)
                    url_root = '/'.join(url_split[0:len(url_split)-1])
                    if url_root:
                        links[i] = url_root+'/'+link.strip('../')

            # Remove any blank links
            links = list(link for link in links if link)

            # For each link not in urls
            for link in links:
                media = False

                if (link not in crawled_urls) and (link not in to_crawl):
                    if link not in media_urls:
                        for type in ['jpg', 'JPG', 'png', 'jpeg', 'pdf', 'gif']:
                            if type in link:
                                media_urls.add(link)
                                media = True
                        
                        if media:
                            continue
                        
                        # Open the url
                        try:
                            res = browser.open(website+link, timeout=15)
                            # Make sure it is a webpage
                            if 'text/html' in res.headers['Content-Type']:
                                to_crawl.add(link)
                            else:
                                media_urls.add(link)
                        except:
                            print("Could not open "+website+link+" !")

        # Open browser
        browser = mechanicalsoup.StatefulBrowser()

        # Crawl the website
        crawled_urls = set()
        media_urls = set()
        to_crawl = set()

        to_crawl.add(urlsplit(url).path.strip("/"))

        print("Crawling:")
        while to_crawl:
            for x in to_crawl.copy():
                crawl(website+x)
                to_crawl.remove(x)
                crawled_urls.add(x)

        # Store the url data
        url_data = {
            "url": url,
            "paths": list(crawled_urls),
            "crawled_at": str(datetime.datetime.now())
        }

        mydb = self.myclient["web_crawler"]
        mycol = mydb["url_data"]

        myquery = { "url": url }
          mycol.update_one(myquery, { "$set": url_data }, upsert=True)   


            
               
    # Scrape data from a website
    def scrapeWebsite(self,website,url):
        mydb = self.myclient["web_crawler"]
        mycol = mydb["url_data"]

        myquery = { "url": url }
        myresult = mycol.find(myquery)

        for result in myresult:
            data = self.scrape(website,url,result['paths'])

            # Store in MongoDB
            # mycol = mydb["page_data"]
            # myquery = { "url": url }
            # mycol.update_one(myquery, { "$set": data_entry }, upsert=True)

            # Export as json
            self.exportData(website,data)

    # Scrape data from all paths for a given site
    def scrape(self,website,url,paths):
        data = []
        i = 1
        total = len(paths)
        for path in paths:
            # Open browser
            browser = mechanicalsoup.StatefulBrowser()

            # Open page at the path
            try:
                browser.open(url+path)
                print(str(i)+"/"+str(total)+") Scrapping: "+url+path)
                page = browser.page

                # Get text
                text = page.get_text()
                # Separate lines and join
                lines = list(line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)

                # Add data to array
                page_data = {
                        "path" : website+path,
                        "data" : text
                    }
                data.append(page_data)
                i += 1
            except:
                print(f"Could not open {website+path}!")

        return data

    def exportURLs(self,url_data):
        f = open("urls.json", "w")
        f.write(json.dumps(url_data,indent=4))
        f.close()

    def exportData(self,website,data):
        index = Index()
        for doc in data:
            index.IndexFile(doc)

def main(argv):
    help_text = """
    Usage:
        web_crawler [-c] [-s] <start urls>

    start_urls:
        The url from which the crawler should start. Multiple urls can be given

    -c:
        Only crawl the given urls

    -s:
        Only scrape the given urls
    """

    try:
        opts, websites = getopt.getopt(argv,"csh",[])
    except getopt.GetoptError:
        print(help_text)
        sys.exit(2)

    run_type = "both"

    for opt, arg in opts:
        if opt == '-c':
            if run_type == "scrape":
              print("Cannot take -c and -s arguments at same time")
              exit(1)
            run_type = "crawl"
        elif opt == '-s':
            if run_type == "crawl":
              print("Cannot take -c and -s arguments at same time")
              exit(1)
            run_type = "scrape"
        elif opt == '-h':
            print(help_text)

    myCrawler = crawler('mongodb://localhost:27017/')

    if run_type == "both":
        for website in websites:
            myCrawler.crawlWebsite(website,website)
            myCrawler.scrapeWebsite(website,website)
    elif run_type == "crawl":
        for website in websites:
            myCrawler.crawlWebsite(website,website)
    elif run_type == "scrape":
        for website in websites:
            myCrawler.scrapeWebsite(website,website)


if __name__ == '__main__':
    main(sys.argv[1:])