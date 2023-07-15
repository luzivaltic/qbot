import requests
import re
import urllib.request
from bs4 import BeautifulSoup
from collections import deque
from html.parser import HTMLParser
from urllib.parse import urlparse
import os
from time import sleep

HTTP_URL_PATTERN = r'^http[s]*://.+'

start_urls = [
    "https://www.cohost.vn",
]

visited = []

class HyperlinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hyperlinks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag == "a" and "href" in attrs:
            self.hyperlinks.append(attrs["href"])

def get_hyperlinks(url):
    try:
        with urllib.request.urlopen(url) as response:
            if not response.info().get("Content-Type").startswith("text/html"):
                return []

            html = response.read().decode("utf-8")
    except Exception as e:
        return []

    parser = HyperlinkParser()
    parser.feed(html)

    return parser.hyperlinks

def get_domain_hyperlinks(local_domain, url):
    clean_links = []
    for link in set(get_hyperlinks(url)):
        clean_link = None
        if re.search(HTTP_URL_PATTERN, link):
            url_obj = urlparse(link)
            # check if the domain is the same
            if url_obj.netloc == local_domain:
                clean_link = link
        else:
            if link.startswith("/"):
                link = link[1:]
            elif link.startswith("#") or link.startswith("mailto:"):
                continue
            clean_link = os.path.join("https://" + local_domain, link)

        if clean_link is not None:
            if clean_link.endswith("/"):
                clean_link = clean_link[:-1]

            clean_links.append(clean_link)

    return list(set(clean_links))

def crawl(url):
    url = url.replace(' ', '')
    local_domain = urlparse(url).netloc
    queue = deque([url])
    seen = set([url])
    if not os.path.exists("text/"):
        os.mkdir("text/")

    if not os.path.exists("text/" + local_domain + "/"):
        os.mkdir("text/" + local_domain + "/")

    if not os.path.exists("processed"):
        os.mkdir("processed")
        
    while queue:
        sleep(1)
        url = queue.pop()

        try:
            texts = requests.get(url).text
            soup = BeautifulSoup(texts)
            paragraph = ""
            mydivs = soup.find_all("div", class_=["margin--bottom margin--xsmall", 
                                                  "margin--bottom margin--small"])
            for mydiv in mydivs:
                text_my_div = ' '.join(mydiv.stripped_strings)
                text_my_div = text_my_div.encode("latin1").decode("utf-8")

                try:
                    nextdiv = mydiv.find_next_sibling("div")
                    text_next_div = ' '.join(nextdiv.stripped_strings)
                    text_next_div = text_next_div.encode("latin1").decode("utf-8")

                    if text_my_div not in visited and text_next_div not in visited:
                        paragraph = paragraph + text_my_div + ' ' + text_next_div + '\n'
                        visited.append(text_my_div)
                        visited.append(text_next_div)

                except Exception as e:
                    continue
            
        except Exception as e:
            paragraph = ""  

        try: 
            texts = requests.get(url).text
            soup = BeautifulSoup(texts)
            all_page_text = soup.get_text('\n').encode("latin1").decode("utf-8")
            for text in all_page_text.splitlines():
                if text not in visited:
                    paragraph = paragraph + text + '\n'
                    visited.append(text)
        except Exception as e:
            pass

        if paragraph == "":
            print(url, "Empty Page")
        else:
            try:
                file_name = url.replace("https://", "").replace("/", "_")
                file_name = file_name.replace(" ", "").replace(".", "_") + ".txt"
                print("url : ", url)
                with open(f"text/{local_domain}/{file_name}",
                            "w", encoding="utf-8") as f:
                    print("committed : ", file_name)
                    f.write(paragraph)
            except Exception as e:
                print(url, "Broken File")

        for link in get_domain_hyperlinks(local_domain, url):
            base_link = link.replace(local_domain, "")
            if "." in base_link and not base_link.endswith(".com"):
                continue
            if link not in seen:
                queue.append(link)
                seen.add(link)

'''
if __name__ == "__main__":
    for url in start_urls:
        visited = []
        crawl(url)
'''

html = """
<article>
   <h2>Google Chrome</h2>
   <span>
      <p>Google Chrome is a web browser</p>
      <p>Chrome is a web browser developed by google </p>
      <div>
         <div>
            <p>This is a leaf node</p>
         </div>
      </div>
   </span>
</article>
"""

def traverse(t, current_path = None):
    if current_path is None:
        current_path = [t.name]

    for tag in t.find_all(recursive=False):
        if not tag.find():
            print(
                " -> ".join(
                    current_path + [tag.name, tag.find(text=True).strip()]
                )
            )
        else:
            traverse(tag, current_path + [tag.name])
        
soup = BeautifulSoup(html, 'html.parser')
traverse(soup.article)