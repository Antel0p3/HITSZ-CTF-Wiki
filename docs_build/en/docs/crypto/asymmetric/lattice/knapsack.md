# 背包加密
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



## 背包问题

首先，我们先来介绍一下背包问题，假定一个背包可以称重 W，现在有 n 个物品，其重量分别为 $a_1, a_2,...,a_n$ 我们想问一下装哪些物品可以恰好使得背包装满，并且每个物品只能被装一次。这其实就是在解这样的一个问题

$$
x_1a_1+x_2a_2+,...,+x_na_n=W
$$

其中所有的 $x_i$ 只能为 0 和 1。显然我们必须枚举所有的 n 个物品的组合才能解决这个问题，而复杂度也就是 $2^n$，这也就是背包加密的妙处所在。

在加密时，如果我们想要加密的明文为 x，那么我们可以将其表示为 n 位二进制数，然后分别乘上 $a_i$ 即可得到加密结果。

但是解密的时候，该怎么办呢？我们确实让其他人难以解密密文，但是我们自己也确实没有办法解密密文。

但是当 $a_i$ 是超递增的话，我们就有办法解了，所谓超递增是指序列满足如下条件

$$
a_i>\sum_{k=1}^{i-1}a_k
$$

即第 i 个数大于前面所有数的和。

为什么满足这样的条件就可以解密了呢？这是因为如果加密后的结果大于 $a_n$ 的话，其前面的系数为必须 1 的。反之，无论如何也无法使得等式成立。因此，我们可以立马得到对应的明文。

但是，这样又出现了一个问题，由于 $a_i$ 是公开的，如果攻击者截获了密文，那么它也就很容易去破解这样的密码。为了弥补这样的问题，就出现了 Merkle–Hellman 这样的加密算法，我们可以使用初始的背包集作为私钥，变换后的背包集作为公钥，再稍微改动加密过程，即可。

这里虽然说了超递增序列，但是却没有说是如何生成的。

## Merkle–Hellman

### 公私钥生成

#### 生成私钥

私钥就是我们的初始的背包集，这里我们使用超递增序列，怎么生成呢？我们可以假设 $a_1=1$，那么 $a_2$ 大于 1 即可，类似的可以依次生成后面的值。

#### 生成公钥

在生成公钥的过程中主要使用了模乘的运算。

首先，我们生成模乘的模数 $m$，这里要确保

$$
m>\sum_{i=1}^{i=n}a_i
$$

其次，我们选择模乘的乘数 $w$，作为私钥并且确保

$$
gcd(w,m)=1
$$

之后，我们便可以通过如下公式生成公钥

$$
b_i \equiv w a_i \bmod m
$$

并将这个新的背包集 $b_i$ 和 $m$ 作为公钥。

### 加解密

#### 加密

假设我们要加密的明文为 $v$，其每一个比特位为 $v_i$，那么我们加密的结果为

$$
\sum_{i=1}^{i=n}b_iv_i \bmod m
$$

#### 解密

对于解密方，首先可以求的 $w$ 关于 $m$ 的逆元 $w^{-1}$。

然后我们可以将得到的密文乘以 $w^{-1}$ 即可得到明文，这是因为

$$
\sum_{i=1}^{i=n}w^{-1}b_iv_i \bmod m=\sum_{i=1}^{i=n}a_iv_i \bmod m
$$

这里有

$$
b_i \equiv w a_i \bmod m
$$

对于每一块的加密的消息都是小于 m 的，所以求得结果自然也就是明文了。

### 破解

该加密体制在提出后两年后该体制即被破译，破译的基本思想是我们不一定要找出正确的乘数 w（即陷门信息），只需找出任意模数 `m′` 和乘数 `w′`，只要使用 `w′` 去乘公开的背包向量 B 时，能够产生超递增的背包向量即可。

参考 https://www.ruanx.net/lattice-2/ 

这里详细解释一下 https://www.ruanx.net/lattice-2/ 中用LLL算法攻击背包密码的细节.

首先明确一下各个符号的含义.

$M = (m_1, m_2, \dots, m_n)$ 是公钥，$x = (x_1, x_2, \dots, x_n)$ 是明文，$x_i$ 代表明文的**1个bit**，取0或1.

密文为

$$
S = \sum_{i = 1}^nx_im_i
$$

攻击者构造如下矩阵（后面会解释为什么构造这样的矩阵）

