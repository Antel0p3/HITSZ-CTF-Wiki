# LD_PRELOAD函数劫持

这个漏洞我问过卓腾龙学长


如果有不会的，看不懂的可以去问他


这里的内容会牵扯到一些linux内核，处理机制相关的知识


就算实在不会利用的，我也给出了一种相对简单的方法


下面是预备知识


################################################################


LD_PRELOAD使用限制


这种方式虽然很酷，但却有一些限制。比如对于静态编译的程序是无效的。因为静态编译的程序不需要连接动态库的面的函数。而且，假如文件的SUID或SGID位被置1，加载的时候会忽略LD_PRELOAD(这是ld的开发者出于安全考虑做的)。


################################################################


## 首先给出linux程序的三种链接


```plain
静态链接：在程序运行之前先将各个目标模块以及所需要的库函数链接成一个完整的可执行程序，之后不再拆开。
装入时动态链接：源程序编译后所得到的一组目标模块，在装入内存时，边装入边链接。
运行时动态链接：原程序编译后得到的目标模块，在程序执行过程中需要用到时才对它进行链接

```



对于动态链接来说，需要一个动态链接库，其作用在于当动态库中的函数发生变化对于可执行程序来说时透明的，可执行程序无需重新编译，方便程序的发布/维护/更新。但是由于程序是在运行时动态加载，这就存在一个问题，假如程序动态加载的函数是恶意的，就有可能导致disable_function被绕过。(这里的disable_function就是系统所过滤的函数。)


## LD_PRELOAD介绍


在UNIX的动态链接库的世界中，LD_PRELOAD就是这样一个环境变量，它可以影响程序的运行时的链接（Runtimelinker），它允许你定义在程序运行前优先加载的动态链接库。这个功能主要就是用来有选择性的载入不同动态链接库中的相同函数。通过这个环境变量，我们可以在主程序和其动态链接库的中间加载别的动态链接库，甚至覆盖正常的函数库。一方面，我们可以以此功能来使用自己的或是更好的函数（无需别人的源码），而另一方面，我们也可以以向别人的程序注入恶意程序，从而达到那不可告人的罪恶的目的。





