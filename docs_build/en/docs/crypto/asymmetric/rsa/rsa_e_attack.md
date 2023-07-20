# 公钥指数相关攻击
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



## 小公钥指数攻击

### 攻击条件

e 特别小，比如 e 为 3。

### 攻击原理

假设用户使用的密钥 $e=3$。考虑到加密关系满足：

$$
c\equiv m^3 \bmod N
$$

则：

$$
\begin{align*}
m^3 &= c+k\times N\\
m &= \sqrt[3]{c+k\times n}
\end{align*}
$$

攻击者可以从小到大枚举 $k$，依次开三次根，直到开出整数为止。

### 范例

这里我们以 XMan 一期夏令营课堂练习为例进行介绍（Jarvis OJ 有复现），附件中有一个 `flag.enc` 和 `pubkey.pem`，很明显是密文和公钥了，先用 `openssl` 读一下公钥。

```bash
➜  Jarvis OJ-Extremely hard RSA git:(master) ✗ openssl rsa -pubin -in pubkey.pem -text -modulus       
Public-Key: (4096 bit)
Modulus:
    00:b0:be:e5:e3:e9:e5:a7:e8:d0:0b:49:33:55:c6:
    18:fc:8c:7d:7d:03:b8:2e:40:99:51:c1:82:f3:98:
    de:e3:10:45:80:e7:ba:70:d3:83:ae:53:11:47:56:
    56:e8:a9:64:d3:80:cb:15:7f:48:c9:51:ad:fa:65:
    db:0b:12:2c:a4:0e:42:fa:70:91:89:b7:19:a4:f0:
    d7:46:e2:f6:06:9b:af:11:ce:bd:65:0f:14:b9:3c:
    97:73:52:fd:13:b1:ee:a6:d6:e1:da:77:55:02:ab:
    ff:89:d3:a8:b3:61:5f:d0:db:49:b8:8a:97:6b:c2:
    05:68:48:92:84:e1:81:f6:f1:1e:27:08:91:c8:ef:
    80:01:7b:ad:23:8e:36:30:39:a4:58:47:0f:17:49:
    10:1b:c2:99:49:d3:a4:f4:03:8d:46:39:38:85:15:
    79:c7:52:5a:69:98:4f:15:b5:66:7f:34:20:9b:70:
    eb:26:11:36:94:7f:a1:23:e5:49:df:ff:00:60:18:
    83:af:d9:36:fe:41:1e:00:6e:4e:93:d1:a0:0b:0f:
    ea:54:1b:bf:c8:c5:18:6c:b6:22:05:03:a9:4b:24:
    13:11:0d:64:0c:77:ea:54:ba:32:20:fc:8f:4c:c6:
    ce:77:15:1e:29:b3:e0:65:78:c4:78:bd:1b:eb:e0:
    45:89:ef:9a:19:7f:6f:80:6d:b8:b3:ec:d8:26:ca:
    d2:4f:53:24:cc:de:c6:e8:fe:ad:2c:21:50:06:86:
    02:c8:dc:dc:59:40:2c:ca:c9:42:4b:79:00:48:cc:
    dd:93:27:06:80:95:ef:a0:10:b7:f1:96:c7:4b:a8:
    c3:7b:12:8f:9e:14:11:75:16:33:f7:8b:7b:9e:56:
    f7:1f:77:a1:b4:da:ad:3f:c5:4b:5e:7e:f9:35:d9:
    a7:2f:b1:76:75:97:65:52:2b:4b:bc:02:e3:14:d5:
    c0:6b:64:d5:05:4b:7b:09:6c:60:12:36:e6:cc:f4:
    5b:5e:61:1c:80:5d:33:5d:ba:b0:c3:5d:22:6c:c2:
    08:d8:ce:47:36:ba:39:a0:35:44:26:fa:e0:06:c7:
    fe:52:d5:26:7d:cf:b9:c3:88:4f:51:fd:df:df:4a:
    97:94:bc:fe:0e:15:57:11:37:49:e6:c8:ef:42:1d:
    ba:26:3a:ff:68:73:9c:e0:0e:d8:0f:d0:02:2e:f9:
    2d:34:88:f7:6d:eb:62:bd:ef:7b:ea:60:26:f2:2a:
    1d:25:aa:2a:92:d1:24:41:4a:80:21:fe:0c:17:4b:
    98:03:e6:bb:5f:ad:75:e1:86:a9:46:a1:72:80:77:
    0f:12:43:f4:38:74:46:cc:ce:b2:22:2a:96:5c:c3:
    0b:39:29
Exponent: 3 (0x3)
Modulus=B0BEE5E3E9E5A7E8D00B493355C618FC8C7D7D03B82E409951C182F398DEE3104580E7BA70D383AE5311475656E8A964D380CB157F48C951ADFA65DB0B122CA40E42FA709189B719A4F0D746E2F6069BAF11CEBD650F14B93C977352FD13B1EEA6D6E1DA775502ABFF89D3A8B3615FD0DB49B88A976BC20568489284E181F6F11E270891C8EF80017BAD238E363039A458470F1749101BC29949D3A4F4038D463938851579C7525A69984F15B5667F34209B70EB261136947FA123E549DFFF00601883AFD936FE411E006E4E93D1A00B0FEA541BBFC8C5186CB6220503A94B2413110D640C77EA54BA3220FC8F4CC6CE77151E29B3E06578C478BD1BEBE04589EF9A197F6F806DB8B3ECD826CAD24F5324CCDEC6E8FEAD2C2150068602C8DCDC59402CCAC9424B790048CCDD9327068095EFA010B7F196C74BA8C37B128F9E1411751633F78B7B9E56F71F77A1B4DAAD3FC54B5E7EF935D9A72FB176759765522B4BBC02E314D5C06B64D5054B7B096C601236E6CCF45B5E611C805D335DBAB0C35D226CC208D8CE4736BA39A0354426FAE006C7FE52D5267DCFB9C3884F51FDDFDF4A9794BCFE0E1557113749E6C8EF421DBA263AFF68739CE00ED80FD0022EF92D3488F76DEB62BDEF7BEA6026F22A1D25AA2A92D124414A8021FE0C174B9803E6BB5FAD75E186A946A17280770F1243F4387446CCCEB2222A965CC30B3929
writing RSA key
-----BEGIN PUBLIC KEY-----
MIICIDANBgkqhkiG9w0BAQEFAAOCAg0AMIICCAKCAgEAsL7l4+nlp+jQC0kzVcYY
/Ix9fQO4LkCZUcGC85je4xBFgOe6cNODrlMRR1ZW6Klk04DLFX9IyVGt+mXbCxIs
pA5C+nCRibcZpPDXRuL2BpuvEc69ZQ8UuTyXc1L9E7Huptbh2ndVAqv/idOos2Ff
0NtJuIqXa8IFaEiShOGB9vEeJwiRyO+AAXutI442MDmkWEcPF0kQG8KZSdOk9AON
Rjk4hRV5x1JaaZhPFbVmfzQgm3DrJhE2lH+hI+VJ3/8AYBiDr9k2/kEeAG5Ok9Gg
Cw/qVBu/yMUYbLYiBQOpSyQTEQ1kDHfqVLoyIPyPTMbOdxUeKbPgZXjEeL0b6+BF
ie+aGX9vgG24s+zYJsrST1MkzN7G6P6tLCFQBoYCyNzcWUAsyslCS3kASMzdkycG
gJXvoBC38ZbHS6jDexKPnhQRdRYz94t7nlb3H3ehtNqtP8VLXn75NdmnL7F2dZdl
UitLvALjFNXAa2TVBUt7CWxgEjbmzPRbXmEcgF0zXbqww10ibMII2M5HNro5oDVE
JvrgBsf+UtUmfc+5w4hPUf3f30qXlLz+DhVXETdJ5sjvQh26Jjr/aHOc4A7YD9AC
LvktNIj3betive976mAm8iodJaoqktEkQUqAIf4MF0uYA+a7X6114YapRqFygHcP
EkP0OHRGzM6yIiqWXMMLOSkCAQM=
-----END PUBLIC KEY-----
```

