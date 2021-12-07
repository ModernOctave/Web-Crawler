# Web-Crawler
Web crawler designed for Niti Ayog search engine project

## Setup
### Python
Please install the following packages in python to run the web crawler

- mechanicalsoup
- pymongo
- elasticsearch

It is recommended to use a virtual environment to prevent package conflicts

### MongoDB
A MongoDB must be setup and its url should be assigned to the ```MONGODB_URL``` variable in [web_crawler.py](web_crawler.py).

### Elastic Search
Elastic search should be installed and running. You can set the address on which it is running in [index.py](index.py) (default is http://localhost:9200).

### Usage
```web_crawler [-c] [-s] <start urls>```

#### start urls
The url from which the crawler should start. Multiple urls can be given

#### -c
Only crawl the given urls

#### -s
Only scrape the given urls