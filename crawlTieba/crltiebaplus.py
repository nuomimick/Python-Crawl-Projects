'''
created by:zrh
time:
description:由于一些贴吧在网页源代码中找不到userList和commentList，
url=http://tieba.baidu.com/p/totalComment?tid=4895246822&fid=58081&pn=1&see_lz=0
访问url可以获取user_list和comment_list,还有其它信息
'''
import re
import json
import requests
from lxml import etree
from multiprocessing.dummy import Pool

class crltieba():

    def __init__(self):
    	#测试用，将存在的文件删除
        import os
        if os.path.exists('crltieba.txt'):
            os.remove('crltieba.txt')

    def __title(self,html):
    	#帖子标题
        r = html.xpath('//title')
        return r[0].text

    def __crawl(self,url):
        rsp = requests.get(url)
        html = etree.HTML(rsp.text)
        pattern = re.compile(r'data : ({.*?})')
        dt1 = re.search(pattern,rsp.text).group(1)
        dt2 = re.compile(r"fid:'(.*?)'.*tid:'(.*?)'").search(dt1)
        fid = dt2.group(1)
        tid = dt2.group(2)
        url = 'http://tieba.baidu.com/p/totalComment?tid={}&fid={}'.format(tid,fid)
        text = requests.get(url).text
        return html, text

    def __crawlUrls(self,url):
        rsp = requests.get(url)
        html = etree.HTML(rsp.text)
        return html

    def __num_reply_page(self,url):
    	#返回回复数和页数
        html = self.__crawlUrls(url)
        r = html.xpath('//li/span[@class="red"]/text()')[:2]
        return int(r[0]),int(r[1])

    def __list_comment(self,text):
        rst = json.loads(text)['data']
        return rst['comment_list']

    def __content(self,html,text):
        '''
        获取一个帖子的内容
        response:response对象
        '''
        results = html.xpath('//div[@class="p_postlist"]/div[@data-field]')
        commentList = self.__list_comment(text)
        file = open('crltext.txt','a',encoding='utf-8')
        file.write('标题 '+self.__title(html)+'\n')
        for i in range(len(results)):
            ele = results[i].xpath('./@data-field')[0]
            json_dict = json.loads(ele)['author']
            user_id = json_dict['user_id']#层主id
            user_name = json_dict['user_name']
            #contains匹配含有post_content的字段
            pc_ele = results[i].xpath('.//div[contains(@id,"post_content")]')[0]
            pc_id = pc_ele.xpath('./@id')[0][13:]#楼层id
            txt = pc_ele.xpath('./node()')
            txt = "".join(map(lambda p:'[表情]' if not isinstance(p,str) else p,txt)).strip()#层主回复
            ctxt = "{}:{}".format(user_name,txt)
            file.write(ctxt+'\n')
            #print(ctxt)#输出楼层内容
            if pc_id in commentList:
                cli = commentList[pc_id]['comment_info']
                #输出楼层回复
                for ct in cli:
                    cname = ct['username']#回复的用户名字
                    retxt = re.sub(r'<img.*?>',"[表情]",ct['content'])
                    retxt = re.sub(r'<.*?>',"",retxt)
                    retxt = "   {} {}".format(cname,retxt)
                    file.write(retxt+'\n')
                    #print(retxt)
        file.close()

    def contentOfOnePost(self,url,see_lz=0):
    	#一个帖子的内容
        u = url + '?see_lz={}'.format(see_lz)
        pn = self.__num_reply_page(u)[1]
        for i in range(1,pn+1):
            self.contentOfOnePage(url,i,see_lz)

    def contentOfOnePage(self,url,pn,see_lz=0):
    	#一页的内容
        url += '?pn={}&see_lz={}'.format(pn,see_lz)
        html, text = self.__crawl(url)
        self.__content(html, text)

    def contentOfPosts(self,urls):
    	#全部帖子的内容
        pool = Pool(10)
        reqList = list(pool.map(self.__crawl,urls))
        for html, text in reqList:
            self.__content(html,text)

    def urlsOfPage(self,kw,pn):
        '''
        爬取单页,pn是页数(0到end-1)
        kw:贴吧的名字
        pn:页数，第一页为0，第二页为1
        '''
        baseurl = 'http://tieba.baidu.com/f?ie=utf-8'
        url = baseurl+'&kw='+kw+'&pn='+str(pn*50)
        html = self.__crawlUrls(url)
        rsts = html.xpath('//li[@class=" j_thread_list thread_top j_thread_list clearfix"]/@data-field | \
                    //li[@class=" j_thread_list clearfix"]/@data-field')
        urls = []
        for rst in rsts:
           urls.append('http://tieba.baidu.com/p/{}'.format(json.loads(rst)['id']))
        return urls

    
    def urlsOfPages(self,kw,pn,begin=0):
    	#爬取范围页数，默认为1-pn页
        urls = []
        for i in range(pn-begin):
             urls.extend(self.urlsOfPage(kw,i))
        return urls


if __name__ == '__main__':
    cr = crltieba()
    res = cr.urlsOfPages('裁决之地',1)
    cr.contentOfPosts(res)