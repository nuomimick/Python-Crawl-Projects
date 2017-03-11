import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import *
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtNetwork import QNetworkRequest 
from PyQt5.QtWebKit import QWebElement

class MWindow(QMainWindow):     
    def __init__(self):
        super().__init__()     
        self.__initUI()
         
    def __initUI(self):  
        act_login = QAction(QIcon(''), '&登录', self) #动作              
        act_login.setShortcut('Ctrl+w')#快捷键
        act_login.setStatusTip('登录')#状态栏
        act_login.triggered.connect(self.__comment)#信号绑定槽

        act_comment = QAction(QIcon(''), '&评论', self)               
        act_comment.setShortcut('Ctrl+w')
        act_comment.setStatusTip('评论')
        act_comment.triggered.connect(self.__comment)

        act_dt = QAction(QIcon(''), '&顶贴', self)               
        act_dt.setShortcut('Ctrl+e')
        act_dt.setStatusTip('顶贴')
        act_dt.triggered.connect(self.__comment)
        
        self.statusBar()#激活状态栏
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(act_login)
        fileMenu.addAction(act_comment)
        fileMenu.addAction(act_dt)
        
        #居中
        self.resize(600,400)
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setWindowTitle('百度贴吧顶贴软件')  
        self.show()

    def __download(self,webview,url):
        loop = QEventLoop()
        webview.loadFinished.connect(loop.quit)
        req = QNetworkRequest(QUrl(url))
        webview.load(req)
        loop.exec_()

    def __comment(self):
        sender = self.sender()
        #print(self.layout)#有layout
        wd = QWidget()
        self.setCentralWidget(wd)#设置widget
        if sender.text() == '&登录':
            self.showMaximized()
            webview = QWebView()
            hbox = QHBoxLayout()
            hbox.addWidget(webview)
            vbox = QVBoxLayout()
            vbox.addLayout(hbox)
            wd.setLayout(vbox)
            self.__download(webview,'https://passport.baidu.com/v2/?login') 
            #wd.deleteLater()#wd.setParent(None)#删除widget
            wd = QWidget()
            self.setCentralWidget(wd)#直接覆盖
            lb = QLabel("正在跳转",wd)

        elif sender.text() == '&评论':
            self.resize(600,400)
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
            #self.setFixedSize(self.size())
            grid = QGridLayout()
            grid.setColumnMinimumWidth(2,350)#第3列最小宽度
            lb_url = QLabel('帖子网址:')
            grid.addWidget(lb_url,0,0,1,1,Qt.AlignRight)

            le = QLineEdit()
            grid.addWidget(le,0,1,1,2)

            lb_floor = QLabel('楼层:')
            le_floor = QLineEdit('')
            grid.addWidget(lb_floor,0,3,1,1,Qt.AlignRight)
            grid.addWidget(le_floor,0,4,1,1)

            lb_cnt = QLabel('评论内容:')
            grid.addWidget(lb_cnt,1,0,1,1,Qt.AlignRight)

            te = QTextEdit()
            grid.addWidget(te,1,1,1,4)

            lb_record = QLabel('评论记录:')
            te_record = QTextEdit()
            grid.addWidget(lb_record,2,0,1,1,Qt.AlignRight)
            grid.addWidget(te_record,2,1,1,4)

            btn = QPushButton('评论', self)
            btn.setToolTip('点击评论')
            grid.addWidget(btn,3,3,1,1)
            btn.clicked.connect(self.__send)
            wd.setLayout(grid)
        elif sender.text() == '&顶贴':
            self.resize(600,400)
            qr = self.frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            qr.moveCenter(cp)
            self.move(qr.topLeft())
            #self.setFixedSize(self.size())
            grid = QGridLayout()
            lb_url = QLabel('帖子网址:')
            grid.addWidget(lb_url,0,0,1,1,Qt.AlignRight)

            le = QLineEdit('')
            grid.addWidget(le,0,1,1,4)

            lb_cnt = QLabel('默认内容:')
            grid.addWidget(lb_cnt,1,0,1,1,Qt.AlignRight)

            te = QLineEdit('hello world!')
            grid.addWidget(te,1,1,1,4)

            lb_time = QLabel('时间(h):')
            grid.addWidget(lb_time,2,0,1,1,Qt.AlignRight)

            te_time = QLineEdit('1')
            grid.addWidget(te_time,2,1,1,4)

            lb_record = QLabel('评论记录:')
            te_record = QTextEdit()
            grid.addWidget(lb_record,3,0,1,1,Qt.AlignRight)
            grid.addWidget(te_record,3,1,1,4)

            btn = QPushButton('顶贴', self)
            btn.setToolTip('开始顶贴')
            grid.addWidget(btn,4,2,1,1)
            btn.clicked.connect(self.__dingt)
            wd.setLayout(grid)
        
    def __send(self):
        wgt = self.centralWidget()
        layout = wgt.layout()
        url = layout.itemAt(1).widget().text()
        floor = layout.itemAt(3).widget().text()
        content = layout.itemAt(5).widget().toPlainText()
       
    def __dingt(self):
        pass
         
if __name__ == '__main__':
    app = QApplication(sys.argv)
    mn = MWindow()
    sys.exit(app.exec_())