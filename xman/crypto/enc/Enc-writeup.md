Enc-writeup

Python知识：

```
int(x, base=10) 函数用于将一个字符串或数字转换为整型。
x -- 字符串或数字。
base -- x的进制数，默认十进制。

libnum库
libnum.n2s(n):将n(整型)转换为字符串
```

坑的是解出来的莫斯密码是`ALEXCTFTH15O1SO5UP3RO5ECR3TOTXT`

要手动变成ALEXCTF{TH15_1S_5UP3R_5ECR3T_TXT}才行……

```python
import libnum
f = open('zero_one','r')
s = f.read()
output = ''
for i in s.split():
	if('ZERO' == i):
		output += '0'
	if('ONE' == i):
		output += '1'
output = int(output,2)
print output
print libnum.n2s(output)
```