$$
\begin{pmatrix} 2&0&0&\cdots&0&m_1\\0&2&0&\cdots&0&m_2 \\ 0&0&2&\cdots&0&m_3 \\ \vdots & \vdots & \vdots & \ddots & \vdots & \vdots \\ 0&0&0&\cdots& 2 & m _ n \\ 1&1&1&\cdots &1&S\end{pmatrix}
$$

设矩阵的第$i$行为向量$v_i$.

这些向量 $v_i$ 张成了一个Lattice，以下向量显然在这个Lattice中

$$
{t} = \sum _{i=1} ^ n x_ i v_i - v_ {n+1} = (2x_1 - 1, 2x_2 - 1, \dots, 2x_n - 1, 0)
$$

注意到这里的 $x_i$ 都是0或1，所以 $2x_i-1$ 只能取1或-1，这就使得这个向量**非常短**，而LLL算法就是求Lattice中短向量的算法.

矩阵中的2和1都是为了使向量 $t$ 最短而选择的.

---

考虑另一种明文形式，若 $x_i$ 不是0或1，而是任意的ASCII码对应则字符，范围为0到128（或32到128），那么就可以构造如下矩阵

$$
\begin{pmatrix} a&0&0&\cdots&0&m_1/c\\0&a&0&\cdots&0&m_2/c \\ 0&0&a&\cdots&0&m_3/c \\ \vdots & \vdots & \vdots & \ddots & \vdots & \vdots \\ 0&0&0&\cdots& a & m _ n/c \\ b&b&b&\cdots &b&S/c\end{pmatrix}
$$

其中，$a$ 取1，$b$ 取64，可以让向量 $t$ 最短.

以上数值的选取只是粗略估计，也许考虑到明文的特定取值范围会有更好的取法（例如`flag`全是小写字母+数字时）.

至于 $c$，个人感觉比较玄学，应该是为了缩短向量的长度，方便LLL算法计算，$c$ 过小向量会很长，$c$ 过大则会损失 $m_i$ 的有效位数.



### 例题 [2021 红帽杯]primegame

```python
#!/usr/bin/env python3

from decimal import *
import math
import random
import struct
from flag import flag

assert (len(flag) == 48)
msg1 = flag[:24]
msg2 = flag[24:]
primes = [2] # 2到90的所有素数
for i in range(3, 90):
    f = True
    for j in primes:
        if i * i < j:
            break
        if i % j == 0:
            f = False
            break
    if f:
        primes.append(i)

getcontext().prec = 100 # 100位有效数字
keys = []
for i in range(len(msg1)):
    keys.append(Decimal(primes[i]).ln())
# keys: 2到89的素数的自然对数

sum_ = Decimal(0.0)
for i, c in enumerate(msg1):
    sum_ += c * Decimal(keys[i])

ct = math.floor(sum_ * 2 ** 256)
print(ct)

sum_ = Decimal(0.0)
for i, c in enumerate(msg2):
    sum_ += c * Decimal(keys[i])

ct = math.floor(sum_ * 2 ** 256)
print(ct)
#597952043660446249020184773232983974017780255881942379044454676980646417087515453
#425985475047781336789963300910446852783032712598571885345660550546372063410589918
```

#### EXP

```python
#sage
import math
from decimal import *
import random

getcontext().prec = int(100)

primes = [2]
for i in range(3, 90):
    f = True
    for j in primes:
        if i * i < j:
            break
        if i % j == 0:
            f = False
            break
    if f:
        primes.append(i)

keys = []
for i in range(len(primes)):
    keys.append(Decimal(int(primes[i])).ln())

arr = []
for v in keys:
    arr.append(int(v * int(2)^int(256)))


def encrypt(res):
    h = Decimal(int(0))
    for i in range(len(keys)):
        h += res[i] * keys[i]
    ct = int(h * int(2)^int(256))
    return ct


def solve(N):
    ln = len(arr)
    A = Matrix(ZZ, ln + 1, ln + 1)
    for i in range(ln):
        A[i, i] = 1
        A[i, ln] = arr[i] // N
        A[ln, i] = 64 # 用来减小向量t的2范数

    A[ln, ln] = ct // N
    res = A.LLL()
    for i in range(ln + 1):
        flag = True
        for j in range(ln):
            if -64 <= res[i][j] and res[i][j] < 64:
                continue
            flag = False
            break
        if flag:
            vec = [int(v + 64) for v in res[i][:-1]]
            ret = encrypt(vec)
            if ret == ct:
                print(vec)
                print(N, bytes(vec))
                return 1
    return 0

ct = 597952043660446249020184773232983974017780255881942379044454676980646417087515453
for i in range(2, 10000):
    # print(i)
    if solve(i):
        break

ct = 425985475047781336789963300910446852783032712598571885345660550546372063410589918
for i in range(2, 10000):
    # print(i)
    if solve(i):
        break
    
'''
root@kali:~/ctf/SageMath# ./sage ./script/test.sage
[102, 108, 97, 103, 123, 55, 49, 53, 99, 51, 57, 99, 51, 45, 49, 98, 52, 54, 45, 52, 99, 50, 51, 45]
83 b'flag{715c39c3-1b46-4c23-'
[56, 48, 48, 54, 45, 50, 55, 98, 52, 51, 101, 98, 97, 50, 52, 52, 54, 125, 0, 0, 0, 0, 0, 0]
2130 b'8006-27b43eba2446}\x00\x00\x00\x00\x00\x00'
'''
```





