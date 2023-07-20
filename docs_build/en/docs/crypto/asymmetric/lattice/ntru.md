# NTRU
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).


## NTRU的低端版本

首先声明，这个密码体系不安全，但是作为NTRU的低端版本，会有相关题目

### 密钥生成

Alice选择一个大整数 $p$，然后随机选择两个较小的整数 $f,g$，

$$
f < \sqrt{\dfrac p2}\\
\sqrt{\frac p4}<g<\sqrt{\frac p2}\\
\gcd(f,p)=1\\
\gcd(f,g)=1
$$

接着，Alice计算

$$
h = (f)^{-1}_{\mathrm{mod}~p}g \mod p
$$

得到公钥 $h$，私钥 $(f, g)$.

### 加密

要求明文 $m<\sqrt{\dfrac p4}$，Bob随机选择 $r < \sqrt{\dfrac p2}$，

Bob给Alice发送的密文为

$$
c=(rh + m) \mod p
$$


### 解密

Alice先计算

$$
a = fc \mod p
$$

然后计算

$$
m = (f)^{-1}_{\mathrm{mod}~g}a \mod g
$$


### 正确性

首先

$$
a \equiv fc \equiv f(rh+m) \equiv rg+fm \mod p
$$

前面整数的选取都有范围限制，可以发现

$$
rg+fm < \sqrt \frac p2 \sqrt \frac p2 + \sqrt \frac p2 \sqrt \frac p4 < p
$$

所以 $a=rg+fm$

到这一步就能看出，

$$
m = (f)^{-1}_{\mathrm{mod}~g}a \mod g
$$


### 攻击

只要我们知道私钥 $(f,g)$ 就能解密，而唯一知道的关于 $f, g$ 的关系式就是

$$
h \equiv (f)^{-1}_{\mathrm{mod}~p}g \mod p
$$

从中如何求出 $f, g$ ？这里就要用到格的相关知识了，可以把这个问题**转化为SVP问题**.

由

$$
fh \equiv g \mod p
$$

可以得到

$$
fh=g+u\cdot p \quad (u \in \mathbb{Z}) \\
fh-up=g
$$

构造一个由$(1,h), (0,p)$张成的格，令

$$
M=  \begin{pmatrix}
	1&h\\
	0&p
    \end{pmatrix}
$$

可以发现

$$
\begin{align}
&(f, -u)M\\
=&(f,-u)\begin{pmatrix}
        1&h\\
        0&p
        \end{pmatrix}\\
=&(f,fh-up)\\
=&(f,g)
\end{align}
$$

$(f,g)$ 可以由两组基向量$M$的线性组合$(f,-u)$来表示，即 $(f,g)$ **在这个格上**.

再看看刚才的范围限制，$f,g \lt \sqrt{\dfrac p2}$，求 $f,g$ 的问题转化为找到合适的系数，使得$(1,h),(0,p)$ 组合出来的向量**足够短**. 实际上，分析各个数据的位数后可以发现，很大概率上 $(f,g)$ 就是这个格上的**最短向量**. 位数只有2维，因此我们利用Gauss的算法或LLL算法就可以求解.

---

参考

https://xz.aliyun.com/t/7163

https://www.ruanx.net/lattice-1/



### 例题 [2021 MAR DASCTF明御攻防赛]son_of_NTRU

```python
#! /bin/bash/env python3
from random import randrange
from Crypto.Util.number import *
from gmpy2 import invert
def gcd(a,b):
    while b:
        a,b = b,a%b
    return a

def generate():
    p = getPrime(1024)
    while True:
        f = randrange(1,(p//2)**(0.5))
        g = randrange((p//4)**(0.5),(p//2)**(0.5))
        if gcd(f,p)==1 and gcd(f,g)==1:
            break
    h = (invert(f,p)*g)%p
    return h,p,f,g

def encrypt(m,h,p):
    assert m<(p//4)**(0.5)
    r = randrange(1,(p//2)**(0.5))
    c = (r*h+m)%p
    return c

h,p,f,g = generate()

from flag import flag
c = encrypt(bytes_to_long(flag),h,p)
print("h = {}".format(h))
print("p = {}".format(p))
print("c = {}".format(c))
# h = 70851272226599856513658616506718804769182611213413854493145253337330709939355936692154199813179587933065165812259913249917314725765898812249062834111179900151466610356207921771928832591335738750053453046857602342378475278876652263044722419918958361163645152112020971804267503129035439011008349349624213734004
# p = 125796773654949906956757901514929172896506715196511121353157781851652093811702246079116208920427110231653664239838444378725001877052652056537732732266407477191221775698956008368755461680533430353707546171814962217736494341129233572423073286387554056407408816555382448824610216634458550949715062229816683685469
# c = 4691517945653877981376957637565364382959972087952249273292897076221178958350355396910942555879426136128610896883898318646711419768716904972164508407035668258209226498292327845169861395205212789741065517685193351416871631112431257858097798333893494180621728198734264288028849543413123321402664789239712408700
```

#### EXP

```python
#sage
def GaussLatticeReduction(v1, v2):
    while True:
        if v2.norm() < v1.norm():
            v1, v2 = v2, v1
        m = round( v1*v2 / v1.norm()^2 )
        if m == 0:
            return (v1, v2)
        v2 = v2 - m*v1

h = 70851272226599856513658616506718804769182611213413854493145253337330709939355936692154199813179587933065165812259913249917314725765898812249062834111179900151466610356207921771928832591335738750053453046857602342378475278876652263044722419918958361163645152112020971804267503129035439011008349349624213734004
p = 125796773654949906956757901514929172896506715196511121353157781851652093811702246079116208920427110231653664239838444378725001877052652056537732732266407477191221775698956008368755461680533430353707546171814962217736494341129233572423073286387554056407408816555382448824610216634458550949715062229816683685469
c = 4691517945653877981376957637565364382959972087952249273292897076221178958350355396910942555879426136128610896883898318646711419768716904972164508407035668258209226498292327845169861395205212789741065517685193351416871631112431257858097798333893494180621728198734264288028849543413123321402664789239712408700

# Construct lattice.
v1 = vector(ZZ, [1, h])
v2 = vector(ZZ, [0, p])
m = matrix([v1,v2])

# Solve SVP.
shortest_vector = m.LLL()[0]
# shortest_vector = GaussLatticeReduction(v1, v2)[0]
f, g = shortest_vector

f = abs(f)
g = abs(g)

print("f =", f)
print("g =", g)
print("-"*30)
# Decrypt.
a = f*c % p % g
m = (a * inverse_mod(f, g)) % g
print(bytes.fromhex(hex(m)[2:]))
```



## NTRU

!!! info
    待补充