看到 $e=3$，很明显是小公钥指数攻击了。这里我们使用 Crypto 库来读取公钥，使用 multiprocessing 来加快破解速度。

```python
#/usr/bin/python
# coding=utf-8
import gmpy2
from Crypto.PublicKey import RSA
from multiprocessing import Pool
pool = Pool(4)

with open('./pubkey.pem', 'r') as f:
    key = RSA.importKey(f)
    N = key.n
    e = key.e
with open('flag.enc', 'r') as f:
    cipher = f.read().encode('hex')
    cipher = int(cipher, 16)


def calc(j):
    print j
    a, b = gmpy2.iroot(cipher + j * N, 3)
    if b == 1:
        m = a
        print '{:x}'.format(int(m)).decode('hex')
        pool.terminate()
        exit()


def SmallE():
    inputs = range(0, 130000000)
    pool.map(calc, inputs)
    pool.close()
    pool.join()


if __name__ == '__main__':
    print 'start'
    SmallE()
```

爆破时间有点长，，拿到 flag

```
Didn't you know RSA padding is really important? Now you see a non-padding message is so dangerous. And you should notice this in future.Fl4g: flag{Sm4ll_3xpon3nt_i5_W3ak}
```

### 题目

## RSA 衍生算法——Rabin 算法

### 攻击条件

