---
title: 符号表恢复
date: 2023-08-12 15:42:12
tags:
- CTF
- pwn
- reverse
- libc
categories:
- pwn-learning
---

遇到静态编译且符号表被抠除的程序（如下图），很不利于分析

![img](0x1.png)

以下介绍恢复符号表的几种方法  

## 1. IDA flair 
flair通过选择的签名文件和程序中的函数进行签名匹配来帮助我们还原库函数   
其中签名文件可以从[sig-database](https://github.com/push0ebp/sig-database)中获取，有制作好的各架构各版本签名文件    
### 使用方法
1. 将签名文件(sig文件)导入到IDA的对应签名目录下`IDAx.x\sig\pc`
2. IDA中按住`SHIFT+F5`
3. 右键选择`Apply new signature...`   
![img](0x2.png)   
4. 选择签名文件进行匹配   
![img](0x3.png)    
5. 多尝试几个签名文件，直到成功匹配函数数量最多（Ctrl+Z 撤销之前选择的签名文件）   
![img](0x4.png)    
可以看到很多函数名已经恢复，代码也就好分析多了  

### 总结
这种方法恢复符号表无需联网，但恢复有时效果也不好，在某些不能联网的比赛中可以作为首选

## 2. 自动检测脚本lscan
[lscan](https://github.com/maroueneboubakri/lscan)可以自动检测静态二进制程序使用的libc版本

### 使用方法
```sh
git clone https://github.com/maroueneboubakri/lscan
cd lscan
python lscan -S [签名文件所在目录] -f [待检测文件]
# python lscan -S ./i386/sig -f ../bin
```

## 3. IDA Finger插件
Finger是阿里云·云安全技术实验室推出的一款二进制函数符号识别引擎，可以识别二进制程序中的库函数与常见的第三方函数，快速定位恶意代码，提高样本分析效率   
### 使用方法
1. pip 安装finger_sdk  
`pip install finger_sdk`
注意安装Finger的python的版本要与IDAPython的版本一致
2. 将[Finger IDA plugin](https://github.com/aliyunav/Finger/blob/master/finger_plugin.py)复制到IDA插件目录`IDAx.x\plugins`中  
3. 重启IDA 在顶部菜单栏中可以看见`Finger`，选择支持单个函数、选中的多个函数和全部函数识别

### 总结
这种方法识别精度高，但需要联网并且函数较多时速度很慢