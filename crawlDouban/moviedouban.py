import requests
from lxml import etree
from multiprocessing.dummy import Pool
from pymongo import MongoClient
import re
import pandas as pd
import proxyip


class CrlMovieUrls():
	"""爬取豆瓣电影"""
	def __init__(self, tags):
		client = MongoClient('localhost',27017)#链接
		dbname = 'test'
		db = client[dbname]#选择数据库
		clctname = 'mvdata'
		self.collection = db[clctname]#选择集合

		burl = 'https://movie.douban.com/tag/'
		self.tagurls = map(lambda p:burl+p,tags)

	def getPageNum(self,tagurl):
		'''获取总页数'''
		rsp = requests.get(tagurl)
		html = etree.HTML(rsp.text) 
		pn = html.xpath('//span[@class="thispage"]/@data-total-page')#总页数
		print(pn)
		return int(pn[0])

	def urlsOfOnePage(self,start,type='T'):
		'''
		爬取一页的链接、片名
		start=0是第一页，之后每页加20
		'''
		url = self.url + '?start={}&type={}'.format(start*20,type)
		rsp = requests.get(url)
		html = etree.HTML(rsp.text)
		trs = html.xpath('//tr[@class="item"]//a[@class="nbg"]')
		for tr in trs:
			href = tr.xpath('./@href')[0]
			title = tr.xpath('./@title')[0]
			self.collection.insert_one({'title':title,'href':href})

	def urlsOfAllPages(self,tagurl):
		'''全部页数的链接'''
		pn = self.getPageNum(tagurl)
		self.url = tagurl
		pool = Pool(20)
		pool.map(self.urlsOfOnePage,range(pn))

	def urlsOfAllTags(self):
		'''全部标签的链接'''
		for tagurl in self.tagurls:
			self.urlsOfAllPages(tagurl)


class CrlMovie():
	'''抓取电影内容'''
	def __init__(self):
		client = MongoClient('localhost',27017)#链接
		dbname = 'test'
		db = client[dbname]#选择数据库
		clctname = 'mvdata'
		self.collection = db[clctname]#选择集合

		self.session = requests.Session()
		
		pxy_ip = CrlProxyIP()
		self.proxies = pxy_ip.crlips()
		self.proxy = self.proxies.pop()


	def contentOfMovie(self,dct):
		'''抓页面内容'''
		url = dct['href']
		rsp = self.session.get(url,proxies=self.proxy)
		while rsp.status_code == 403:
			if self.proxies:
				self.proxy = self.proxies.pop()
				rsp = self.session.get(url,proxies=self.proxy_ip)
			else:
				self.proxies = pxy_ip.crlnext()
		html = etree.HTML(rsp.text)
		ele_div = html.xpath('//div[@id="info"]')[0]#电影信息div
		str_html = etree.tostring(ele_div,encoding='utf-8').decode()#转成字符串
		title = ele_div.xpath('//span[@property = "v:itemreviewed"]/text()')[0]#更新title
		year = ele_div.xpath('//span[@class="year"]/text()')[0]
		director = '/'.join(ele_div.xpath('.//span[text() = "导演"]/following-sibling::*[1]/a/text()'))#导演
		scenarist = '/'.join(ele_div.xpath('.//span[text() = "编剧"]/following-sibling::*[1]/a/text()'))#编剧
		actor = '/'.join(ele_div.xpath('.//span[text() = "主演"]/following-sibling::*[1]/a/text()'))#主演
		tp = '/'.join(ele_div.xpath('.//span[@property = "v:genre"]/text()'))#类型
		state = re.compile(r'制片国家/地区:</span> (.*?)<br/>').search(str_html).group(1)#地区
		time = '/'.join(ele_div.xpath('.//span[@property="v:initialReleaseDate"]/text()'))#上映时间
		try:
			language = re.compile(r'语言:</span> (.*?)<br/>').search(str_html).group(1)#语言
		except AttributeError:
			language = None
		try:
			runtime = ele_div.xpath('.//span[@property="v:runtime"]/text()')[0]#片长
		except IndexError:
			runtime = None
		try:
			name = re.compile(r'又名:</span> (.*?)<br/>').search(str_html).group(1)#又名
		except AttributeError:
			name = None
		try:
			link = ele_div.xpath('.//span[text()="IMDb链接:"]/following-sibling::*[1]/@href')[0]#IMDb链接
		except IndexError:
			link = None
		related_info = '/'.join(map(lambda s:s.strip(),html.xpath('//div[@class="related-info"]//span[@property="v:summary"]/text()')))#剧情简介

		dc = dict(zip(('title','year','director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info'),
			(title,year,director,scenarist,actor,tp,state,language,time,runtime,name,link,related_info)))
		
		self.collection.update_one({'title':title,'href':url},{'$set':dc})

	def contentOfAllMovies(self):
		pool = Pool(50)
		pool.map(self.contentOfMovie,self.collection.find())

if __name__ == '__main__':
	# cmu = CrlMovieUrls(['2016','2015','2014'])
	# cmu.urlsOfAllTags()
	# cm = CrlMovie()
	# cm.contentOfAllMovies()
	cip = CrlProxyIP()
	cip.crlips()


	
		
