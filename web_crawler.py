import requests
import json
from bs4 import BeautifulSoup
from urllib.request import urlopen

# creating an empty list to store all the urls on the given website
urls = []

# function to crawl the complete website
def crawl_php(site):
    current_site=""

    # getting the request from the url
    source_code = requests.get(site)
    soup = BeautifulSoup(source_code.text, 'lxml')

    # getting php files
    for i in soup.find_all('a',href=True):
        href = i['href']
        if('php' in href and ('https' not in href and 'http' not in href)):
            current_site = website + href
            if current_site not in urls:
                urls.append(current_site)
                # recursion
                crawl_php(current_site)

# def crawl_html(base_url,site):
#     current_site=""

#     # getting the request from the url
#     source_code = requests.get(site, verify=False)
#     soup = BeautifulSoup(source_code.text, 'lxml')

#     # getting html files
#     for i in soup.find_all('a'):
#         href = i['href']
#         if('html' in href and 'https' not in href):
#             current_site = base_url + href
#             if current_site not in urls:
#                 urls.append(current_site)
#                 print(current_site)
#                 #crawl_html(base_url,current_site)

def write_urls(urls):
    file = open('urls.txt', 'w')
    #file.writelines(urls)
    file.write('\n'.join(urls))
    file.close()

def get_data():
    json_file = open('data.json', 'w', encoding='utf-8')
    json_file.write('[\n')
    url_file = open('urls.txt', 'r')
    file_urls = url_file.readlines()
    count = 1
    for url in file_urls:
        print(count)
        count += 1
        try:
            html = urlopen(url).read()
        except:
            continue
        soup = BeautifulSoup(html, features="html.parser")

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        text = soup.get_text()

        # break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)

        json_object = {
            "url" : url.replace('\n',""),
            "data" : text
        }
        json.dump(json_object, json_file, ensure_ascii=False, indent=4)
        if(count<len(urls)):
            json_file.write(',\n')

    json_file.write(']')
    

if __name__ == '__main__':
    website = "https://www.iitdh.ac.in/"
    urls.append(website)
    # crawl_html("https://smp.iitdh.ac.in","https://smp.iitdh.ac.in")
    # crawl_html("https://cdc.iitdh.ac.in","https://cdc.iitdh.ac.in")
    print("crawling...")
    crawl_php(website)
    write_urls(urls)
    get_data()