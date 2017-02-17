import requests
from lxml import etree
import re

proxy = {'http':'http://175.160.148.243:9999'}


def download(url):
    r = session.get(url)
    html = etree.HTML(r.text)
    divs = html.xpath('//div[@class="comment-item"]')
    for div in divs:
        user_name = div.xpath('.//span[@class="comment-info"]/a/text()')[0]
        user_url = div.xpath('.//span[@class="comment-info"]/a/@href')[0]
        saw = div.xpath('.//span[@class="comment-info"]/child::span[1]/text()')[0]
        rating = div.xpath('.//span[@class="comment-info"]/child::span[2]/@class')[0]
        time = div.xpath('.//span[@class="comment-info"]/child::span[3]/text()')[0].strip()
        content = div.xpath('.//p/text()')[0].strip()
        print(user_name,user_url,saw,rating,time,content)

mvurl = 'https://movie.douban.com/subject/25980443/'
session = requests.Session()
session.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            "Host": "movie.douban.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-CN, zh; q=0.8, en; q=0.6",
        }

r = session.get(mvurl,proxies=proxy)
print(r.status_code)
html = etree.HTML(r.text)

url_href = html.xpath('//div[@id="comments-section"]//span[@class="pl"]/a/@href')[0]
url = '{}&start={}&limit=20&sort=new_score'.format(url_href,2000)
r = session.get(url,auth=('350478064@qq.com','zhou930721'))

print(r.text)

