# extract变量覆盖

完全可以自己搭个环境来玩，加条highligh_file("index.php")


```plain
<?php
$flag='xxx';
extract($_GET);
if(isset($shiyan))
{
$content=trim(file_get_contents($flag));
if($shiyan==$content)
{
echo'ctf{xxx}';
}
else
{
echo'Oh.no';
}
}
?>
Plain Text
```



定义和用法


extract() 函数从数组中将变量导入到当前的符号表。


该函数使用数组键名作为变量名，使用数组键值作为变量值。针对数组中的每个元素，将在当前符号表中创建对应的一个变量。


第二个参数*type*用于指定当某个变量已经存在，而数组中又有同名元素时，extract() 函数如何对待这样的冲突。


该函数返回成功导入到符号表中的变量数目。


[http://127.0.0.1/Php_Bug/extract1.php?shiyan=&flag=1](http://127.0.0.1/Php_Bug/extract1.php?shiyan=&flag=1)


略微解释


首先是isset,只检查变量是否存在，不会去检查变量的值为空或者什么其他的东西


然后file_get_contents当文件不存在的时候的返回是个0,然后空=0



