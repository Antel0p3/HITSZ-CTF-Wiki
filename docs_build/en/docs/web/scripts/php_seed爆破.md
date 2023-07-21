# php seed爆破
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



```plain
是php中的两个生成随机数的函数其实是伪随机数，也就是说可以爆破出来具体该怎么做好像也没什么好解释的，所以干脆直接把代码放上来用好了。

s = 'abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
key = 'c1z5DuPZXT'
m = ''
for i in key:
    for j in range(len(s)):
        if i == s[j]:
            m += "{} {} 0 {} ".format(j,j,len(s)-1)
print(m)
将生成的参数放到一个叫做php_mt_seed4.0的脚本中就好了
使用了mt_srand()函数播种，并使用mt_rand()函数生成随机数。这里的随机数都是伪随机数，只要得到种子，就可以生成相同的随机数。
```



下面的东西可以下载php_mt_seed4.0：

https://thoughts.aliyun.com/workspaces/5f98e6276b9dce0024026750/docs/607d8129e87e050001924835




