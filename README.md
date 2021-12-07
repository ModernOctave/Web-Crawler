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
In the main if statement you can set the website variable to the url of the website you wish to crawl. Post this run the ```crawlwebsite``` and ```scrapewebsite``` commands for the website variable as required.