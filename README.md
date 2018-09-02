# Designer

## 关于分享功能的问题

### 术语约定

Circuit - 指通路信息。（一个SBOL文档可以描述一个Circuit）
Protocol - 描述某一个Circuit的实验过程。
Design - 记录一个Circuit和其对应的Protocol的信息。
Document - 一系列具有父子关系（历史继承关系）的Design。


### 关于part
part之前设计分成公有和私有了。在后端可能需要修改一下逻辑。

### 关于Document
事实上这是一个不需要被实现的概念。把Design的`name`字段作为Document的id，在处理时我们认为拥有同一个`Name`的Design是归属于同一个`Document`的。同时，一个`Document`只有一个`Master`，即建立这个Document（或者说建立这个Document的第一个Design）的用户名。此外，一个Document共享一个`EditableGroup`，其中记录着可以编辑该Document下所有Design的用户。

### 关于Design
Design由唯一id号确认。访问Design的url约定为:`homepage/circuit/{id}`

Design需要新加入以下字段：
1. `Master`，指建立**该Design所归属于某个Document**的用户。
2. `UpdateTime`，记录该Design的更新时间。
3. `Version`，版本号。`Name`与`Version`唯一映射到一个`Id`。
4. `Previous`，父亲/前驱版本号。
5. `Master`，含义参考上文。
6. `Editor`，编辑该Design的用户。
7. `EditableGroup`，含义参考上文。

### 前端更新
#### 保存Design
保存分两种：
1. 保存(save)。默认是在同一个Document下派生出一个新的Design版本，不需要记录Design名字信息，只需要记录更新了的信息和父亲版本即可。
2. 保存为新的Document(save as new document)。要求用户填写`Name`字段，父亲版本记为-1（表示没有前驱）。

#### 加载Design
加载Design首先要选定`Name`，然后再选定对应的`Version`。这部分还可以做各种排序、过滤，此是后话。

#### Something Else
有一个叫`simple_history`的py库，我要先看一下能不能用进来。


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
