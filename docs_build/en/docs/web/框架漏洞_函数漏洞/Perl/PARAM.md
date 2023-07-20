# PARAM
!!! warning
    The current page still doesn't have a translation for this language.

    You can read it through google translate.

    Besides, you can also help to translate it: [Contributing](https://ctf-wiki.org/en/contribute/before-contributing/).



## csaw-ctf-2016-quals i-got-id-200





my $file_name =param($field_name);





获取上传的文件名 后者post或者get的数据.





param()函数会返回一个列表的文件但是只有第一个文件会被放入到下面的接收变量中。如果我们传入一个ARGV的文件，那么Perl会将传入的参数作为文件名读出来。对正常的上传文件进行修改,可以达到读取任意文件的目的





ARGV(相当于本题目的接受变量的数组，这个数组里面的内容作为命令行可以执行，相当于是param()接受get到的参数并且放在ARGV中，然后ARFV中默认就默认调用执行)





perl将perl命令行的参数列表放进数组ARGV(@ARGV)中。既然是数组，就可以访问($ARGV[n])、遍历，甚至修改数组元素



