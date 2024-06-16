import os
from time import sleep

import scrapy
from bs4 import BeautifulSoup

init_url = "https://mirrors.tuna.tsinghua.edu.cn/"


class MirrorLink:
    def __init__(self, href, name):
        self.href = href
        self.name = name

    def __repr__(self):
        return f"{init_url+self.href}"


class TunaSpider(scrapy.Spider):
    name = "tuna"
    allowed_domains = ["mirrors.tuna.tsinghua.edu.cn"]
    start_urls = ["https://mirrors.tuna.tsinghua.edu.cn/help/AOSP/"]

    def start_requests(self):
        if not os.path.exists("./content/mirror_links.txt"):
            yield scrapy.Request(
                "https://mirrors.tuna.tsinghua.edu.cn/help/AOSP/", callback=self.parse
            )
        else:
            with open("./content/mirror_links.txt", "r", encoding="utf-8") as f:
                for line in f:
                    yield scrapy.Request(url=line, callback=self.content_parse)

    def content_parse(self, response):
        print("Here is the content we got")
        content = response.css("#help-content").get()
        soup = BeautifulSoup(content, "lxml")
        text = soup.get_text(separator="\n", strip=True)
        print(text)

        url_parts = response.url.rstrip("/").split("/")
        filename = url_parts[-1] + ".txt"

        if not os.path.exists("./content"):
            os.makedirs("./content")

        with open(os.path.join("./content", filename), "w", encoding="utf-8") as f:
            f.write(text)

    def parse(self, response):
        help_nav_html = response.css("#help-nav").get()

        soup = BeautifulSoup(help_nav_html, "lxml")
        help_nav = soup.find("ul", {"id": "help-nav"})

        mirror_links = []
        for li in help_nav.find_all("li", class_="nav-item"):
            a = li.find("a", class_="nav-link")
            href = a["href"]
            name = a.text.strip()
            mirror_links.append(MirrorLink(href, name))

        if not os.path.exists("./content"):
            os.makedirs("./content")

        with open("./content/mirror_links.txt", "w", encoding="utf-8") as f:
            for link in mirror_links:
                f.write(f"{link}\n")

        for lin in mirror_links:
            sleep(2)
            yield scrapy.Request(init_url + lin.href, self.content_parse)
