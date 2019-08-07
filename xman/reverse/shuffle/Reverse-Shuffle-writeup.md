# Reverse-Shuffle-writeup

放进ida：

```c
  v3 = time(0);
  v4 = getpid();
  srand(v3 + v4);
  for ( i = 0; i <= 99; ++i )
  {
    v5 = rand() % 0x28u;
    v6 = rand() % 0x28u;
    v7 = *(&s + v5);
    *(&s + v5) = *(&s + v6);
    *(&s + v6) = v7;
  }
  puts(&s);
  return 0;
```

发现字符串被和随机出来的数进行了一下操作

题目提示说：`找到字符串在随机化之前.`

于是在gdb里，在for循环之前找个位置打断点，然后看栈上有些什么

```shell
gdb-peda$ stack 30
0000| 0xffffceb0 --> 0x5d4ad850 
0004| 0xffffceb4 --> 0x2f ('/')
0008| 0xffffceb8 --> 0xf7e0fdc8 --> 0x2b76 ('v+')
0012| 0xffffcebc --> 0xffffcfa4 --> 0xffffd17d ("/home/parallels/Documents/xman/reverse/shuffle/shuffle")
0016| 0xffffcec0 --> 0x8000 
0020| 0xffffcec4 --> 0xf7fb5000 --> 0x1b1db0 
0024| 0xffffcec8 --> 0xf7fb3244 --> 0xf7e1b020 (<_IO_check_libio>:	)
0028| 0xffffcecc --> 0x8048379 (<_init+9>:	add    ebx,0x1c87)
0032| 0xffffced0 --> 0x1 
0036| 0xffffced4 ("SECCON{Welcome to the SECCON 2014 CTF!}")
0040| 0xffffced8 ("ON{Welcome to the SECCON 2014 CTF!}")
0044| 0xffffcedc ("elcome to the SECCON 2014 CTF!}")
0048| 0xffffcee0 ("me to the SECCON 2014 CTF!}")
0052| 0xffffcee4 ("o the SECCON 2014 CTF!}")
0056| 0xffffcee8 ("e SECCON 2014 CTF!}")
0060| 0xffffceec ("CCON 2014 CTF!}")
0064| 0xffffcef0 (" 2014 CTF!}")
0068| 0xffffcef4 ("4 CTF!}")
0072| 0xffffcef8 --> 0x7d2146 ('F!}')
0076| 0xffffcefc --> 0xb2efbf00 
0080| 0xffffcf00 --> 0x0 
0084| 0xffffcf04 --> 0xf7fb5000 --> 0x1b1db0 
0088| 0xffffcf08 --> 0x0 
0092| 0xffffcf0c --> 0xf7e1b637 (<__libc_start_main+247>:	add    esp,0x10)
0096| 0xffffcf10 --> 0x1 

```

flag：`SECCON{Welcome to the SECCON 2014 CTF!}`

