# escapeshellarg()+escapeshellcmd()
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



escapeshellarg会对所有单引号进行转义,并且给字符串增加一个 单引号





escapeshellcmd仅会对落单了的单引号进行转义，对一些特殊字符进行转义如：& # ;` | * ? ~ < > ^ ( ) [ ] { } $





传入的参数是：172.17.0.2'-v -d a=1





经过escapeshellarg处理后变成了'172.17.0.2'\'' -v -d a=1'，即先对单引号转义，再用单引号将左右两部分括起来从而起到连接的作用。





经过escapeshellcmd处理后变成'172.17.0.2'\\'' -v -d a=1\'，这是因为escapeshellcmd对\以及最后那个不配对儿的引号进行了转义：[http://php.net/manual/zh/function.escapeshellcmd.php](http://php.net/manual/zh/function.escapeshellcmd.php)





最后执行的命令是curl'172.17.0.2'\\'' -v -d a=1\'，由于中间的\\被解释为\而不再是转义字符，所以后面的'没有被转义，与再后面的'配对儿成了一个空白连接符。所以可以简化为curl 172.17.0.2\ -v -da=1'，即向172.17.0.2\发起请求，POST 数据为a=1'。



