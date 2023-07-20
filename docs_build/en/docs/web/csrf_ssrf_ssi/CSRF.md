# CSRF
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



csrf（**Cross Site Request Forgery**）跨站请求伪造


高级一点的XSS


站是通过**cookie**来识别用户的，当用户成功进行身份验证之后浏览器就会得到一个标识其身份的**cookie**，只要不关闭浏览器或者退出登录，以后访问 这个网站会带上这个**cookie**


如果这期间浏览器被人控制着请求了这个网站的**url**，可能就会执行一些用户不想做的功能（比如修改个人资料）


这个请求并不是用户真正想发出的请求，这就是所谓的<**请求伪造**>


因为这些请求也是可以从第三方网站提交的，所以前面加上<**跨站**>二字


所以经常XSS所弹出的cookie是用来做csrf请求伪造的。


比如我们打算攻击一个存在问题的**Blog**，那就先去目标**Blog**留言，留下一个网址，诱其**Blog**的主人点击（当然，这是一种方法，也可以使用我们上节课讲的**XSS**），然后构造个**HTML**表单提交些数据过去。

## 漏洞示例

一个典型的CSRF攻击有着如下的流程：


>*受害者登录a.com，并保留了登录凭证（Cookie）。*攻击者引诱受害者访问了b.com。*b.com 向 a.com 发送了一个请求：a.com/act=xx。浏览器会默认携带a.com的Cookie。*a.com接收到请求后，对请求进行验证，并确认是受害者的凭证，误以为是受害者自己发送的请求。*a.com以受害者的名义执行了act=xx。*攻击完成，攻击者在受害者不知情的情况下，冒充受害者，让a.com执行了自己定义的操作。

GET型


```plain
<img src=http://xxx.org/csrf.php?xx=1 />
访问页面后就成功向http://xxx.org/csrf.php 发送了一次请求
<link href="…">
<iframe src="…">
<meta http-equiv="refresh" content="0; url=…">
<script src="…">
<video src="…">
<audio src="…">
<a href="…">
<table background="…">
Plain Text
```



POST型


```plain
<form action=http://woyun.org/csrf.php method=POST>
<input type="text" name='xx' value='11' />
</form>
<script>document.forms[0].submit();</script>
Plain Text
```

## 例题

从一道高质量的ctf题中看渗透测试 - 安全客，安全资讯平台

最近做了一道质量挺不错的ctf题，涉及web渗透、sql注入、csrf、权限提升等知识点，所以特地重新自己搭了个环境复现了一下这道高质量的ctf题分享给大家，并谈谈一些个人的感悟。

![图片](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAFIUlEQVRYCb3Bb2zUdx3A8ffn8/v27no9uubuSrvaMmDFMChUiBO3PdA47ex0krlsz8yWjBgTjCT+iQ/1gfGRW7IHS8wCi3+euQfEado6fSBsTDdIMFQIi6PAugKl5Vq69nq93u/zkUtoJJf+oIZtr5dwi+dHXsxH2D53fQx8K5AHMtydClACOYv7sKm8eujrPyxxk3DTvuEXHsflt0CRT9Y04s8eHPzREDcINzw3/NLj6v5HIPDpqJnI3t8MHhiS50dezJtF7wFF1iClgb72DfS2dZLP5KibqSzw/uxlRqc+oGo11qikGm8JNWvaBxS5A0V49L4+vrF5N7lUhkaPspP5aoWhsZP87eIohnMHeTPdF9zlMe4gHTWxf9dX2V7s4XZyqQzPbH2IvvYeXj75Vyq1ZW7HhcFgLlsREinC/l1fY3uxmzp35/S1CY5N/IcP50vg0L0uz8NdvfQVuxERthW62b9rgBdOjGBu3MZng4nkuY2BjTvYXuymrhrXeOXUUY5PjnGrD+ZnePvyOT7fsYnv7vwS6SiwrfAZBjbuYOj8KRI5RTU0YyiGYiiGYiiGEjTFE5v7qXN3Xhl9k3cmL2AohmIohmIohvLu5EV+feoo7k7dNzf30xSlMRRDMRRDMRRDMTSl5oK5YC6YC+aCuWAu9Lf3kEtlqDt97TL/uHwBc8FcMBfMBXPBXDAXzIV3r1xkdPoSdS1NaT7X3oO5YC6YC+aCuWAumAtqKIZiKIZiKIZiKL1tHax469IYhmIohmIohmIohmIohmIob14aY8WWtg4MxVAMxVAMxVAMJZgLSVSU0mKZunPXZzAX1mL8o+vU4pi61nQz5kKSYChJDp05waEzJ/gfZS0W45hr5XnqytUlDCVJMIQkHc05Cpks/698uplKbZm6pdgwhCQhdiHJz/cM0JVr5W5cq9WIXUgSHGU1xUyWe1vWcbfcBUdJEgxhNX2FTkSEj4MhJAmxC6vZUejg4+BA7EKSECOspr/YSZ2784OjQ/zsC1/mF8eP8P2de/jVyWPUPXLvBqYWyzzU2c3EwhzmsK4pxdtXxpldqvCT3Y/gCDFCkhCjNOpoztKZbWHF2NwsL48eZ3zhI5biGBXlqd5tPNjexff+/mfKtWXG5+fIRIHB+3qZWizzzJY+ulpa+XBhgRglSYhdaNRf6EBEWJGKAterVeaXa9QtxcbUYhkRobetwL+mr9KZbWFmqcLAhl4iVYYvvs/8cpVCc47YhSQhRmjUX1jPrUSUA/172H9kBBCmlyq8MX6Bntw97G7vIteUYVNrG+Pzc5yfm+F37/0bQdjcmmd2eZkYIYnsOfwHp0FntoV7UinqfvngF+nKtiAiuDt3IiKYOwKICG9ducSP/3mMJCFGaTRRXmSivEjdUhwjItSJCGuhIqxwhxhlVQ7BXCpAhgTm3BVHMBcSVIMhJaCLBC+dPsPDHetZEYmwPZcjEwKZEJEJgXQUkQoRkSiNzA1DSDAdYuQsSBcJjkxe5cjkVVZszDZzYMv95DMZouYM2RARIkFwHKOR4cQoq/OzISYaxv0rrNGuQoEHigXWpdOkQ4QgiJDIEWIXViU6HFISH1z06KdAkTVYRinVYkq1MmvxzlSJGGEV080SHxRu6H3t9QFX+ROQ4tPgVFHbe+7be0eEmza99vqAi/weZD2fKL8q7t85//S33uAG4RYbDx9uM2t6zl0GHbaC50EygNLISSasMJwqMC1wFucvUVP11QtPPjnLTf8FJngeQoTy2TUAAAAASUVORK5CYII=)[https://www.anquanke.com/post/id/97567](https://www.anquanke.com/post/id/97567)

大家自己看看？确实是高级点的XSS,比较重合，不做过多叙述




