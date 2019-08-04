Xbase64-writeup

题目中给了一个base64_table

```python
base64_table = ['=','A', 'B', 'C', 'D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                'a', 'b', 'c', 'd','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                '0', '1', '2', '3','4','5','6','7','8','9',
                '+', '/'][::-1]
```

与普通base64加密时的表不同在于`‘=’放在了第一个`，`最后有一个[::]-1颠倒`

从剩下的代码可以看出加密方式还是按照普通base64的方法加密的，只是base64表的顺序不一样了



给出output：`mZOemISXmpOTkKCHkp6Rgv==`

解法思路是将output里的所有字符按照位置顺序替换成普通base64加密时表里的该顺序的字符，再调用正常的`base64.b64decode(str)`来解码

```python
import base64
base64_table = ['=','A', 'B', 'C', 'D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                'a', 'b', 'c', 'd','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                '0', '1', '2', '3','4','5','6','7','8','9',
                '+', '/'][::-1]
table = ['A', 'B', 'C', 'D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                'a', 'b', 'c', 'd','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z',
                '0', '1', '2', '3','4','5','6','7','8','9',
                '+', '/','=']
output = 'mZOemISXmpOTkKCHkp6Rgv=='
output2 = ''
for char in output:
	output2 += table[base64_table.index(char)]

print base64.b64decode(output2).decode()
```

