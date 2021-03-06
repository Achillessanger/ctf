## XCTF crypto x_xor_md5

**这道题总体而言没什么意思，但是锻炼了python写代码能力**

拿到文件，用winhex打开，发现是一串数字，根据题目的意思猜测是异或，发现后面的数字有一串是一样的！！
![img](http://img.wandouip.com/crawler/article/201967/dc9e9e3599ba95a43bf9384738f64d8b)
把这一串16进制的数字copy下来，与每一行进行异或得到：

```python
num = ['68', '4d', '4d', '4d', '0c', '00', '47', '4f', '4f', '44', '00', '4a', '4f', '42', '0c', '2a', 
'54', '48', '45', '00', '46', '4c', '41', '47', '00', '49', '53', '00', '4e', '4f', '54', '00', 
'72', '63', '74', '66', '5b', '77', '45', '11', '4c', '7f', '44', '10', '4e', '13', '7f', '3c', 
'55', '54', '7f', '57', '48', '14', '54', '7f', '49', '15', '7f', '0a', '4b', '45', '59', '20', 
'5d', '2a', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '72', '6f', '69', '73']
```

再转化为ASCII码，发现思路没错，出现rctf字样：
![img](http://img.wandouip.com/crawler/article/201967/4bf6318efd7c4526d2e33d335b204567)
接着，发现异或完的数字有许多是0x00隔开的，猜测是不是空格，，英文使用空格（0x20）来分隔每一单词,空格是0x20，如果0x00是空格的话，那么就是0x00^0x20，
整体数据都异或0x20得到：

```python
num2 = ['48', '6d', '6d', '6d', '2c', '20', '67', '6f', '6f', '64', '20', '6a', '6f', '62', '2c', '0a', 
'74', '68', '65', '20', '66', '6c', '61', '67', '20', '69', '73', '20', '6e', '6f', '74', '20', 
'52', '43', '54', '46', '7b', '57', '65', '31', '6c', '5f', '64', '30', '6e', '33', '5f', '36', 
'75', '74', '5f', '77', '68', '34', '74', '5f', '69', '35', '5f', '2a', '6b', '65', '79', '2a', 
'7d', '0a', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '52', '4f', '49', '53']
```

转化成字符串形式得到：
![img](http://img.wandouip.com/crawler/article/201967/e1d4f979b57fee4dfd143de0a7655cd1)
看这情况八九不离十是正确的思路，，，，，
突然发现有些地方字符不对劲，，
*key后面是个空格，还有ut前面，猜测key被两个`\*`包括，即`*key*`，所以就是`0x00^0x2a`,所以不对劲的地方`1c^2a`得到36，所以正确的列表如下:

```python
num2 = ['48', '6d', '6d', '6d', '2c', '20', '67', '6f', '6f', '64', '20', '6a', '6f', '62', '2c', '0a', 
'74', '68', '65', '20', '66', '6c', '61', '67', '20', '69', '73', '20', '6e', '6f', '74', '20', 
'52', '43', '54', '46', '7b', '57', '65', '31', '6c', '5f', '64', '30', '6e', '33', '5f', '36', 
'75', '74', '5f', '77', '68', '34', '74', '5f', '69', '35', '5f', '2a', '6b', '65', '79', '2a', 
'7d', '0a', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '52', '4f', '49', '53']
```

转化成字符串形式得到：
![img](http://img.wandouip.com/crawler/article/201967/f32f4d6fc2141e54b7f21c54b79cc6f2)
嗯，差不多就是这样了，，，
提交，不对，，，，，，，，，，，，，
回头看题目提示，说有MD5值，我们异或的就是MD5值吧，32位，刚刚好（MD5是16位或者32位的密文）
编写脚本：

```python
m = ['01','78','0C','4C','10','9E','32','37','12','0C','FB','BA','CB','8F','6A','53']
zz = []
for i in range(0,len(m)):
	x = int(m[i],16)
	zz.append(hex(x^32)[2:])
print(zz)
```

得到：`['21', '58', '2c', '6c', '30', 'be', '12', '17', '32', '2c', 'db', '9a', 'eb', ' af', '4a', '73']`

经过解码得到`that`
把`*key*`替换成that
也就是提交`RCTF{We1l_d0n3_6ut_wh4t_i5_that}`，Right！！！！！

最后把做题的整个脚本贴上，有兴趣就看一看，可能有些冗余！！
整体脚本：

```python
n = ['69','35','41','01','1C','9E','75','78','5D','48','FB','F0','84','CD','66','79',
'55','30','49','4C','56','D2','73','70','12','45','A8','BA','85','C0','3E','53',
'73','1B','78','2A','4B','E9','77','26','5E','73','BF','AA','85','9C','15','6F',
'54','2C','73','1B','58','8A','66','48','5B','19','84','B0','80','CA','33','73',
'5C','52','0C','4C','10','9E','32','37','12','0C','FB','BA','CB','8F','6A','53',
'01','78','0C','4C','10','9E','32','37','12','0C','FB','BA','CB','8F','6A','53',
'01','78','0C','4C','10','9E','32','37','12','0C','FB','BA','CB','8F','6A','53',
'01','78','0C','4C','10','9E','32','37','12','0C','89','D5','A2','FC']

m = ['01','78','0C','4C','10','9E','32','37','12','0C','FB','BA','CB','8F','6A','53']
j = 0
s = ""
num = []
for i in range(0,len(n)):
	x = int(n[i],16)
	if j >= 16:
		j = 0 
	y = int(m[j],16)
	j += 1
	num.append(hex(x^y)[2:])
	s += chr(x^y)
print(num)
print(s)

num = ['68', '4d', '4d', '4d', '0c', '00', '47', '4f', '4f', '44', '00', '4a', '4f', '42', '0c', '2a', 
'54', '48', '45', '00', '46', '4c', '41', '47', '00', '49', '53', '00', '4e', '4f', '54', '00', 
'72', '63', '74', '66', '5b', '77', '45', '11', '4c', '7f', '44', '10', '4e', '13', '7f', '3c', 
'55', '54', '7f', '57', '48', '14', '54', '7f', '49', '15', '7f', '0a', '4b', '45', '59', '20', 
'5d', '2a', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '00', 
'00', '00', '00', '00', '00', '00', '00', '00', '00', '00', '72', '6f', '69', '73']

ss = ""
num2 = []
for i in range(0,len(num)):
	x = int(num[i],16)
	num2.append(hex(x^32)[2:])
	ss += chr(x^32)
    #32是0x20的十进制表达
print(num2)
print(ss)

#查看字符串，发现有个不对劲的地方，猜测key被两个*包括，即*key*，所以就是00^2a,所以不对劲的地方1c^2a得到36，所以正确的列表如下

num2 = ['48', '6d', '6d', '6d', '2c', '20', '67', '6f', '6f', '64', '20', '6a', '6f', '62', '2c', '0a', 
'74', '68', '65', '20', '66', '6c', '61', '67', '20', '69', '73', '20', '6e', '6f', '74', '20', 
'52', '43', '54', '46', '7b', '57', '65', '31', '6c', '5f', '64', '30', '6e', '33', '5f', '36', 
'75', '74', '5f', '77', '68', '34', '74', '5f', '69', '35', '5f', '2a', '6b', '65', '79', '2a', 
'7d', '0a', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '20', 
'20', '20', '20', '20', '20', '20', '20', '20', '20', '20', '52', '4f', '49', '53']

xx = ""
for i in range(0,len(num2)):
	xx += chr(int(num2[i],16))
print(xx) 

zz = []
for i in range(0,len(m)):
	x = int(m[i],16)
	zz.append(hex(x^32)[2:])
print(zz)
```

#### MD5算法
MD5算法步骤编辑
* 附加填充位
　　首先对输入的报文进行填位补充,使填充后的数据长度模512后余448.如果数据长度正好模512余448,则需增加512个填充位,也就是说填充的个数为1~512位.填充位第一个位为1,其余全部为0.
* 补足长度
将数据长度表示为二进制,如果长度超过64位,则截取其低64位;如果长度不足64位,则在其高位补0.将这个64位的报文长度补在经过填充的报文后面,使得最后的数据为512位的整数倍.
* 初始化MD缓存器
MD5运算要用到一个128位的MD5缓存器,用来保存中间变量和最终结果.该缓存器又可看成是4个32位的寄存器A、B、C、D,初始化为:
A ： 01 23 45 67
B： 89 ab cd ef
C： fe dc ba 98
D： 76 54 32 10
* 处理数据段
首先定义4个非线性函数F、G、H、I,对输入的报文运算以512位数据段为单位进行处理.对每个数据段都要进行4轮的逻辑处理,在4轮中分别使用4个不同的函数F、G、H、I.每一轮以ABCD和当前的512位的块为输入,处理后送入ABCD(128位)

### 法二 用工具
winhex打开

发现`01780C4C109E3237120CFBBACB8F6A53`字符有两段重复，结合题目
首先看看XOR的运算规则：
```txt
1 XOR 0 = 1
0 XOR 1 = 1
0 XOR 0 = 0
1 XOR 1 = 0 
```
注意到下面的规律：

`p XOR k = c，c XOR k = p，p XOR c = k`

把P看成明文，通过XOR运算后得到密文C，那么K值便是密钥。因此XOR常用于加密。由于简单，而且速度很快，常用于简单的字符加密，以对抗字符参考。本文仅讨论使用8位key，只作一次xor运算的情况。尽管安全性很差(p xor c = k)，但是大家都喜欢用简单的方法。

先从最简单的ASCII编码开始。它包括26个英文字母和10个数字以及一些符号。单字节的编码，而且最高位一般情况下为0。由于每个字节都由固定的KEY进行XOR加密，因此检查每一个字节的最高位是否相同，便能知道处理的字符是否为ASCII编码。

我们知道，英文使用空格（0x20）来分隔每一单词。这样便为我们提供了另外一个攻击XOR加密字符的途径。

回到题目

使用工具https://github.com/hellman/xortool/tree/master/xortool

将其进行异或./xortool-xor -f xmd5 -h 01780c4c109e3237120cfbbacb8f6a53 | xxd


发现有很多0x00,猜测是不是空格，空格是0x20，如果0x00是空格的话，那么就是0x00^0x20，
整体数据都异或0x20得到：

./xortool-xor -f xmd5 -h 01780c4c109e3237120cfbbacb8f6a53 -h 20 | xxd


key后面是个空格，还有ut前面，猜测key被两个\*包括，即\*key\*，所以就是0x00^0x2a,所以不对劲的地方1c^2a得到36，所以正确的列表如下:

xortool-xor -f xmd5 -h 01780c4c109e3237120cfbbacb8f6a53 -h 20 -h 0000000000000000000000000000002a | xxd

RCTF{We1l_d0n3_6ut_wh4t_i5_\*key\*} 不是 flag，檔名 x_xor_md5 ，所以猜測 xor key 應該是一組 MD5 hash

md5("that") == "21582c6c30be1217322cdb9aebaf4a59"
