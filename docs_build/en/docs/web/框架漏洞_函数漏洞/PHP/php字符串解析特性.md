# PHP的字符串解析特性
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



```
我们知道 PHP 将查询字符串转换为内部关联数组 $_GET 或关联数组 $_POST。例如：/?foo=bar 将变成 Array([foo] => "bar")。值得注意的是，查询字符串在解析的过程中会将某些字符删除或用下划线代替。例如，/?%20news[id%00=42 会转换为Array([news_id] => 42)。如果一个 IDS/IPS 或 WAF 中有一条规则是当 news_id 参数的值是一个非数字的值则拦截，那么我们就可以用以下语句绕过：

/news.php?%20news[id%00=42"+AND+1=0–-+

So when we pass parameters, we use [ instead of _ to bypass the Waf here

```
