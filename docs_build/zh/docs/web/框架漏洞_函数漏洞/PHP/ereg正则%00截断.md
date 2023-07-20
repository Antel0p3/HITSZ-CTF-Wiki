# ereg正则%00截断

```plain

<?php
$flag = "flag";
if (isset ($_GET['nctf'])) {
if (@ereg ("^[1-9]+$", $_GET['nctf']) === FALSE)
echo '必须输入数字才行';
else if (strpos ($_GET['nctf'], '#biubiubiu') !== FALSE)
die('Flag: '.$flag);
else
echo '骚年，继续努力吧啊~';
}
?>
Plain Text
```



ereg函数遇到%00会认为函数执行完毕


[http://127.0.0.1/Php_Bug/16.php?nctf=1%00%23biubiubiu](http://127.0.0.1/Php_Bug/16.php?nctf=1%00%23biubiubiu)