Rabin 算法的特征在于 $e=2$。

### 攻击原理

密文：

$$
c = m^2\bmod n
$$

解密：

- 计算出 $m_p$ 和 $m_q$：

$$
\begin{align*}
m_p &= \sqrt{c} \bmod p\\
m_q &= \sqrt{c} \bmod q
\end{align*}
$$

- 用扩展欧几里得计算出 $y_p$ 和 $y_q$：

$$
y_p \cdot p + y_q \cdot q = 1
$$

- 解出四个明文：

$$
\begin{align*}
a &= (y_p \cdot p \cdot m_q + y_q \cdot q \cdot m_p) \bmod n\\
b &= n - a\\
c &= (y_p \cdot p \cdot m_q - y_q \cdot q \cdot m_p) \bmod n\\
d &= n - c
\end{align*}
$$

注意：如果 $p \equiv q \equiv 3 \pmod 4$，则

$$
\begin{align*}
m_p &= c^{\frac{1}{4}(p + 1)} \bmod p\\
m_q &= c^{\frac{1}{4}(q + 1)} \bmod q
\end{align*}
$$

而一般情况下，$p \equiv q \equiv 3 \pmod 4$ 是满足的，对于不满足的情况下，请参考相应的算法解决。

### 例子

这里我们以 XMan 一期夏令营课堂练习（Jarvis OJ 有复现）为例，读一下公钥。

```bash
➜  Jarvis OJ-hard RSA git:(master) ✗ openssl rsa -pubin -in pubkey.pem -text -modulus 
Public-Key: (256 bit)
Modulus:
    00:c2:63:6a:e5:c3:d8:e4:3f:fb:97:ab:09:02:8f:
    1a:ac:6c:0b:f6:cd:3d:70:eb:ca:28:1b:ff:e9:7f:
    be:30:dd
Exponent: 2 (0x2)
Modulus=C2636AE5C3D8E43FFB97AB09028F1AAC6C0BF6CD3D70EBCA281BFFE97FBE30DD
writing RSA key
-----BEGIN PUBLIC KEY-----
MDowDQYJKoZIhvcNAQEBBQADKQAwJgIhAMJjauXD2OQ/+5erCQKPGqxsC/bNPXDr
yigb/+l/vjDdAgEC
-----END PUBLIC KEY-----
```

