'''
created by:zrh
time:2016.12.24
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
        r = html.xpath('//h1[@class="core_title_txt  "]')
        return r[0].text

    def __crawl(self,url):
        rsp = requests.get(url)
        return rsp

    def __num_reply_page(self,url):
        #返回回复数和页数
        rsp = self.__crawl(url)
        html = etree.HTML(rsp.text)
        r = html.xpath('//li/span[@class="red"]/text()')[:2]
        return int(r[0]),int(r[1])

    def __userList(self,text):
        #获取楼层用户列表
        pattern = re.compile(r'"userList".*?({.*}).*"commentList"')
        r = re.search(pattern,text)
        user_dict = json.loads(r.group(1))
        return user_dict

    def __commentList(self,text):
        #获取楼层回复列表
        pattern = re.compile(r'"commentList".*?({.*}).*"isAdThread"')
        r = re.search(pattern,text)
        comment_dict = json.loads(r.group(1))
        return comment_dict

    def __content(self,response):
        '''
        获取一个帖子的内容
        response:response对象
        '''
        text = response.text
        html = etree.HTML(text)
        results = html.xpath('//div[@class="l_post j_l_post l_post_bright noborder "] \
        | //div[@class="l_post j_l_post l_post_bright  "]')
        commentList = self.__commentList(text)
        userList = self.__userList(text)
        file = open('crltext.txt','a',encoding='utf-8')
        file.write('标题 '+self.__title(html)+'\n')
        for i in range(len(results)):
            ele = results[i].xpath('.//div[@class="d_post_content j_d_post_content  clearfix"]')[0]
            txt = ele.xpath('./node()')
            id = ele.xpath('./@id')[0][13:]#段落id，用于楼层回复
            txt = "".join(map(lambda p:'[表情]' if not isinstance(p,str) else p,txt)).strip()#层主回复
            rn = json.loads(results[i].xpath('.//li[@class="d_name"]/@data-field')[0])#层主id
            uname = userList[str(rn['user_id'])]['user_name']#层主名字
            ctxt = "{}:{}".format(uname,txt)
            file.write(ctxt+'\n')
            #print(ctxt)#输出楼层内容
            cli = commentList[id]
            #输出楼层回复
            for ct in cli:
                cname = userList[ct['user_id']]['user_name']
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
        self.__content(self.__crawl(url))

    def contentOfPosts(self,urls):
        #全部帖子的内容
        pool = Pool(10)
        reqList = list(pool.map(self.__crawl,urls))
        for req in reqList:
            self.__content(req)

    def urlsOfPage(self,kw,pn):
        '''
        爬取单页,pn是页数(0到end-1)
        kw:贴吧的名字
        pn:页数，第一页为0，第二页为1
        '''
        baseurl = 'http://tieba.baidu.com/f?ie=utf-8'
        url = baseurl+'&kw='+kw+'&pn='+str(pn*50)
        req = self.__crawl(url)
        html = etree.HTML(req.text)
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
    res = cr.urlsOfPages('西南交通大学',1)
    cr.contentOfPosts(res)