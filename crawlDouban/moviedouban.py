import requests
from lxml import etree
from multiprocessing.dummy import Pool
from pymongo import MongoClient
import re
import pandas as pd
from proxyip import CrlProxyIP

def get_mongo_collection(ip,port,dbname,collection):
	client = MongoClient(ip,port)#链接
	db = client[dbname]#选择数据库
	clct = db[collection]#选择集合
	return clct

def df_to_mongo(dataframe):
	records = dataframe.to_dict('records')
	clct = get_mongo_collection('localhost',27017,'test','mvdata')
	clct.insert_many(records)

class CrlMovieUrls():
	"""
	爬取豆瓣电影
	return DataFrame	
	"""
	def __init__(self, tags):
		burl = 'https://movie.douban.com/tag/'
		self.tagurls = map(lambda p:burl+p,tags)
		

	def getPageNum(self,tagurl):
		'''获取总页数'''
		rsp = requests.get(tagurl)
		html = etree.HTML(rsp.text) 
		pn = html.xpath('//span[@class="thispage"]/@data-total-page')#总页数
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
		data = [(tr.xpath('./@href')[0], tr.xpath('./@title')[0]) for tr in trs]
		return pd.DataFrame(data,columns=['url','title'])

	def urlsOfAllPages(self,tagurl):
		'''全部页数的链接'''
		pn = self.getPageNum(tagurl)
		self.url = tagurl
		pool = Pool(20)
		df_list = pool.map(self.urlsOfOnePage,range(pn))
		return pd.concat(df_list,ignore_index=True)

	def urlsOfAllTags(self):
		'''全部标签的链接'''
		df = pd.DataFrame({})
		for tagurl in self.tagurls:
			df = df.append(self.urlsOfAllPages(tagurl),ignore_index=True)
		return df
		

class CrlMovie():
	'''抓取电影内容'''
	def __init__(self):
		self.session = requests.Session()
		self.session.headers = {
            "User-Agent": 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            "Host": "movie.douban.com",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch, br",
            "Accept-Language": "zh-CN, zh; q=0.8, en; q=0.6",
        }

		self.pxy_ip = CrlProxyIP()
		self.proxies = self.pxy_ip.crlips()
		proxy = self.proxies.pop()
		self.proxy = {'https':'http://{}:{}'.format(proxy[0],proxy[1])}
		print('finish crawl proxy ip')


	def contentOfMovie(self,item):
		'''抓页面内容'''
		url = item[1]
		print(self.proxy)
		try:
			rsp = self.session.get(url,proxies=self.proxy)
			while rsp.status_code == 403:
				if self.proxies:
					proxy = self.proxies.pop()
					self.proxy = {'https':'http://{}:{}'.format(proxy[0],proxy[1])}
					rsp = self.session.get(url,proxies=self.proxy)
				else:
					self.proxies = self.pxy_ip.crlnext()
		except Exception:
			proxy = self.proxies.pop()
			self.proxy = {'https':'http://{}:{}'.format(proxy[0],proxy[1])}
			rsp = self.session.get(url,proxies=self.proxy)
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

		# dc = dict(zip(('title','year','director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info'),
		# 	(title,year,director,scenarist,actor,tp,state,language,time,runtime,name,link,related_info)))
	
		df = pd.DataFrame([(title,year,director,scenarist,actor,tp,state,language,time,runtime,name,link,related_info)],columns=
			['title','year','director','scenarist','actor','tp','state','language','time','runtime','name','link','related_info'])
		print(df)
		input()
		

	def contentOfAllMovies(self,dataframe):
		pool = Pool(1)
		pool.map(self.contentOfMovie,dataframe.itertuples())

if __name__ == '__main__':
	# cmu = CrlMovieUrls(['2016','2015','2014'])
	# cmu.urlsOfAllTags().to_csv('urldata.csv',index=False,encoding='utf-8')

	# df = pd.read_csv('urldata.csv')
	# cm = CrlMovie()
	# cm.contentOfAllMovies(df)
	
	# pxy_ip = CrlProxyIP(type='https')
	# proxies = pxy_ip.crlips()
	# pd.DataFrame(proxies,columns=['ip','port']).to_csv('ips.csv')
	
	s = requests.Session()
	proxy = {'https':'http://{}:{}'.format('202.111.175.97','8080')}
	
	rsp = s.get('http://www.baidu.com',proxies=proxy)
	print(rsp.status_code)
	
	rsp = s.get('https://movie.douban.com/',proxies=proxy)
	print(rsp.status_code)
	



	
		