$e=2$，考虑 Rabin 算法。首先我们先分解一下 p 和 q，得到

```text
p=275127860351348928173285174381581152299
q=319576316814478949870590164193048041239
```

编写代码

```python
#!/usr/bin/python
# coding=utf-8
import gmpy2
import string
from Crypto.PublicKey import RSA

# 读取公钥参数
with open('pubkey.pem', 'r') as f:
    key = RSA.importKey(f)
    N = key.n
    e = key.e
with open('flag.enc', 'r') as f:
    cipher = f.read().encode('hex')
    cipher = string.atoi(cipher, base=16)
    # print cipher
print "please input p"
p = int(raw_input(), 10)
print 'please input q'
q = int(raw_input(), 10)
# 计算yp和yq
inv_p = gmpy2.invert(p, q)
inv_q = gmpy2.invert(q, p)

# 计算mp和mq
mp = pow(cipher, (p + 1) / 4, p)
mq = pow(cipher, (q + 1) / 4, q)

# 计算a,b,c,d
a = (inv_p * p * mq + inv_q * q * mp) % N
b = N - int(a)
c = (inv_p * p * mq - inv_q * q * mp) % N
d = N - int(c)

for i in (a, b, c, d):
    s = '%x' % i
    if len(s) % 2 != 0:
        s = '0' + s
    print s.decode('hex')
```

拿到 flag，`PCTF{sp3ci4l_rsa}`。



## Tonelli–Shanks算法

`e=2`，`n`是素数

TS算法是用于求解二次方根的

也可以用`sympy`自带的方法

```python
from sympy.ntheory.residue_ntheory import nthroot_mod
# nthroot_mod(a,n,p) Find the solutions to x**n = a mod p
m = nthroot_mod(c,2,r)
print(m)
```

真正的TS算法

```python
import gmpy2
from Crypto.Util.number import *
def legendre(a, p):
    return pow(a, (p - 1) // 2, p)

def tonelli(n, p):
    assert legendre(n, p) == 1
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1
    if s == 1:
        return pow(n, (p + 1) // 4, p)
    for z in range(2, 10000):
	#for z in range(2, p):
        if p - 1 == legendre(z, p):
            break
    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    m = s
    t2 = 0
    while (t - 1) % p != 0:
        t2 = (t * t) % p
        for i in range(1, m):
            if (t2 - 1) % p == 0:
                break
            t2 = (t2 * t2) % p
        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        c = (b * b) % p
        t = (t * c) % p
        m = i
    return r
n=7941371739956577280160664419383740967516918938781306610817149744988379280561359039016508679365806108722198157199058807892703837558280678711420411242914059658055366348123106473335186505617418956630780649894945233345985279471106888635177256011468979083320605103256178446993230320443790240285158260236926519042413378204298514714890725325831769281505530787739922007367026883959544239568886349070557272869042275528961483412544495589811933856131557221673534170105409
d=gmpy2.mpz(7515987842794170949444517202158067021118454558360145030399453487603693522695746732547224100845570119375977629070702308991221388721952258969752305904378724402002545947182529859604584400048983091861594720299791743887521228492714135449584003054386457751933095902983841246048952155097668245322664318518861440)
cipher=1618155233923718966393124032999431934705026408748451436388483012584983753140040289666712916510617403356206112730613485227084128314043665913357106301736817062412927135716281544348612150328867226515184078966397180771624148797528036548243343316501503364783092550480439749404301122277056732857399413805293899249313045684662146333448668209567898831091274930053147799756622844119463942087160062353526056879436998061803187343431081504474584816590199768034450005448200

#python2 -m primefac -vs -m=p+1  7941371739956577280160664419383740967516918938781306610817149744988379280561359039016508679365806108722198157199058807892703837558280678711420411242914059658055366348123106473335186505617418956630780649894945233345985279471106888635177256011468979083320605103256178446993230320443790240285158260236926519042413378204298514714890725325831769281505530787739922007367026883959544239568886349070557272869042275528961483412544495589811933856131557221673534170105409
p=gmpy2.mpz(102634610559478918970860957918259981057327949366949344137104804864768237961662136189827166317524151288799657758536256924609797810164397005081733039415393)

q2=gmpy2.invert(d,p**2)
for i in range(1000000):
	q=gmpy2.iroot(q2+i*p**2,2)
	if(q[1]==1):
		print q[0],i
		break
q=q[0]
r=n//p//q

e=0x10001
phi=(p-1)*(q-1)*(r-1)
D=gmpy2.invert(e,phi)
c=pow(cipher,D,n)
print c

m=tonelli(c,r)
print m
print long_to_bytes(m)
#flag{fd462593-25e4-4631-a96a-0cd5c72b2d1b}
```



