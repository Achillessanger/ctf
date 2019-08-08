## XMan reverse Secret Galaxy 结构体分析

参考资料：https://github.com/ctfs/write-ups-2015/tree/master/school-ctf-winter-2015/reverse/secret-galaxy-300

> 他们说我们旁边有一个有人居住的星系。
>
> 我们有一个奇怪的程序，提供有关附近星系的信息。乍一看，人们会认为它没有提到秘密......
>


## Write-up
### Secret Galaxy

程序输出是galaxy数据库的内容。根据故事，我们需要找到一个隐藏在二进制中的星系。让我们检查一下程序的调试信息。

```assembly
strip task4
task4: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked (uses shared libs), for GNU/Linux 2.6.32, BuildID[sha1]=1577ba67c51b6a8c49caacd2b4fe578c502619a9, not stripped
```

二进制文件没有被剥离，所以它有调试信息。因此调试器将有助于解决它。我们可以使用GDB。

```assembly
gdb ./task4
(gdb) br main
(gdb) r
78      fill_starbase(starbase);
(gdb) n
79      print_starbase(starbase);
(gdb) print starbase
$1 = [{name = 0x400a38 "NGS 2366", distance = 1804289383, is_inhabited = 0, secret_information = 0x0, next = 0x6010bc <starbase+40>, pred = 0x0}, {name = 0x400a41 "Andromeda", distance = 846930886, is_inhabited = 0, secret_information = 0x0, next = 0x6010e4 <starbase+80>, pred = 0x601094 <starbase>}, {name = 0x400a4b "Messier", distance = 1681692777, is_inhabited = 0, secret_information = 0x0, next = 0x60110c <starbase+120>, pred = 0x6010bc <starbase+40>}, {name = 0x400a53 "Sombrero", distance = 1714636915, is_inhabited = 0, secret_information = 0x0, next = 0x601134 <starbase+160>, pred = 0x6010e4 <starbase+80>}, {name = 0x400a5c "Triangulum", distance = 1957747793, is_inhabited = 0, secret_information = 0x0, next = 0x60115c <sc>, pred = 0x60110c <starbase+120>}]
```

Starbase是一个映射列表。每个项目都有指向下一个项目的指针。星系结构的一个字段是secret_information字段，它不出现在程序的输出中。接下来是`next`列表的最后一项的字段不等于`NULL`。我们来看看那个地址吧。

```assembly
(gdb) x/10qw 0x60115c
0x60115c <sc>:  0x00400a67  0x00000000  0x00007a69  0x00000001
0x60116c <sc+16>:   0x00601184  0x00000000  0x00000000  0x00000000
0x60117c <sc+32>:   0x00000000  0x00000000
```

查看结构中的每个地址并找到一个标志。

```assembly
...
(gdb) x/1s 0x00601184
0x601184 <sc+40>:   "aliens_are_around_us"
```