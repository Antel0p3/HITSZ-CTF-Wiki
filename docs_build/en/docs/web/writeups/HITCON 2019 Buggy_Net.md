# [Windows]HITCON 2019 Buggy_Net
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/). 



```
    bool isBad = false;
    try {
        if ( Request.Form["filename"] != null ) {
            isBad = Request.Form["filename"].Contains("..") == true;
        }
    } catch (Exception ex) {
        
    } 

    try {
        if (!isBad) {
            Response.Write(System.IO.File.ReadAllText(@"C:\inetpub\wwwroot\" + Request.Form["filename"]));
        }
    } catch (Exception ex) {

    }
%></font></h3>
        </div>
    </div>
</body>
</html>
```

题目给出源码

抓包分析，有和平时不太一样的东西：

```
HTTP/1.1 500 Internal Server Error

Cache-Control: private

Content-Type: text/html; charset=utf-8

Server: Microsoft-IIS/10.0

X-AspNet-Version: 4.0.30319

X-Powered-By: ASP.NET

Date: Sun, 01 Aug 2021 05:04:07 GMT

Connection: close

Content-Length: 3420
```

对应使用的ASP.NET 4.0版本

```
1:
Basic idea
The basic idea of that vulnerability is that, for POST requests, request validation prevents “dangerous content” (e.g. HTML tags or similar, such as <x) in POST form fields by terminating the whole application. However, the same content in query-string fields will pass initial request validation and will “only” raise an exception on first access of Request.QueryString[...] (since that field is populated on first access?)

Similarly, for GET requests, request validation prevents “dangerous content” (e.g. HTML tags or similar, such as <x) in GET query-string fields by terminating the whole application. However, the same content in form fields (i.e. in a request body encoded as application/x-www-form-urlencoded) will pass initial request validation and will “only” raise an exception on first access of Request.Form[...] (again, since that field is populated on first access?)

Nevertheless, query-string fields in a POST request are accessbile through Request.QueryString[...] and form fields submitted in the request body of a GET request (with content-type application/x-www-form-urlencoded) are accessible through Request.Form[...].

Hence, we should be able to successfully submit the form by the sending a GET request without any query-string field but with the filename field in the request body. Further, by also including another form field in the request body that will trigger that “late” request validation bug (or is it a feature if Microsoft declared to won’t fix? 😜), e.g. a simple &o=<x, we should be able to trigger an exception on first access of Request.Form["filename"] … and this is exactly what we need to escape from the first try-catch-block before changing isBad.

https://www.sigflag.at/blog/2019/writeup-hitconctf2019-buggy-dot-net/




2:
So I started to read the .NET source code, and I found that we should use some malicious payload (e.g. XSS) to trigger the Request Validation exception.

(The function calling chain looks like: Form.get -> ValidateHttpValueCollection -> collection.EnableGranularValidation -> ValidateString -> RequestValidator.Current.IsValidRequestString -> rossSiteScriptingValidation.IsDangerousString -> throw new HttpRequestValidationException)

And it validated the Form data only once, so it will not throw any exception when we called it in the second time.
public NameValueCollection Form {
    get {
        EnsureForm();

        if (_flags[needToValidateForm]) {
            _flags.Clear(needToValidateForm);
            ValidateHttpValueCollection(_form, RequestValidationSource.Form);
        }

        return _form;
    }
}

https://balsn.tw/ctf_writeup/20191012-hitconctfquals/#buggy-.net
```

Request.Form：获取以POST方式提交的数据。

Request.QueryString：获取地址栏参数（以GET方式提交的数据）。

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

综上所述，有点像asp.net的语言特性之一，Request.From在接受到以GET形式传来的x-www-form-urlencode类型的数据时，只会报一次错，在这里相当于第一条进了exception，第二条没报错进了try读文件。

----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

因此最后的paylaod

```
GET / HTTP/1.1
Host: xxx
Connection: close
Content-Type: application/x-www-form-urlencoded
Content-Length: 
Referer: xxx

filename=../../FLAG.txt&AAA=<!
```
