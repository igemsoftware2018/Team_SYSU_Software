# Designer


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
