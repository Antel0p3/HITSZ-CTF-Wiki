---
title: 使用指定版本libc执行/调试二进制文件方法
tags:
- CTF
- pwn
categories:
- pwn-learning
---
刚开始学习pwn的时候大部分人都会遇见由于libc版本与程序要求不匹配而导致的无法调试或运行的大坑。这是因为大部分程序是动态链接生成的，在首次执行到某些系统函数的时候会先在libc.so (shared object) 当中找到对应函数并执行，所以连接到错误版本的glibc，会出现攻击脚本失败，调试过程出错等情况。查看程序当前使用的libc版本的命令：`ldd ./bin`

解决方法如下：

## 0x1 glibc-all-in-one下载安装
```shell
git clone https://github.com/matrix1001/glibc-all-in-one.git
cd glibc-all-in-one/

python3 update_list
```
可以看到有list, old_list; download, download_old 文件

## 0x2 查看所有glibc版本
```shell
cat list
(输出:
2.23-0ubuntu11.3_amd64
2.23-0ubuntu11.3_i386
2.23-0ubuntu3_amd64
2.23-0ubuntu3_i386
2.27-3ubuntu1.5_amd64
2.27-3ubuntu1.5_i386
...

cat old_list
(输出:
2.21-0ubuntu4.3_amd64
2.21-0ubuntu4.3_i386
2.21-0ubuntu4_amd64
2.21-0ubuntu4_i386
2.24-3ubuntu1_amd64
2.24-3ubuntu1_i386
...
```
## 0x3 下载所需版本glibc(32位程序用 \*_i386 64位用 \*_amd64)
文件中download对应下载list中的glibc,  download_old对应下载old_list中的glibc
下载后的glibc在`./libs`目录中
```shell
./download 2.23-0ubuntu3_amd64
./download_old 2.24-3ubuntu1_i386
```

## 0x4 patchelf 下载安装
```shell
git clone https://github.com/NixOS/patchelf.git
cd patchelf

sudo apt-get install autoconf automake libtool
./boostrap.sh

./configure
make && make install
```

## 0x5 更换目标程序libc为指定libc (./bin为你想运行的elf文件)
```shell
patchelf --set-interpreter glibc-all-in-one/libs/2.23-0ubuntu3_amd64/ld-linux-x86-64.so.2 ./bin

libpath=$(patchelf --print-needed ./bin)    #获取当前连接的libc路径名称
patchelf --replace-needed "$libpath" glibc-all-in-one/libs/2.23-0ubuntu3_amd64/libc-2.23.so ./bin  #更换   第一个参数是libc*.so的目录, 每个版本名称不一样，仔细查看

```
## 0x6 可能问题： patchelf报错 `version GLIBC_2.34’ not found` 
解决方法（稍为繁琐）：在ubuntu18或ubuntu16中用gcc (gcc版本为7-) 编译，再将文件导入当前系统并进行以上patchelf操作，就可以正常执行了
具体原因笔者还没找到，可能是因为你当前linux系统版本较高，对应的gcc版本高，编译后的二进制文件无法与过早的glibc版本连接，但我尝试过在kali 6.0.0 (gcc版本为12.2.0) 中下载低版本gcc进行编译以及多种方式，还是同样的报错结果（如果有大神发现具体原因和更简便的解决方法能告诉我吗，感激）

> 个人博客 https://antel0p3.github.io/