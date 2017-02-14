import requests
from lxml import etree
from multiprocessing.dummy import Pool
import pandas as pd

class CrlProxyIP:
	"""爬取代理IP"""
	def __init__(self):
		self.url = 'http://www.xicidaili.com/nn'#某代理ip网址
		self.session = requests.Session()

	def crlips(self,n=1):
		'''抓取一页的ip,n为第几页'''
		headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
		url = self.url + '/' + str(n)
		rsp = self.session.get(url,headers=headers)
		html = etree.HTML(rsp.text)
		trs = html.xpath('//tr[@class]')
		ips_ports = [(tr.xpath('.//td')[1].text,tr.xpath('.//td')[2].text) for tr in trs]
		pool = Pool(50)
		ips = pool.map(self.verify_ip,ips_ports)
		efc_ips = filter(lambda p:p,ips)#ip can use
		return efc_ips
			
	def verify_ip(self,ips):
		ip = ips[0]
		port = ips[1]
		return self.verify_ip_port(ip,port)
		
	def verify_ip_port(self,ip,port):
		'''验证ip是否可用'''
		url = 'http://ip.chinaz.com/getip.aspx'
		proxy = {'http':'http://{}:{}'.format(ip,port)}
		try:
			rsp = self.session.get(url,proxies=proxy,timeout=2)
		except Exception as e:
			print('此ip {}, port {}不可用'.format(ip,port))#此ip不可用
			return False
		else:
			return ip,port
			
if __name__ == '__main__':
	pro_ip = CrlProxyIP()
	pro_ip.crlips()