import requests
from lxml import etree
from multiprocessing.dummy import Pool

class CrlProxyIP:
	"""爬取代理IP"""
	def __init__(self,type='https'):
		if type == 'https':
			self.url = 'http://www.xicidaili.com/wn/'
			self.prefix = 'https'
		elif type == 'http':
			self.url = 'http://www.xicidaili.com/wt/'
			self.prefix = 'http'
			
		self.session = requests.Session()
		self.ips = self.crlips()

	def update(self):
		self.ips.extend(self.crlnext())

	def crlips(self,n=1,proxies=None):
		'''抓取一页的ip,n为第几页'''
		self.curPage = n
		url = self.url + str(n)
		rsp = self.session.get(url,proxies=proxies)
		print(rsp.status_code)
		html = etree.HTML(rsp.text)
		trs = html.xpath('//tr[@class]')
		ips_ports = [(tr.xpath('.//td')[1].text,tr.xpath('.//td')[2].text) for tr in trs if tr.xpath('.//td')[4].text == '高匿']
		pool = Pool(50)
		ips = pool.map(self.verify_ip,ips_ports)
		efc_ips = filter(lambda p:p,ips)#ip can use
		efc_ips = map(lambda ip:{self.prefix:'{}://{}:{}'.format(self.prefix,ip[0],ip[1])},efc_ips)
		return list(efc_ips)
	
	def crlnext(self,proxies=None):
		self.curPage += 1
		return self.crlips(self.curPage,proxies)
		
	def verify_ip(self,ips):
		ip = ips[0]
		port = ips[1]
		return self.verify_ip_port(ip,port)
		
	def verify_ip_port(self,ip,port):
		'''验证ip是否可用'''
		url = 'http://ip.chinaz.com/getip.aspx'
		proxy = {self.prefix:'{}://{}:{}'.format(self.prefix,ip,port)}
		try:
			rsp = self.session.get(url,proxies=proxy,timeout=2)
		except Exception as e:
			#print('此ip {}, port {}不可用'.format(ip,port))#此ip不可用
			return False
		else:
			#print(rsp.text)
			return ip,port
			
if __name__ == '__main__':
	pro_ip = CrlProxyIP('https')
	print(pro_ip.crlips())