web常用linux路径:

1./etc/passwd


2./etc/hosts


3./proc/net/arp


4./proc/net/dev


5./proc/net/dev_mcast


6./proc/net/igmp


7./proc/net/netlink


8./proc/net/netstat


9./proc/net/raw


10./proc/net/route


11./proc/net/rt_cache


12./proc/net/snmp


13./proc/net/sockstat


14./proc/net/tcp


15./proc/net/udp


16./proc/net/unix


# /proc/self/

## /proc/self/environ


尝试访问/proc/self/environ


/proc/self–其路径指向当前进程


/environ–记录当前进程的环境变量信息


## /proc/self/root


/proc/self/root/是指向/的符号链接，想到这里，用伪协议配合多级符号链接的办法进行绕过


漏洞存在的位置位于php的内核（我是很想尝试做一次调试的，但是没找着）


```plain
https://mp.weixin.qq.com/s?__biz=MzA5ODA0NDE2MA==&mid=2649729209&idx=1&sn=78c1f6cf291e5cfca3088f02216ccffd&chksm=888c98d6bffb11c014d8f98437879564702bd35b100f4337cbdf1f3cff827edfa4b9a8672637&mpshare=1&scene=23&srcid=0812s60kjiOtHT66otXJWIHt&sharer_sharetime=1597388716474&seharer_shareid=33a823b10ae99f33a60db621d83241cb#rd

```



所以最后："/proc/self/root"*21+/flag就可以完成绕过。


[WMCTF2020]Make PHP Great Again


代码十分简单，需要用到的是在群里所发的那个漏洞，/proc/self/root/是指向/的符号链接。（PHP内核我看起来也比较吃力）关键点应该是：lstat函数判断文件是否存在读取path存在了一个最大值，会认为路径不存在，然后有另外一个函数virtual_file_ex(..., CWD_FILEPATH)，当路径不存在时会返回一个合法的路径，因此绕过lstat后相当于时任意文件读取了，当然需要php的伪协议读流。


"/proc/self/root"*21+/flag











