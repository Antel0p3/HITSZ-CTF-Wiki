# .htaccess文件
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



分布式配置文件


全称是Hypertext Access(超文本入口)。提供了针对目录改变配置的方法， 即，在一个特定的文档目录中放置一个包含一个或多个指令的文件， 以作用于此目录及其所有子目录。作为用户，所能使用的命令受到限制。管理员可以通过Apache的AllowOverride指令来设置。.htaccess是一个纯文本文件，存放着一些apache指令，与httpd.conf类似，但作用范围仅限当前目录。


.htaccess是在用户访问该目录下的站点时加载的，不需要重启apache服务进行载入，更灵活但更耗系统资源。由于.htaccess可以配置很多东西，如目录访问、文件执行、错误页面重定向等


稍微举个例字：


<FilesMatch"1">


SetHandlerapplication/x-httpd-php


</FilesMatch>//或者干脆不要FilesMatch,这里的意思是配置，如果包含1，则将其视为php文件执行


通常在文件上传中使用。上传一个.htaccess文件之后就可以传入一个包含1的文件上去，乱杀执行。
