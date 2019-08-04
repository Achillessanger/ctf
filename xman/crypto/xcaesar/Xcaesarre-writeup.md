Xcaesarre-writeup

凯撒密码：128个字符按j进行偏移（ascii可表示128个字符）

所以进行简单爆破即可

```python
output = 'bXNobgJyaHB6aHRwdGgE'
for i in range(128):
	output2=''
	for j in output.decode('base64'):
		output2 += chr((ord(j)+i)%128)
	if 'flag' in output2:
		print output2
	
```

*注意`for j in output.decode('base64'):`

因为源文件最后是`print caesar_encrypt(m,k).encode("base64")`

