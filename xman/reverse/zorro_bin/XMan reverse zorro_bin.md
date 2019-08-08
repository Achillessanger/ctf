## XMan reverse zorro_bin

### MD5函数

```c
struct MD5Context {
    uint32 buf[4];
    uint32 bits[2];
    unsigned char in[64];
};

/*
 * Start MD5 accumulation.  Set bit count to 0 and buffer to mysterious
 * initialization constants.
 */
void MD5Init(struct MD5Context *context);

/*
 * Update context to reflect the concatenation of another buffer full
 * of bytes.
 */
void MD5Update(struct MD5Context *context, unsigned char const *buf, unsigned len);

/*
 * Final wrapup - pad to 64-byte boundary with the bit pattern 
 * 1 0* (64-bit count of bits processed, MSB-first)
 */
void MD5Final(unsigned char digest[16], struct MD5Context *context);
//结果就在buf中，16字节

/*
 * The core of the MD5 algorithm, this alters an existing MD5 hash to
 * reflect the addition of 16 longwords of new data.  MD5Update blocks
 * the data and converts bytes into longwords for this routine.
 */
void MD5Transform(uint32 buf[4], uint32 const in[16]);


/* 
 * 
 * MD5Init是一个初始化函数，初始化核心变量，装入标准的幻数
 * MD5Update是MD5的主计算过程，buf是要变换的字节串，inputlen是长度，这个函数由getMD5ofStr调用，调用之前需要调用md5init
 * MD5Final整理和填写输出结果
 */
```

### 题目分析

首先，flag存在v12变量中，该变量由MD5和一个加密获得。需要输入数字，经过加密算法生成与`5eba99aff105c9ff6a1a913e343fec67`字符一样的。

两个方法，首先加密是个异或，异或的字符串是可以直接得到的，存在反异或再md5解密的可能性。

另一种方法，分析加密，发现，我们输入的数字，如果符合要求，即使`v9==10`，会成为srand的seed，而字符串的加密过程是由srand(seed) rand()生成。我们输入饮料ID在17-65535（0x10,0xffff），异或不会超过这个范围，所以所有可能的字符串是可以爆破出来的，则我们可以尝试所有可能爆破出密码。

### exp

```python
import subprocess

l = []
for i in range(65535):
    t = 0
    j = i
    while i:
        i = i & (i - 1)
        t += 1
    if t == 10:
        l.append(j)
### 爆破写法
for i in l:
    proc = subprocess.Popen(['./zorro_bin'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out = proc.communicate(('1\n%s\n' % i).encode('utf-8'))[0]
    if "nullcon".encode('utf-8') in out:
      print(out)

```

### 命令行写法（未试）

```shell
for i in $(seq 1 65535); do echo -e "1\n$i" | ./zorro_bin | grep -i nullcon ; done

for i in `seq 1 65535`; do echo $i >> answers.txt; ./zorro_bin <<< $'1\n'$i$'\n' | grep -i 'choose right mix' >> answers.txt; done
```



## Other write-ups and resources

- http://vulnerablespace.blogspot.co.uk/2016/01/ctf-writeup-hackim-2016-zorropub-re-100.html
- http://bannsecurity.com/index.php/home/10-ctf-writeups/26-hackim-2016-zorropub
- https://www.xil.se/post/hackim-2016-re-1-kbeckmann/
- https://medium.com/guilty-spork/hackim-re-100-zorropub-89f81c3f7c16#.tb869lzaf
- https://github.com/Team-Sportsball/CTFs-2016/blob/master/nullcon-hackim-2016/RE_1/zorro_pub.md