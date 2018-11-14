# ctf
in_array()函数
来检测上传的文件名，未将第三个参数设置为 true时可以通过构造的文件名来绕过服务端的检测，例如文件名为 7shell.php。因为PHP在使用 in_array()函数判断时，会将 7shell.php强制转换成数字7，而数字7在 range(1,24)数组中，最终绕过 in_array()函数判断，导致任意文件上传漏洞。
in_array：(PHP 4, PHP 5, PHP 7)
功能：检查数组中是否存在某个值
定义： bool in_array ( mixed $needle , array $haystack [, bool $strict = FALSE ] )
在 $haystack中搜索 $needle，如果第三个参数 $strict的值为 TRUE，则 in_array()函数会进行强检查，检查 $needle的类型是否和 $haystack中的相同。如果找到 $haystack，则返回 TRUE，否则返回 FALSE。
