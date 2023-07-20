# LCG相关问题

LCG 即线性同余发生器，是一种简单的随机数生成算法，公式如下：

$$
s_{i+1} = (as_i+b) \mod m
$$

利用 LLL 算法可以求解 truncated LCG 问题，即已知若干连续状态的值的高位，求出 seed 并预测其他状态.

其余 LLL 算法在 LCG 上的应用参考 https://0xdktb.top/2020/03/27/Summary-of-Crypto-in-CTF-PRNG/

以下题为例说明

### 例题 [NPUCTF2020]babyLCG

BUUCTF 上可以下载原题

题目源码（附件中给出ct, key, old）

```python
from Crypto.Util.number import *
from Crypto.Cipher import AES
from secret import flag

class LCG:
    def __init__(self, bit_length):
        m = getPrime(bit_length)
        a = getRandomRange(2, m)
        b = getRandomRange(2, m)
        seed = getRandomRange(2, m)
        self._key = {'a':a, 'b':b, 'm':m}
        self._state = seed
        
    def next(self):
        self._state = (self._key['a'] * self._state + self._key['b']) % self._key['m']
        return self._state
    
    def export_key(self):
        return self._key


def gen_lcg():
    rand_iter = LCG(128)
    key = rand_iter.export_key()
    f = open("key", "w")
    f.write(str(key))
    return rand_iter


def leak_data(rand_iter):
    f = open("old", "w")
    for i in range(20):
        f.write(str(rand_iter.next() >> 64) + "\n")
    return rand_iter


def encrypt(rand_iter):
    f = open("ct", "wb")
    key = rand_iter.next() >> 64
    key = (key << 64) + (rand_iter.next() >> 64)
    key = long_to_bytes(key).ljust(16, b'\x00')
    iv = long_to_bytes(rand_iter.next()).ljust(16, b'\x00')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = flag + (16 - len(flag) % 16) * chr(16 - len(flag) % 16)
    ct = cipher.encrypt(pt.encode())
    f.write(ct)


def main():
    rand_iter = gen_lcg()
    rand_iter = leak_data(rand_iter)
    encrypt(rand_iter)


if __name__ == "__main__":
    main()
```

#### 分析

一个普通的 LCG，但是我们不知道`seed`，只知道前20个状态的高64位，要预测后面的几个数.

设生成的128位状态为 $x_i$，高64位为 $y_i$ （已知），低64位为 $z_i$，则

$$
x_i = y_i \times 2^{64} + z_i \\
x_{i+1} - x_i = a^i(x_1 - x_0) \mod m
$$

令

$$
\begin{aligned}
deltaX &= [x_1 - x_0, \dots, x_n - x_{n-1}]^T\\
deltaY &= [2^{64}(y_1 - y_0), \dots, 2^{64}(y_n - y_{n-1})]^T \\
deltaZ &= [z_1 - z_0, \dots, z_{n} - z_{n-1}]
\end{aligned}
$$

构造矩阵$A$如下

$$
A = \left[
\begin{matrix}
m & 0 & 0 & ... & 0\\
a & -1 & 0 & ... & 0\\
a^{2} & 0 & -1 & ... & 0\\
... & ... & ... & ... & ...\\
a^{n} & 0 & 0 & ... & -1
\end{matrix}
\right]
$$

不难验证，$A \cdot deltaX=0 \mod m$

设 $AL = A.LLL()$，有

$$
AL \cdot deltaX = 0 \mod m
$$

不妨设 $AL \cdot deltaX = m \cdot [k_0, k_1, \dots, k_{n-1}]^T = AL \cdot (deltaY + deltaZ)$

$AL$ 是格基规约的结果，其中的向量都比较短，因此 $k$ 中的元素也较小.

接下来对大小进行粗略的计算，$deltaX, deltaY$ 中的元素都是128位的，$deltaZ$ 中的元素是64位的.

粗略估计$AL$ 中的元素大小是$\det(AL) ^ {1/n}=m^{1/n}$，注意 $n$ 是矩阵 $A$ 的行数减1.

则 $AL \cdot deltaZ$ 中的元素大小大约是

$$
\sum_{i=0}^{n}m^{1/n} \cdot 2^{64}=n\cdot m^{1/n} \cdot 2^{64}
$$

这里的 $n$ 是我们自己可以取的，已知20个状态，所以 $n \le 20$.

显然上式小于 $m$，即 $deltaZ$ 中的元素小于 $m$.

因此有

$$
k_i=\lfloor\dfrac 1m \cdot AL \cdot(deltaY_i+deltaZ_i)\rfloor=\lfloor\dfrac 1m \cdot AL \cdot deltaY_i \rfloor
$$

那我们就能通过 $deltaY$ 求出 $k$，从而得到 $deltaZ$ 和 $deltaX$，最后求出所有状态.

#### EXP

```python
# sage
from Crypto.Util.number import *
from Crypto.Cipher import AES

b = 153582801876235638173762045261195852087
a = 107763262682494809191803026213015101802
m = 226649634126248141841388712969771891297

class LCG:
    def __init__(self, seed, a, b, m):
        self.a = a
        self.b = b
        self.m = m
        self._state = seed
        
    def next(self):
        self._state = (self.a * self._state + self.b) % self.m
        return self._state

with open("../old", "r") as f:
    y = f.readlines()
y = list(map(int, y))
# print(y)

A = matrix(ZZ, 10, 10)
A[0, 0] = m
for i in range(1, 10):
    A[i, 0] = a ^ i
    A[i, i] = -1
AL = A.LLL()

delta_y = vector([(y[i+1] - y[i]) << 64 for i in range(10)])
k0 = AL * delta_y
# print(k0)
k = vector([round(RR(ki) / m) for ki in k0])
delta_z = AL.solve_right(m * k - k0)
# print(delta_z)

delta_x = delta_y + delta_z
# x1 = (a * x0 + b) % m
# delta_x[0] = x1 - x0 = ((a - 1) * x0 + b) % m
# x0 = ((delta_x[0] - b) / (a - 1)) % m
x0 = (((delta_x[0] - b) % m) * inverse_mod(a - 1, m)) % m

lcg = LCG(x0, a, b, m)
for i in range(20):
    key = lcg.next() >> 64
key = (key << 64) + (lcg.next() >> 64)
key = long_to_bytes(key).ljust(16, b'\x00')
iv = long_to_bytes(lcg.next()).ljust(16, b'\x00')
aes = AES.new(key, AES.MODE_CBC, iv)
with open("../ct", "rb") as f:
    ct = f.read()
print(aes.decrypt(ct))
```

