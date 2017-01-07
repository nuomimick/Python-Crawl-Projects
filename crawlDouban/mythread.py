'''
description：获取线程返回值
在run函数中给属性赋的值不能传递到函数外，因此使用队列来传递值
'''
import threading
import time
import queue

class myThread(threading.Thread):   #继承父类threading.Thread
    def __init__(self, target, *args, **kwargs):
        threading.Thread.__init__(self)
        self.target = target
        self.args = args
        self.kwargs = kwargs

        self.__queue = queue.Queue()

    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        result = self.target(*self.args, **self.kwargs)
        self.__queue.put(result)

    @property
    def return_value(self):
        return self.__queue.get()

if __name__ == '__main__':
    def hello(something):
        print('hello',something)
        return something

    # 创建新线程
    thread = myThread(hello,"world")
    thread.name = 'mythread'#设置线程名字
    print(thread.getName())#输出线程名字
    # 开启线程
    thread.start()
    print(thread.return_value)#获得线程返回值