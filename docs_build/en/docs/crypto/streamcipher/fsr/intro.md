# 反馈移位寄存器
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



一般的，一个 n 级反馈移位寄存器如下图所示

![image-20180712201048987](./figure/n-fsr.png)

其中

- $a_0$，$a_1$，…，$a_{n-1}$，为初态。
- F 为反馈函数或者反馈逻辑。如果 F 为线性函数，那么我们称其为线性反馈移位寄存器（LFSR），否则我们称其为非线性反馈移位寄存器（NFSR）。
- $a_{i+n}=F(a_i,a_{i+1},...,a_{i+n-1})$ 。

一般来说，反馈移位寄存器都会定义在某个有限域上，从而避免数字太大和太小的问题。因此，我们可以将其视为同一个空间中的变换，即

$(a_i,a_{i+1},...,a_{i+n-1}) \rightarrow (a_{i+1},...,a_{i+n-1},a_{i+n})$
.
对于一个序列来说，我们一般定义其生成函数为其序列对应的幂级数的和。