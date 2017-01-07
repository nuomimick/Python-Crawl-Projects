import requests
from lxml import etree
from multiprocessing.dummy import Pool
from pymongo import MongoClient
import re




class CrlMovieUrls():
	"""爬取豆瓣电影"""
	def __init__(self, tags):
		client = MongoClient('localhost',27017)#链接
		dbname = 'test'
		db = client[dbname]#选择数据库
		clctname = 'mvdata'
		self.collection = db[clctname]#选择集合

		burl = 'https://movie.douban.com/tag/电影%20'
		self.tagurls = map(lambda p:burl+p,tags)

	def getPageNum(self,tagurl):
		'''获取总页数'''
		rsp = requests.get(tagurl)
		html = etree.HTML(rsp.text)
		pn = html.xpath('//span[@class="thispage"]/@data-total-page')[0]#总页数
		return int(pn)

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
		pool = Pool(10)
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

	def contentOfMovie(self,dct):
		url = dct['href']
		title = dct['title']
		rsp = requests.get(url)
		html = etree.HTML(rsp.text)
		ele_div = html.xpath('//div[@id="info"]')[0]#电影信息div
		str_html = etree.tostring(ele_div,encoding='utf-8').decode()#转成字符串
		director = '/'.join(ele_div.xpath('.//span[text() = "导演"]/following-sibling::*[1]/a/text()'))#导演
		scenarist = '/'.join(ele_div.xpath('.//span[text() = "编剧"]/following-sibling::*[1]/a/text()'))#编剧
		actor = '/'.join(ele_div.xpath('.//span[text() = "主演"]/following-sibling::*[1]/a/text()'))#主演
		tp = '/'.join(ele_div.xpath('.//span[@property = "v:genre"]/text()'))#类型
		state = re.compile(r'制片国家/地区:</span> (.*?)<br/>').search(str_html).group(1)#地区
		language = re.compile(r'语言:</span> (.*?)<br/>').search(str_html).group(1)#语言
		time = '/'.join(ele_div.xpath('.//span[@property="v:initialReleaseDate"]/text()'))#上映时间
		runtime = ele_div.xpath('.//span[@property="v:runtime"]/text()')[0]#片长
		name = re.compile(r'又名:</span> (.*?)<br/>').search(str_html).group(1)#又名
		link = ele_div.xpath('.//span[text()="IMDb链接:"]/following-sibling::*[1]/@href')[0]#IMDb链接
		related_info = '/'.join(map(lambda s:s.strip(),html.xpath('//div[@class="related-info"]//span[@property="v:summary"]/text()')))#剧情简介

		dc = dict(zip(('director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info'),
			(director,scenarist,actor,tp,state,language,time,runtime,name,link,related_info)))
		
		self.collection.update_one({'title':title,'href':url},{'$set':dc})
		# print(director)
		# print(scenarist)
		# print(actor)
		# print(tp)
		# print(state)
		# print(language)
		# print(time)
		# print(runtime)
		# print(name)
		# print(link)
		# print(related_info)

	def contentOfAllMovies(self):
		pool = Pool(10)
		pool.map(self.contentOfMovie,self.collection.find())

if __name__ == '__main__':
	cmu = CrlMovieUrls(['2015','2014','2013'])
	cmu.urlsOfAllTags()
	cm = CrlMovie()
	cm.contentOfAllMovies()
	

	
		