## $e, \phi(n)$不互素时

### sympy库直接开根号

`sympy.nthroot_mod(c, e, n)`

适用于e较小时



### $e/\gcd(e, \phi(n))$

适用于e较小，且$e/\gcd(e, \phi(n))$和$\phi(n)$互素时

```python
def invalidExponent(p,q,e,c):
    phiN = (p - 1) * (q - 1)
    n = p * q
    GCD = gcd(e, phiN)
    if (GCD == 1):
        return "Public exponent is valid....."
    d = invert(e//GCD,phiN)
    c = powmod(c, d, n)
    plaintext = sympy.root(c, GCD)
    plaintext = n2s(plaintext)
    return plaintext
```



### AMM 算法

AMM算法用于在有限域内开根，常用于**$e, \phi(n)$不互质**的情况。

$e, \phi(n)$不互质时有解，且不止有一个解。

### 例题 NCTF2019 easyRSA

![image-20191118155729801](https://i.loli.net/2020/04/18/5eGxTEdK67JBWz9.png)

题面十分简洁，甚至都给出了`p, q`。乍一看，肯定觉得这是一道**送分题**，然而事实远非如此。

------

正常情况下的RSA都要求`e`和`phi(n)`要互素，不过也有一些`e`和`phi(n)`有很小的公约数的题目，这些题目基本都能通过计算`e`对`phi(n)`的逆元`d`来求解。

然而本题则为`e`和`p-1`(或`q-1`)的最大公约数就是`e`本身，也就是说`e | p-1`，只有对`c`开`e`次方根才行。
可以将同余方程

$$
m^e \equiv c \quad (\text{mod}\ n)
$$

化成

$$
\begin{aligned}
m^e &\equiv c \quad (\text{mod}\ p)\newline
m^e &\equiv c \quad (\text{mod}\ q)
\end{aligned}
$$

然后分别在`GF(p)`和`GF(q)`上对`c`开`e=0x1337`次方根，再用`CRT`组合一下即可得到在`mod n`下的解。

#### EXP

- 先用`Adleman-Manders-Miller rth Root Extraction Method`在`GF(p)`和`GF(q)`上对`c`开`e`次根，分别得到一个解。大概不到10秒。
- 然后去找到所有的`0x1336`个`primitive nth root of 1`，乘以上面那个解，得到所有的`0x1337`个解。大概1分钟。
- 再用`CRT`对`GF(p)`和`GF(q)`上的两组`0x1337`个解组合成`mod n`下的解，可以得到`0x1337**2==24196561`个`mod n`的解。最后能通过`check`的即为`flag`。大概十几分钟。

`exp.sage`如下，需要十几分钟：

已修改成python3版本，在别的题目使用时需要修改RSA相关数据以及`check`函数

```python
import random
import time

# About 3 seconds to run
def AMM(o, r, q):
    start = time.time()
    print('\n----------------------------------------------------------------------------------')
    print('Start to run Adleman-Manders-Miller Root Extraction Method')
    print('Try to find one {:#x}th root of {} modulo {}'.format(r, o, q))
    g = GF(q)
    o = g(o)
    p = g(random.randint(1, q))
    while p ^ ((q-1) // r) == 1:
        p = g(random.randint(1, q))
    print('[+] Find p:{}'.format(p))
    t = 0
    s = q - 1
    while s % r == 0:
        t += 1
        s = s // r
    print('[+] Find s:{}, t:{}'.format(s, t))
    k = 1
    while (k * s + 1) % r != 0:
        k += 1
    alp = (k * s + 1) // r
    print('[+] Find alp:{}'.format(alp))
    a = p ^ (r**(t-1) * s)
    b = o ^ (r*alp - 1)
    c = p ^ s
    h = 1
    for i in range(1, t):
        d = b ^ (r^(t-1-i))
        if d == 1:
            j = 0
        else:
            print('[+] Calculating DLP...')
            j = - dicreat_log(a, d)
            print('[+] Finish DLP...')
        b = b * (c^r)^j
        h = h * c^j
        c = c ^ r
    result = o^alp * h
    end = time.time()
    print("Finished in {} seconds.".format(end - start))
    print('Find one solution: {}'.format(result))
    return result

def findAllPRoot(p, e):
    print("Start to find all the Primitive {:#x}th root of 1 modulo {}.".format(e, p))
    start = time.time()
    proot = set()
    while len(proot) < e:
        proot.add(pow(random.randint(2, p-1), (p-1)//e, p))
    end = time.time()
    print("Finished in {} seconds.".format(end - start))
    return proot

def findAllSolutions(mp, proot, cp, p):
    print("Start to find all the {:#x}th root of {} modulo {}.".format(e, cp, p))
    start = time.time()
    all_mp = set()
    for root in proot:
        mp2 = mp * root % p
        assert(pow(mp2, e, p) == cp)
        all_mp.add(mp2)
    end = time.time()
    print("Finished in {} seconds.".format(end - start))
    return all_mp


c = 10562302690541901187975815594605242014385201583329309191736952454310803387032252007244962585846519762051885640856082157060593829013572592812958261432327975138581784360302599265408134332094134880789013207382277849503344042487389850373487656200657856862096900860792273206447552132458430989534820256156021128891296387414689693952047302604774923411425863612316726417214819110981605912408620996068520823370069362751149060142640529571400977787330956486849449005402750224992048562898004309319577192693315658275912449198365737965570035264841782399978307388920681068646219895287752359564029778568376881425070363592696751183359
e = 0x1337
p = 199138677823743837339927520157607820029746574557746549094921488292877226509198315016018919385259781238148402833316033634968163276198999279327827901879426429664674358844084491830543271625147280950273934405879341438429171453002453838897458102128836690385604150324972907981960626767679153125735677417397078196059
q = 112213695905472142415221444515326532320352429478341683352811183503269676555434601229013679319423878238944956830244386653674413411658696751173844443394608246716053086226910581400528167848306119179879115809778793093611381764939789057524575349501163689452810148280625226541609383166347879832134495444706697124741

cp = c % p
cq = c % q
mp = AMM(cp, e, p)
mq = AMM(cq, e, q)
p_proot = findAllPRoot(p, e)
q_proot = findAllPRoot(q, e)
mps = findAllSolutions(mp, p_proot, cp, p)
mqs = findAllSolutions(mq, q_proot, cq, q)
print(mps, mqs)

def check(m):
    h = m.hex()
    if len(h) & 1:
        return False
    try:
        tmp = bytearray.fromhex(h).decode('utf-8')
    except:
        return False
    if tmp.startswith('NCTF'):
        print(tmp)
        return True
    else:
        return False


# About 16 mins to run 0x1337^2 == 24196561 times CRT
start = time.time()
print('Start CRT...')
for mpp in mps:
    for mqq in mqs:
        solution = CRT_list([int(mpp), int(mqq)], [p, q])
        if check(solution):
            print(solution)
            exit(0)
    print(time.time() - start)

end = time.time()
print("Finished in {} seconds.".format(end - start))
```
