---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: GDOUCTF2023-小学数学-wp
date: 2023-06-13 09:01:08
tags:
- CTF
- pwn
- GDOUCTF2023
- nssctf
categories:
- pwn-wp
---
[相关资源](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/13/GDOUCTF2023-easymath-wp)

## exp
查看server.py代码逻辑, 简单替换运算
```python
from pwn import *
context.log_level = 'debug'

proc = remote("node4.anna.nssctf.cn", 28793)

def sl(x): return proc.sendline(x)
def sd(x): return proc.send(x)
def sla(x, y): return proc.sendlineafter(x, y)
def sa(x, y): return proc.sendafter(x, y)
def ru(x): return proc.recvuntil(x)
def rc(): return proc.recv()
def rl(): return proc.recvline()
def li(con): return log.info(con)
def ls(con): return log.success(con)
def pi(): return proc.interactive()
def pcls(): return proc.close()

d = {'//': '*', 'x': '-', '-': '+', '%': '//', '+': '%'}
sla(b'start...', b'')
for i in range(301):
    ru(b'Round')
    ru(b'\n')
    epr = ru(b'= ')[:-3].decode().split(' ') #空格分隔
    epr[1] = d[epr[1]] # 替换运算符
    epr = ''.join(epr)
    print(epr)
    sl(str(eval(epr)).encode())
```