### 例题 [ASIS Cyber Security Contest Quals 2014]Archaic

[题目链接](https://github.com/ctfs/write-ups-2014/tree/b02bcbb2737907dd0aa39c5d4df1d1e270958f54/asis-ctf-quals-2014/archic)

首先查看源程序

```python
secret = 'CENSORED'
msg_bit = bin(int(secret.encode('hex'), 16))[2:]
```

首先得到了 secret 的所有二进制位。

其次，利用如下函数得到 keypair，包含公钥与私钥。

```python
keyPair = makeKey(len(msg_bit))
```

仔细分析 makekey 函数，如下

```python
def makeKey(n):
	privKey = [random.randint(1, 4**n)]
	s = privKey[0]
	for i in range(1, n):
		privKey.append(random.randint(s + 1, 4**(n + i)))
		s += privKey[i]
	q = random.randint(privKey[n-1] + 1, 2*privKey[n-1])
	r = random.randint(1, q)
	while gmpy2.gcd(r, q) != 1:
		r = random.randint(1, q)
	pubKey = [ r*w % q for w in privKey ]
	return privKey, q, r, pubKey
```

可以看出 prikey 是一个超递增序列，并且得到的 q 比 prikey 中所有数的和还要大，此外我们得到的 r，恰好与 q 互素，这一切都表明了该加密是一个背包加密。

果然加密函数就是对于消息的每一位乘以对应的公钥并求和。

```python
def encrypt(msg, pubKey):
	msg_bit = msg
	n = len(pubKey)
	cipher = 0
	i = 0
	for bit in msg_bit:
		cipher += int(bit)*pubKey[i]
		i += 1
	return bin(cipher)[2:]
```

对于破解的脚本我们直接使用 [GitHub](https://github.com/ctfs/write-ups-2014/tree/b02bcbb2737907dd0aa39c5d4df1d1e270958f54/asis-ctf-quals-2014/archaic) 上的脚本。进行一些简单的修改。

```python
import binascii
# open the public key and strip the spaces so we have a decent array
fileKey = open("pub.Key", 'rb')
pubKey = fileKey.read().replace(' ', '').replace('L', '').strip('[]').split(',')
nbit = len(pubKey)
# open the encoded message
fileEnc = open("enc.txt", 'rb')
encoded = fileEnc.read().replace('L', '')
print "start"
# create a large matrix of 0's (dimensions are public key length +1)
A = Matrix(ZZ, nbit + 1, nbit + 1)
# fill in the identity matrix
for i in xrange(nbit):
    A[i, i] = 1
# replace the bottom row with your public key
for i in xrange(nbit):
    A[i, nbit] = pubKey[i]
# last element is the encoded message
A[nbit, nbit] = -int(encoded)

res = A.LLL()
for i in range(0, nbit + 1):
    # print solution
    M = res.row(i).list()
    flag = True
    for m in M:
        if m != 0 and m != 1:
            flag = False
            break
    if flag:
        print i, M
        M = ''.join(str(j) for j in M)
        # remove the last bit
        M = M[:-1]
        M = hex(int(M, 2))[2:-1]
		print M
```

输出之后再解码下

```python
295 [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0]
415349535f3962643364356664323432323638326331393536383830366130373036316365
>>> import binascii
>>> binascii.unhexlify('415349535f3962643364356664323432323638326331393536383830366130373036316365')
'ASIS_9bd3d5fd2422682c19568806a07061ce'
```

需要注意的是，我们得到的 LLL 攻击得到的矩阵 res 的只包含 01 值的行才是我们想要的结果，因为我们对于明文加密时，会将其分解为二进制比特串。此外，我们还需要去掉对应哪一行的最后一个数字。

flag 是 `ASIS_9bd3d5fd2422682c19568806a07061ce`。



### 题目

- 2017 国赛 classic