import mechanicalsoup
import json
from urllib.parse import urlsplit
import datetime
import pymongo

MONGODB_URL = "mongodb://localhost:27017/"

# Crawl a given website
def crawlWebsite(url):
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

    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["web_crawler"]
    mycol = mydb["url_data"]

    myquery = { "url": url }
    mycol.update_one(myquery, { "$set": url_data }, upsert=True)


            

# Scrape data from a website
def scrapeWebsite(url):
    myclient = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = myclient["web_crawler"]
    mycol = mydb["url_data"]

    myquery = { "url": url }
    myresult = mycol.find(myquery)

    for result in myresult:
        data = scrape(url,result['paths'])

        # Store in MongoDB
        # mycol = mydb["page_data"]
        # myquery = { "url": url }
        # mycol.update_one(myquery, { "$set": data_entry }, upsert=True)

        # Export as json
        exportData(data)

# Scrape data from all paths for a given site
def scrape(url,paths):
    data = []
    for path in paths:
        # Open browser
        browser = mechanicalsoup.StatefulBrowser()

        # Open page at the path
        browser.open(url+path)
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

    return data

def exportURLs(url_data):
    f = open("urls.json", "w", encoding='utf-8')
    f.write(json.dumps(url_data,ensure_ascii=False,indent=4))
    f.close()

def exportData(data):
    f = open("data.json", "w", encoding='utf-8')
    f.write(json.dumps(data,ensure_ascii=False,indent=4))
    f.close()

if __name__ == '__main__':
    website = "https://www.iitb.ac.in/"
    crawlWebsite(website)
    scrapeWebsite(website)