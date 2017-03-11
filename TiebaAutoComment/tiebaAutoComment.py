from PyQt5 import QtGui, QtCore, QtNetwork,QtWidgets,QtWebKitWidgets,QtWebKit
import requests,re,json
from lxml import etree
import time

def download(webview,url):
	loop = QtCore.QEventLoop()
	webview.loadFinished.connect(loop.quit)
	req = QtNetwork.QNetworkRequest(QtCore.QUrl(url))
	webview.load(req)
	loop.exec_()

app = QtWidgets.QApplication([])
webview = QtWebKitWidgets.QWebView()
webview.show()
download(webview,'https://passport.baidu.com/v2/?login')
frame = webview.page().mainFrame()
# frame.findFirstElement('#TANGRAM__PSP_3__userName').setAttribute('value','')
# frame.findFirstElement('#TANGRAM__PSP_3__password').setAttribute('value','')
# frame.findFirstElement('#TANGRAM__PSP_3__submit').evaluateJavaScript("this.click()")
#等待结果
elements = QtWebKit.QWebElement()
while elements.isNull():
    #每次循环，都会调用app.processEvents(),用于给Qt事件循环执行任务的时间，比如响应点击事件和更新GUI
	app.processEvents()
	elements = frame.findFirstElement('#displayUsername')

s_cookies = {}
for citem in webview.page().networkAccessManager().cookieJar().cookiesForUrl(QtCore.QUrl('http://www.baidu.com')):
    s_cookies[bytes(citem.name()).decode()] = bytes(citem.value()).decode()
# cookiejar = webview.page().networkAccessManager().cookieJar()
# for ck in cookiejar.allCookies():
#     s_cookies[bytes(ck.name()).decode()] = bytes(ck.value()).decode()
webview.close()
download(webview,'http://tieba.baidu.com/')
for citem in webview.page().networkAccessManager().cookieJar().cookiesForUrl(QtCore.QUrl('http://tieba.baidu.com/')):
    s_cookies[bytes(citem.name()).decode()] = bytes(citem.value()).decode()

s = requests.Session()
s.headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36',
        }
s.cookies.update(s_cookies)

while True:
    url = 'http://tieba.baidu.com/p/5016192642'
    r = s.get(url)
    html = etree.HTML(r.text)
    data_field = json.loads(html.xpath('//*[@id="j_p_postlist"]/div[3]/@data-field')[0])

    kw = html.xpath('//*[@id="container"]/div/div[1]/div[2]/div[2]/a[1]/@title')[0]
    fid = re.compile("fid:'(.*?)'").search(r.text).group(1)
    tid = url[-10:]
    quote_id = str(data_field['content']['post_id'])
    tbs = re.compile('tbs.*?:."(.*?)"').search(r.text).group(1)
    repostid = quote_id

    url_add = 'http://tieba.baidu.com/f/commit/post/add'
    add_data = {
        'ie':'utf-8',
        'kw':kw,
        'fid':fid,
        'tid':tid,
        'floor_num':'2',
        'quote_id':quote_id,
        'rich_text':'1',
        'tbs':tbs,
        'content':'test',
        'lp_type':'0',
        'lp_sub_type':'0',
        'new_vcode':'1',
        'repostid':repostid,
        'anonymous':'0'
    }
    rsp = s.post(url_add,data=add_data)
    if rsp.status_code == 200:
        print('add comment successful!'.center(40,'#'))
    else:
        print('add comment failed'.center(40,'#'))

    time.sleep(3)

    r = s.get(url)
    html = etree.HTML(r.text)
    tbs = re.compile('tbs.*?:."(.*?)"').search(r.text).group(1)
    user_id = re.compile('"user_id":.*?(.*?),').search(r.text).group(1)

    comment_url = 'http://tieba.baidu.com/p/totalComment?tid={}&fid={}'.format(tid,fid)
    text = s.get(comment_url).text
    comments = json.loads(text)['data']['comment_list']
    comment_id = None
    user_name = None
    for cmt in comments[quote_id]['comment_info']:
        if user_id in cmt.values():
            comment_id = cmt['comment_id']
            user_name = cmt['username']

    delete_url = 'http://tieba.baidu.com/f/commit/post/delete'
    delete_data = {
        'ie':'utf-8',
        'tbs':tbs,
        'kw':kw,
        'fid':fid,
        'tid':tid,
        'user_name':user_name,
        'delete_my_post':'1',
        'delete_my_thread':'0',
        'is_vipdel':'0',
        'pid':comment_id,
        'is_finf':'1'
    }
    rsp = s.post(delete_url,delete_data)
    if rsp.status_code == 200:
        print('delete comment successful!'.center(40,'#'))
    else:
        print('delete comment failed'.center(40,'#'))

    time.sleep(3600)#循环时间


