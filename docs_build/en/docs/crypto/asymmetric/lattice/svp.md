# SVP
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



SVP即最短向量问题，给定lattice和基向量，找到lattice中的一个长度最短的非零向量。

对**维度较低**的lattice，目前最好的求解SVP的算法是**LLL算法**（及其变种）。

### sage实现

高斯提出的能稳定求解**2维**SVP问题的算法

```python
# sage
def GaussLatticeReduction(v1, v2):
    while True:
        if v2.norm() < v1.norm():
            v1, v2 = v2, v1
        m = round( v1*v2 / v1.norm()^2 )
        if m == 0:
            return (v1, v2)
        v2 = v2 - m*v1
        
# h = ...
# p = ...
v1 = vector(ZZ, [1, h])
v2 = vector(ZZ, [0, p])
print(GaussLatticeReduction(v1, v2)[0])
```

LLL算法

```python
# h = ...
# p = ...

# Construct lattice.
v1 = vector(ZZ, [1, h])
v2 = vector(ZZ, [0, p])
m = matrix([v1,v2]);

# Solve SVP.
shortest_vector = m.LLL()[0]
f, g = shortest_vector
print(f, g)
```
