import requests
from lxml import etree
# from base64 import b64decode
import pandas as pd
import asyncio
import aiohttp
import concurrent.futures
import random
from autoadsl import Adsl
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO,
         format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
         datefmt='[%Y-%m_%d %H:%M:%S]',
         filename='./crlcomments.log',
         filemode='a')
adsl = Adsl()

class CrlComments:
    '''
	可以构建代理ip队列和user-agent队列
	每次访问时随机
    '''
    def __init__(self):
        self.sema = asyncio.Semaphore(15)#限制并发数量
        self.lock = asyncio.Lock()
        self.hds=['Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6',\
			 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11',\
			 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)',\
			 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
			 ]

        #模拟登录
        # login_url = 'https://accounts.douban.com/login'
        # data = {'form_email':b64decode(b''),'form_password':b64decode(b''),\
        # 'source':'movie','login':'登录','redir':'https://movie.douban.com'}
        # r = self.session.post(login_url,data=data)
        # print(r.status_code,'login successfully!')
        # self.session.cookies.update(r.cookies)

    def get_comments(self, url,text):
        html = etree.HTML(text)
        divs = html.xpath('//div[@class="comment-item"]')
        if len(divs) > 1:
            for div in divs:
                user_name = div.xpath('.//span[@class="comment-info"]/a/text()')
                user_name = user_name[0] if user_name else None
                user_url = div.xpath('.//span[@class="comment-info"]/a/@href')[0]
                saw = div.xpath('.//span[@class="comment-info"]/child::span[1]/text()')
                saw = saw[0] if saw else None
                rating = div.xpath('.//span[@class="comment-info"]/child::span[2]/@class')
                rating = rating[0] if rating else None
                time = div.xpath('.//span[@class="comment-info"]/span[@class="comment-time "]/text()')[0].strip()
                content = div.xpath('.//p/text()')[0].strip()
                df = pd.DataFrame([(url,user_name,user_url,saw,rating,time,content)],columns=\
                    ['url','user_name','user_url','saw','rating','time','content'])
                df.to_csv('comments.csv',mode='a',index=False,encoding='utf-8',header=False)

    #不使用aiohttp
    # async def download(self,url,*args,**kwargs):
    #     future = self.loop.run_in_executor(None,partial(self.session.get,url,*args,**kwargs))
    #     response = await future
    #     print(response.status_code,url)
    #     self.get_comments(response)

    async def fetch(self,session,url):
        with await self.sema:
            try:
                async with session.get(url,allow_redirects=False) as response:
                    if response.status == 200:
                        text = await response.text()
                        if len(text) < 500:
                            raise Exception
                        self.get_comments(url,text)
                        with await self.lock:
                            self.urls.remove(url)
                        #response.status = 403
                    elif response.status == 404:#页面不存在
                        with await self.lock: 
                            self.urls.remove(url)
                        logging.warning('status:{},url:{}'.format(response.status,url))
                        # for task in asyncio.Task.all_tasks():
                        #     task.cancel()
                    else:#ip被封，403,302错误
                        for task in asyncio.Task.all_tasks():
                            task.cancel()
                        logging.warning('status:{},url:{}'.format(response.status,url))
            except Exception as e:#clientresponse错误
                for task in asyncio.Task.all_tasks():
                    task.cancel()
                    # asyncio.Task.current_task().cancel()
                logging.error('error:{}'.format(e))
                    

    async def download(self,loop,urls):
        async with aiohttp.ClientSession(loop=loop) as session:
            session.headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-CN, zh; q=0.8, en; q=0.6",
            }
            tasks = []
            session.headers['User-Agent'] = self.hds[random.randint(0,3)]
            for url in urls:
                #随机User-agent,代理ip
                tasks.append(asyncio.ensure_future(self.fetch(session,url)))
            try:
                await asyncio.wait(tasks)
            except concurrent.futures._base.CancelledError:#cancel task会报这个错误
                pass



    def crawls(self):
        #大文件分块读取，用于内存不够用的情况
        # num_line = 1000#要读取的行数
        # reader = pd.read_csv('moviedata.csv', iterator=True)
        # loop = True
        # while loop:
        #     try:
        #         df = reader.get_chunk(1000)
        #         print(len(df))
        #         #dosomething()
        #     except StopIteration:
        #         loop = False
        #         print("Iteration is stopped.")

        df = pd.read_csv('moviedata.csv')
        df_urls = df['url'].apply(lambda url:url+'comments')[:1000]
        self.urls = []
        for url in df_urls:
            tmp = [url+'?start={}&limit=20&sort=new_score&status=P'.format(i*20) for i in range(10)]
            self.urls.extend(tmp)
        print(len(self.urls))
        loop = asyncio.get_event_loop()
        # executor = concurrent.futures.ThreadPoolExecutor(5)
        # loop.set_default_executor(executor)
        loop.run_until_complete(self.download(loop,self.urls))

        while self.urls:
            print(len(self.urls))
            print('失败重新爬取。。。')
            adsl.reconnect()
            loop.run_until_complete(self.download(loop,self.urls))

        # executor.shutdown(wait=True)
        loop.close()
        print('loop is closed')


if __name__ == '__main__':
    cc = CrlComments()
    cc.crawls()


