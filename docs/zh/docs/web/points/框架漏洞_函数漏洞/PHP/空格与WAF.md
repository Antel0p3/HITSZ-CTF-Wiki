# 空格与WAF

## 假如waf不允许num变量传递字母：





[http://www.xxx.com/index.php?num=](http://www.xxx.com/index.php?num=)aaaa   //显示非法输入的话





那么我们可以在num前加个空格：





[http://www.xxx.com/index.php?num](http://www.xxx.com/index.php?num)= aaaa





这样waf就找不到num这个变量了，因为现在的变量叫“ num”，而不是“num”。但php在解析的时候，会先把空格给去掉，这样我们的代码还能正常运行，还上传了非法字符。




