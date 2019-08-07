# Reverse-rel-100-writeup

```c
int __cdecl __noreturn main(int argc, const char **argv, const char **envp)
{
  __pid_t v3; // eax
  size_t read_str_length; // rax
  ssize_t v5; // rbx
  bool v6; // al
  char **argva; // [rsp+0h] [rbp-1D0h]
  bool bCheckPtrace; // [rsp+13h] [rbp-1BDh]
  ssize_t numRead; // [rsp+18h] [rbp-1B8h]
  ssize_t numReada; // [rsp+18h] [rbp-1B8h]
  char bufWrite[200]; // [rsp+20h] [rbp-1B0h]
  char bufParentRead[200]; // [rsp+F0h] [rbp-E0h]
  unsigned __int64 v13; // [rsp+1B8h] [rbp-18h]

  argva = (char **)argv;
  v13 = __readfsqword(0x28u);
  bCheckPtrace = detectDebugging();
  if ( pipe(pParentWrite) == -1 )
    exit(1);
  if ( pipe(pParentRead) == -1 )
    exit(1);
  v3 = fork();
  if ( v3 != -1 )
  {
    if ( v3 )
    {
      close(pParentWrite[0]);
      close(pParentRead[1]);
      while ( 1 )
      {
        printf("Input key : ", argva);
        memset(bufWrite, 0, 0xC8uLL);
        gets(bufWrite, 0LL);
        read_str_length = strlen(bufWrite);
        v5 = write(pParentWrite[1], bufWrite, read_str_length);
        if ( v5 != strlen(bufWrite) )
          printf("parent - partial/failed write", bufWrite);
        do
        {
          memset(bufParentRead, 0, 0xC8uLL);
          numReada = read(pParentRead[0], bufParentRead, 0xC8uLL);
          v6 = bCheckPtrace || checkDebuggerProcessRunning();
          if ( v6 )
          {
            puts("Wrong !!!\n");
          }
          else if ( !checkStringIsNumber(bufParentRead) )
          {
            puts("Wrong !!!\n");
          }
          else
          {
            if ( atoi(bufParentRead) )
            {
              puts("True");
              if ( close(pParentWrite[1]) == -1 )
                exit(1);
              exit(0);
            }
            puts("Wrong !!!\n");
          }
        }
        while ( numReada == -1 );
      }
    }
    close(pParentWrite[1]);
    close(pParentRead[0]);
    while ( 1 )
    {
      memset(bufParentRead, 0, 0xC8uLL);
      numRead = read(pParentWrite[0], bufParentRead, 0xC8uLL);
      if ( numRead == -1 )
        break;
      if ( numRead )
      {
        if ( childCheckDebugResult() )
        {
          responseFalse();
        }
        else if ( bufParentRead[0] == 123 )
        {
          if ( strlen(bufParentRead) == 42 )
          {
            if ( !strncmp(&bufParentRead[1], "53fc275d81", 0xAuLL) )
            {
              if ( bufParentRead[strlen(bufParentRead) - 1] == 125 )
              {
                if ( !strncmp(&bufParentRead[31], "4938ae4efd", 0xAuLL) )
                {
                  if ( !confuseKey(bufParentRead, 42) )
                  {
                    responseFalse();
                  }
                  else if ( !strncmp(bufParentRead, "{daf29f59034938ae4efd53fc275d81053ed5be8c}", 0x2AuLL) )
                  {
                    responseTrue();
                  }
                  else
                  {
                    responseFalse();
                  }
                }
                else
                {
                  responseFalse();
                }
              }
              else
              {
                responseFalse();
              }
            }
            else
            {
              responseFalse();
            }
          }
          else
          {
            responseFalse();
          }
        }
        else
        {
          responseFalse();
        }
      }
    }
    exit(1);
  }
  exit(1);
}
```

主要看下面那段

注意`else if ( bufParentRead[0] == 123 )`这个地方的123在ida里可以右键显示成char

```c
else if ( bufParentRead[0] == '{' )  //第一个字符是{
        {
          if ( strlen(bufParentRead) == 42 ) //长度42
          {
            if ( !strncmp(&bufParentRead[1], "53fc275d81", 0xAuLL) ) //第二个字符开始是53fc275d81
            {
              if ( bufParentRead[strlen(bufParentRead) - 1] == '}' ) //最后一个字符是}
              {
                if ( !strncmp(&bufParentRead[31], "4938ae4efd", 0xAuLL) )//第31个字符开始到结尾是4938ae4efd
                {
                  if ( !confuseKey(bufParentRead, 42) )
                  {
                    responseFalse();
                  }
                  else if ( !strncmp(bufParentRead, "{daf29f59034938ae4efd53fc275d81053ed5be8c}", 0x2AuLL) ) //字符串需要饱含这些内容
                  {
                    responseTrue();
                  }
```

综上条件

```shell
parallels@parallels-vm:~/Documents/xman/reverse/rel-100$ ./RE100 
Input key : {53fc275d81053ed5be8cdaf29f59034938ae4efd}   
True

```

