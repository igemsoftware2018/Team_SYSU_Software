# Designer

## 值得大家知道的新特性
### Logger
**tips** 遇到`xxx file not found`的报错时，只需要把该文件创建好即可。所有的log文件都在`gitignore`里，目的是防止大家的log之间出现conflict.
现在所有的Python后端都可以很方便地输出Logger调试信息。
具体用法如下。
``` python
import logging
logger = logging.getLogger(__name__)
# 以上两行放在文件的开头。常用的文件里，已经设置好了，不用再设置了

logger.error('hello world')
```
以上代码的输出信息是
``` shell
ERROR:design.views: hello (2018-08-31 13:54:21; design_views.py:414)
```
会自动带上日期、文件名、行号等信息。

一共有5种debug方式
- logger.debug(): Low level system information for debugging purposes
- logger.info(): General system information
- logger.warning(): Information describing a minor problem that has occurred.
- logger.error(): Information describing a major problem that has occurred.
- logger.critical(): Information describing a critical problem that has occurred.
按照认为的程度使用就可以了。
logger的方式从上到下是越来越重要的关系。可以设置filter来隔离调低等级的log，保留高等级的log。
## 当前存在的一些问题

### 关于User的Model
当前user的model是以email字符串作为来唯一识别的，我个人打算考虑再加入一个Username的串作为唯一识别每一个账户的关键字，如：
```
Username: user1 (identity)
Password: xxxxx
Email: xxxx@example.com (identity)
```
这样做我认为对后续的功能延伸是很有必要的。(毕竟只有傻逼才会用email作为identity)(我并没有骂去年的软件队是傻逼)(x)

## 存储Part的思路
按照豪辰的意思，我们对part进行分类：
1.公有part。
所有的用户都具有访问此类part的权限。也就是说他们在搜索栏里是可以搜索到这些part的。
2.私有part
这类part由用户生成，并且只能由生成该part的用户所访问。

可以考虑如下的实现方式：

给Part的Model中添加两项：
```python
isPublic = models.BooleanField() #True表示这个part是公有
user = models.CharField(default = "Unknown") #当isPublic = False时这一项记录的则是创建这个part的用户的用户名
```
同时，我们可以约定，一个part的Name可以是如下结构：
1. 如果part是公有的，那么其name中一定不含有`@`字符
2. 如果part是私有的，那么其name的结构一定是`part_original_name@username`。例如说yb创建了一个名字为HappyValentinesDay的part，那么这个part的名字就叫做`HappyValentinesDay@yb`。
有如上约定的情况下，就可以确保数据库中的每一个part的name都是唯一的。

此外，在搜索part的时候，要使用正则表达式对所有part_name进行处理，只输出公有part和用户自己的私有part。

--by kingiw

## Import data

```shell
cd designSite
python manage.py makemigrations design
python manage.py migrate
python manage.py shell < init.py
```
