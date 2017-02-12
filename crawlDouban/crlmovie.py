import requests
from lxml import etree
import re
import threading
import time

SLEEP_TIME = 1

class crawlMovies():
	def __init__(self):
		pass

	def crawler(self,seed_url,link_regex,max_threads=10):
		crawl_queue = [seed_url]
		seen = set(crawl_queue) 
		threads = []
		while threads or crawl_queue:#如果线程池不为空或者队列不为空(说明还有任务没有执行完)
			for thd in threads:
				if not thd.isAlive():
					threads.remove(thd)
			if len(threads) < max_threads and crawl_queue:#任务列表不为空且线程数小于最大线程数，新建线程
				thread = threading.Thread(target=self.process_url,args=(crawl_queue,seen,link_regex))
				thread.setDaemon(True)
				thread.start()
				threads.append(thread)
			#等待(线程池满了或者任务队列为空)
			time.sleep(SLEEP_TIME)
			
	def process_url(self,crawl_queue,seen,link_regex):
		url = crawl_queue.pop()
		html = self.download(url)
		self.crl_content(html)
		for link in self.get_links(html):
			if re.match(link_regex,link):
				if link not in seen:
					seen.add(link)
					crawl_queue.append(link)

	def download(self,url,timeout=3):
		rsp = requests.get(url,timeout=timeout)
		html = etree.HTML(rsp.text)
		return html

	def crl_content(self,html):
		title = html.xpath('//span[@property="v:itemreviewed"]/text()')[0]
		year = html.xpath('//span[@class="year"]/text()')[0]
		with open('data.dat','a',encoding='utf-8') as f:
			f.write('{} {}\n'.format(title,year))

	def get_links(self,html):
		rst = html.xpath('//a/@href')
		return set(rst)

if __name__ == '__main__':
	seed_url = 'https://movie.douban.com/subject/26635319/'
	pattern = re.compile(r'https://movie.douban.com/subject/\d+/\?from.*')
	cm = crawlMovies()
	cm.crawler(seed_url,pattern)
