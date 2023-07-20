# md5截断爆破
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



```plain
就是说给出md5后前多少位数字，求原数字
脚本如下
from multiprocessing.dummy import Pool as tp
import hashlib

knownMd5 = 'af53d'      #已知的md5明文
def md5(text):
    return hashlib.md5(str(text).encode('utf-8')).hexdigest()

def findCode(code):
    key = code.split(':')
    start = int(key[0])
    end = int(key[1])
    for code in range(start, end):
        if md5(code)[0:5] == knownMd5:
            print(code)
            break
list=[]
for i in range(3):    #这里的range(number)指爆破出多少结果停止
    list.append(str(10000000*i) + ':' + str(10000000*(i+1)))
pool = tp()    #使用多线程加快爆破速度
pool.map(findCode, list)
pool.close()
pool.join()
```




