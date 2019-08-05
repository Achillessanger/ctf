### XMan Crypto 你猜猜

下载附件得到`haha.txt`



![img](https:////upload-images.jianshu.io/upload_images/10148719-ce9ff9da7a2d191b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/862/format/webp)




 HxD新建文件，将中的数据copy进去，命名为

注意是文件内的内容是二进制文件，所以新建一个文件而不是修改之前的文件后缀

![img](https:////upload-images.jianshu.io/upload_images/10148719-9d4098f7da94b548.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/853/format/webp)




 解压1.zip,发现需要解压密码，直接暴力破解得到密码为123456



![img](https:////upload-images.jianshu.io/upload_images/10148719-9f1a313b040e627b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/996/format/webp)


 解压后得到



![img](https:////upload-images.jianshu.io/upload_images/10148719-e357742de0570499.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/375/format/webp)

解码工具使用的是fcrackzip，安装在Linux下

使用命令

### 使用穷举法：

```shell
# fcrackzip -b -c 'aA1!' -l 1-10 -u crack_this.zip 
```

-b代表brute-force；-l限制密码长度；-c指定使用的字符集：

![fcrackzip破解zip密码](http://topspeedsnail.com/images/2016/5/Screen%20Shot%202016-05-08%20at%2013.56.05.png)

知道zip的密码是数字，可以执行（加快破解速度）：

```
# fcrackzip -b -c '1' -l 1-10 -u crack_this.zip 
```

### 使用字典：

下面以Kali Linux自带的rockyou字典为例，你可以去网上下载GB级的大字典。

使用前先解压：

```shell
# gzip -d /usr/share/wordlists/rockyou.txt.gz
```

使用字典破解：

```shell
# fcrackzip -D -p /usr/share/wordlists/rockyou.txt -u crack_this.zip
```