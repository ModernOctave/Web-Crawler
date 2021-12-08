# Web-Crawler
Web crawler designed for Niti Ayog search engine project

## Setup
### Python
Please install the following packages in python to run the web crawler

- mechanicalsoup
- pymongo

It is recommended to use a virtual environment to prevent package conflicts

### MongoDB
A MongoDB must be setup and its url should be assigned to the ```MONGODB_URL``` variable.

### Usage
```web_crawler [-c] [-s] <start urls>```

#### start urls
The url from which the crawler should start. Multiple urls can be given

#### -c
Only crawl the given urls

#### -s
Only scrape the given urls