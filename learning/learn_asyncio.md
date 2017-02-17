参考[asyncio协程](http://mp.weixin.qq.com/s/mI7SYWQ3EKdu-SuL9UtzOg)
* event_loop 事件循环：程序开启一个无限的循环，程序员会把一些函数注册到事件循环上。当满足事件发生的时候，调用相应的协程函数。  
* coroutine 协程：协程对象，指一个使用async关键字定义的函数，它的调用不会立即执行函数，而是会返回一个协程对象。协程对象需要注册到事件循环，由事件循环调用。
* task 任务：一个协程对象就是一个原生可以挂起的函数，任务则是对协程进一步封装，其中包含任务的各种状态。
* future： 代表将来执行或没有执行的任务的结果。它和task上没有本质的区别
* async/await 关键字：python3.5 用于定义协程的关键字，async定义一个协程，await用于挂起阻塞的异步调用接口。

#### 定义一个协程
定义一个协程很简单，使用async关键字，就像定义普通函数一样：
```
import time
import asyncio
 
now = lambda : time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
start = now()
 
coroutine = do_some_work(2)
 
loop = asyncio.get_event_loop()
loop.run_until_complete(coroutine)
 
print('TIME: ', now() - start)
```
通过async关键字定义一个协程（coroutine），协程也是一种对象。协程不能直接运行，需要把协程加入到事件循环（loop），由后者在适当的时候调用协程。asyncio.get_event_loop方法可以创建一个事件循环，然后使用run_until_complete将协程注册到事件循环，并启动事件循环。
#### 创建一个task
协程对象不能直接运行，在注册事件循环的时候，其实是run_until_complete方法将协程包装成为了一个任务（task）对象。所谓task对象是Future类的子类。保存了协程运行后的状态，用于未来获取协程的结果。
```
import asyncio
import time
 
now = lambda : time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
start = now()
 
coroutine = do_some_work(2)
loop = asyncio.get_event_loop()
# task = asyncio.ensure_future(coroutine)
task = loop.create_task(coroutine)
print(task)
loop.run_until_complete(task)
print(task)
print('TIME: ', now() - start)
```
创建task后，task在加入事件循环之前是pending状态，因为do_some_work中没有耗时的阻塞操作，task很快就执行完毕了。后面打印的finished状态。

asyncio.ensure_future(coroutine) 和 loop.create_task(coroutine)都可以创建一个task，run_until_complete的参数是一个futrue对象。当传入一个协程，其内部会自动封装成task，task是Future的子类。isinstance(task, asyncio.Future)将会输出True。
#### 绑定回调
绑定回调，在task执行完毕的时候可以获取执行的结果，回调的最后一个参数是future对象，通过该对象可以获取协程返回值。如果回调需要多个参数，可以通过偏函数导入。
```
import time
import asyncio
 
now = lambda : time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
    return 'Done after {}s'.format(x)
 
def callback(future):
    print('Callback: ', future.result())
 
start = now()
 
coroutine = do_some_work(2)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(coroutine)
task.add_done_callback(callback)
loop.run_until_complete(task)
 
print('TIME: ', now() - start)
```
多个参数
```
def callback(t, future):
    print('Callback:', t, future.result())
 
task.add_done_callback(functools.partial(callback, 2))
```
可以看到，coroutine执行结束时候会调用回调函数。并通过参数future获取协程执行的结果。我们创建的task和回调里的future对象，实际上是同一个对象。

#### future与result
回调一直是很多异步编程的恶梦，程序员更喜欢使用同步的编写方式写异步代码，以避免回调的恶梦。回调中我们使用了future对象的result方法。前面不绑定回调的例子中，我们可以看到task有fiinished状态。在那个时候，可以直接读取task的result方法。
```
async def do_some_work(x):
    print('Waiting {}'.format(x))
    return 'Done after {}s'.format(x)
 
start = now()
 
coroutine = do_some_work(2)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(coroutine)
loop.run_until_complete(task)
 
print('Task ret: {}'.format(task.result()))
print('TIME: {}'.format(now() - start))
```

#### 阻塞与await
使用async可以定义协程对象，使用await可以针对耗时的操作进行挂起，就像生成器里的yield一样，函数让出控制权。协程遇到await，事件循环将会挂起该协程，执行别的协程，直到其他的协程也挂起或者执行完毕，再进行下一个协程的执行。

耗时的操作一般是一些IO操作，例如网络请求，文件读取等。我们使用asyncio.sleep函数来模拟IO操作。协程的目的也是让这些IO操作异步化。
```
import asyncio
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
start = now()
 
coroutine = do_some_work(2)
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(coroutine)
loop.run_until_complete(task)
 
print('Task ret: ', task.result())
print('TIME: ', now() - start)
```
在 sleep的时候，使用await让出控制权。即当遇到阻塞调用的函数的时候，使用await方法将协程的控制权让出，以便loop调用其他的协程。现在我们的例子就用耗时的阻塞操作了。
#### 并发和并行
并发和并行一直是容易混淆的概念。并发通常指有多个任务需要同时进行，并行则是同一时刻有多个任务执行。用上课来举例就是，并发情况下是一个老师在同一时间段辅助不同的人功课。并行则是好几个老师分别同时辅助多个学生功课。简而言之就是一个人同时吃三个馒头还是三个人同时分别吃一个的情况，吃一个馒头算一个任务。

asyncio实现并发，就需要多个协程来完成任务，每当有任务阻塞的时候就await，然后其他协程继续工作。创建多个协程的列表，然后将这些协程注册到事件循环中。
```
import asyncio
 
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
start = now()
 
coroutine1 = do_some_work(1)
coroutine2 = do_some_work(2)
coroutine3 = do_some_work(4)
 
tasks = [
    asyncio.ensure_future(coroutine1),
    asyncio.ensure_future(coroutine2),
    asyncio.ensure_future(coroutine3)
]
 
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
 
for task in tasks:
    print('Task ret: ', task.result())
 import asyncio
 
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
start = now()
 
coroutine1 = do_some_work(1)
coroutine2 = do_some_work(2)
coroutine3 = do_some_work(4)
 
tasks = [
    asyncio.ensure_future(coroutine1),
    asyncio.ensure_future(coroutine2),
    asyncio.ensure_future(coroutine3)
]
 
loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait(tasks))
 
for task in tasks:
    print('Task ret: ', task.result())
 
print('TIME: ', now() - start)
```

#### 协程嵌套
使用async可以定义协程，协程用于耗时的io操作，我们也可以封装更多的io操作过程，这样就实现了嵌套的协程，即一个协程中await了另外一个协程，如此连接起来。
```
import asyncio
 
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
async def main():
    coroutine1 = do_some_work(1)
    coroutine2 = do_some_work(2)
    coroutine3 = do_some_work(4)
 
    tasks = [
        asyncio.ensure_future(coroutine1),
        asyncio.ensure_future(coroutine2),
        asyncio.ensure_future(coroutine3)
    ]
    
    dones, pendings = await asyncio.wait(tasks)
 
    for task in dones:
        print('Task ret: ', task.result())
 
start = now()
 
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
 
print('TIME: ', now() - start)
```
asyncio.wait() 等待task或future对象完成，返回两个future集合，done和pending

如果使用的是 asyncio.gather创建协程对象，那么await的返回值就是协程运行的结果。
```
results = await asyncio.gather(*tasks)
for result in results:
        print('Task ret: ', result)
```
不在main协程函数里处理结果，直接返回await的内容，那么最外层的run_until_complete将会返回main协程的结果。
```
async def main():
    coroutine1 = do_some_work(1)
    coroutine2 = do_some_work(2)
    coroutine3 = do_some_work(2)
 
    tasks = [
        asyncio.ensure_future(coroutine1),
        asyncio.ensure_future(coroutine2),
        asyncio.ensure_future(coroutine3)
    ]
 
    return await asyncio.gather(*tasks)
 
start = now()
 
loop = asyncio.get_event_loop()
results = loop.run_until_complete(main())
 
for result in results:
    print('Task ret: ', result)
```
也可以使用asyncio的as_completed方法(返回一个迭代对象)
```
async def main():
    coroutine1 = do_some_work(1)
    coroutine2 = do_some_work(2)
    coroutine3 = do_some_work(4)
 
    tasks = [
        asyncio.ensure_future(coroutine1),
        asyncio.ensure_future(coroutine2),
        asyncio.ensure_future(coroutine3)
    ]
    for task in asyncio.as_completed(tasks):
        result = await task
        print('Task ret: {}'.format(result))
 
start = now()
 
loop = asyncio.get_event_loop()
done = loop.run_until_complete(main())
print('TIME: ', now() - start)
```
#### 协程停止
上面见识了协程的几种常用的用法，都是协程围绕着事件循环进行的操作。future对象有几个状态：

* Pending
* Running
* Done
* Cancelled

创建future的时候，task为pending，事件循环调用执行的时候当然就是running，调用完毕自然就是done，如果需要停止事件循环，就需要先把task取消。可以使用asyncio.Task获取事件循环的task
```
import asyncio
 
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
coroutine1 = do_some_work(1)
coroutine2 = do_some_work(2)
coroutine3 = do_some_work(2)
 
tasks = [
    asyncio.ensure_future(coroutine1),
    asyncio.ensure_future(coroutine2),
    asyncio.ensure_future(coroutine3)
]
 
start = now()
 
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(asyncio.wait(tasks))
except KeyboardInterrupt as e:
    print(asyncio.Task.all_tasks())
    for task in asyncio.Task.all_tasks():
        print(task.cancel())
    loop.stop()
    loop.run_forever()
finally:
    loop.close()
 
print('TIME: ', now() - start)
```
启动事件循环之后，马上ctrl+c，会触发run_until_complete的执行异常 KeyBorardInterrupt。

循环task，逐个cancel是一种方案，可是正如上面我们把task的列表封装在main函数中，main函数外进行事件循环的调用。这个时候，main相当于最外出的一个task，那么处理包装的main函数即可。
```
import asyncio
 
import time
 
now = lambda: time.time()
 
async def do_some_work(x):
    print('Waiting: ', x)
 
    await asyncio.sleep(x)
    return 'Done after {}s'.format(x)
 
async def main():
    coroutine1 = do_some_work(1)
    coroutine2 = do_some_work(2)
    coroutine3 = do_some_work(4)
 
    tasks = [
        asyncio.ensure_future(coroutine1),
        asyncio.ensure_future(coroutine2),
        asyncio.ensure_future(coroutine3)
    ]
 
    return await asyncio.gather(*tasks)
 
 
start = now()
 
loop = asyncio.get_event_loop()
task = asyncio.ensure_future(main())
try:
    loop.run_until_complete(task)
except KeyboardInterrupt as e:
    print(asyncio.Task.all_tasks())
    print(asyncio.gather(*asyncio.Task.all_tasks()).cancel())
    loop.stop()
    loop.run_forever()
finally:
    loop.close()
print('TIME: ', now() - start)
```
