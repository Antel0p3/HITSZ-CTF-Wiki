# 其他

这里一般用来写一些用起来比较简单的类，可以自己添加。


DirectoryIterator	遍历目录


FilesystemIterator	遍历目录


GlobIterator  遍历目录，但是不同的点在于它可以通配例如/var/html/www/flag*


SplFileObject  读取文件，按行读取，多行需要遍历


finfo/finfo_open()需要两个参数


这是那天DASCTF&MAR中的反序列化学到的东西。这里就有类来读取文件了。


```plain
<?phpclass A{	public $class='SplFileObject';    public $para='/var/www/html/aMaz1ng_y0u_c0Uld_f1nd_F1Ag_hErE/flag.php';}echo serialize(new A());
PHP
```






