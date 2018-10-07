# Designer

## 术语约定

Circuit - 指通路信息。（一个SBOL文档可以描述一个Circuit）
Protocol - 描述某一个Circuit的实验过程。
Design - 记录一个Circuit和其对应的Protocol的信息。
Document - 一系列具有父子关系（历史继承关系）的Design。

## 关于分享功能

### url

url有以下两种形式  
第一种形如  
```url
/design/{{design-id}}
```
它是在用户点击了主页的通路存档后，跳转到链接。  
第二种形如  
``` url
/design/share/{{design-id}}
```
它是在用户创建了一个分享后，分享对应的链接。  

### 关于part

part 分成公有和私有

### 关于Document

事实上这是一个不需要被实现的概念。把Design的`name`字段作为Document的id，在处理时我们认为拥有同一个`Name`的Design是归属于同一个`Document`的。同时，一个`Document`只有一个`Master`，即建立这个Document（或者说建立这个Document的第一个Design）的用户名。此外，一个Document共享一个`EditableGroup`，其中记录着可以编辑该Document下所有Design的用户。

### 关于Design

Design由唯一id号确认。访问Design的url约定为:`homepage/circuit/{id}`

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

## Import data

```shell
cd designSite
python manage.py makemigrations design
python manage.py migrate
python manage.py shell < init.py
```
