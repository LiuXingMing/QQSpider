##**博客见：《 [QQ空间爬虫分享（一天可抓取400万条数据）](http://blog.csdn.net/bone_ace/article/details/50759970) 》**##
<p>
<p>
##**爬虫功能：**##
QQSpider 使用广度优先策略爬取QQ空间中的个人信息、日志、说说、好友四个方面的信息，详细可见[数据库说明](#Database)。
判重使用“内存位”判重，理论上亿数量级的QQ可瞬间判重，内存只占用400M+。
爬虫速度可达到单机每天400万条数据以上（具体要考虑网速、网络带宽、稳定性等原因。我在学校是400万+，但在公司那边却只有六成的速度，普通家庭网络可能会更慢）。

<p>
<p>
##**环境、架构：**##
开发语言：Python2.7
开发环境：64位Windows8系统，4G内存，i7-3612QM处理器。
数据库：MongoDB 3.2.0
（Python编辑器：Pycharm 5.0.4；MongoDB管理工具：MongoBooster 1.1.1）

主要使用 requests 模块抓取，部分使用 BeautifulSoup 解析。
多线程使用 multiprocessing.dummy 。
抓取 Cookie 使用 selenium 和 PhantomJS 。
判重使用 BitVector 。

<p>
<p>
##**使用说明：**##
启动前配置：
MongoDB安装好 能启动即可，不需要配置。
Python需要安装以下模块（注意官方提供的模块是针对win32系统的，64位系统用户在使用某些模块的时候可能会出现问题，所以尽量先找[64位模块](http://www.lfd.uci.edu/~gohlke/pythonlibs/)，如果没有64的话再去安装32的资源）：
requests、BeautifulSoup、multiprocessing、selenium、itertools、BitVector、pymongo

另外我们需要使用到 PhantomJS，这并不是 Python 的模块，而是一个exe可执行文件，我们可以利用它模拟浏览器去获取 Cookie 。使用方法：将 phantomjs-2.0.0-windows.zip 压缩包里面的 phantomjs.exe 放到你的 Python 目录下就行了。

----------
启动程序：

 1. 进入 myQQ.txt 写入QQ账号和密码（用一个空格隔开，不同QQ换行输入），一般你开启几个QQ爬虫线程，就至少需要两倍数量的QQ用来登录，至少要轮着登录嘛。
 2. 进入 init_messages.py 进行爬虫参数的配置，例如线程数量的多少、设置爬哪个时间段的日志，哪个时间段的说说，爬多少个说说备份一次等等。
 3. 运行 init.py 文件开启爬虫项目。
 4. 爬虫开始之后首先根据 myQQ.txt 里面的QQ去获取 Cookie（以后登录的时候直接用已有的Cookie，就不需要每次都去拿Cookie了，遇到Cookie失效也会自动作相应的处理）。获取完Cookie后爬虫程序会去申请四百多兆的内存，**申请的时候会占用两G左右的内存，大约五秒能完成申请，之后会掉回四百多M**。
 5. 爬虫程序可以中途停止，下次可打开继续抓取。

<p>
<p>
##**运行截图：**##
![QQSpider code](http://img.blog.csdn.net/20160228182808259)

说说数据：
![QQSpider Mood](http://img.blog.csdn.net/20160228182903510)

日志数据：
![QQSpider Blog](http://img.blog.csdn.net/20160228183006425)

好友关系数据：
![QQSpider Friends](http://img.blog.csdn.net/20160228183036105)

个人信息数据：
![QQSpider Information1](http://img.blog.csdn.net/20160228183107622)

![QQSpider Information2](http://img.blog.csdn.net/20160228183128216)
<div id="Database"></div>
<p>
<p>
##**数据库说明：**##
QQSpider主要爬取QQ用户的说说、日志、朋友关系、个人信息。
数据库分别设置 Mood、Blog、Friend、Information 四张表。

<p>
**Mood 表：**
\_id：采用 "QQ_说说id" 的形式作为说说的唯一标识。
Co-oridinates：发说说时的定位坐标，调用地图API可直接查看具体方位，可识别到在哪一栋楼。
Comment：说说的评论数。
Like：说说的点赞数。
Mood_cont：说说内容。
PubTime：说说发表时间。
QQ：发此说说的QQ号。
Source：说说的根源（对于转发的说说），采用 "QQ_说说id" 的形式标识。
Tools：发说说的工具（手机类型或者平台）。
Transfer：说说的转发数。
URL：说说的链接地址。
isTransfered：此说说是否属于转发来的。

<p>
**Blog 表：**
_id：采用 "QQ_日志id" 的形式作为日志的唯一标识。
Blog_cont：日志内容。
Comment：日志的评论数。
Like：日志的点赞数。
PubTime：日志的发表时间。
QQ：发此日志的QQ号。
Share：日志的分享数。
Source：日志的根源（对于转发的日志），采用 "QQ_日志id" 的形式标识。
Title：日志的标题。
Transfer：日志的转发数。
URL：日志的链接地址。
isTransfered：此日志是否属于转发来的。

<p>
**Friend 表：**
_id：采用 QQ 作为唯一标识。
Num：此QQ的好友数（仅统计已抓取到的）。
Fx：朋友的QQ号，x代表第几位好友，x从1开始逐渐迭加。

<p>
**Information 表：**
_id：采用 QQ 作为唯一标识。
Age：年龄。
Birthday：出生日期。
Blog：已发表的日志数。
Blogs_WeGet：我们已抓取的日志数。
Blood_type：血型。
Career：职业。
Company：公司。
Company_address：公司详细地址。
Company_city：公司所在城市。
Company_country：公司所在国家。
Company_province：公司所在省份。
Constellation：星座。
CurrentTime：抓取当前信息的时间（不同时间信息会不同）。
FriendsNum：好友数（仅统计已抓取的）。
Gender：性别。
Hometown_city：故乡所在城市。
Hometown_country：故乡所在国家。
Hometown_province：故乡所在省份。
Living_city：居住的城市。
Living_country：居住的国家。
Living_province：居住的省份。
Marriage：婚姻状况。
Message：空间留言数。
Mood：已发表的说说数。
Mood_WeGet：我们已抓取的说说数。
PageView：空间总访问量。
Picture：已发表的照片数（包括相册里的照片和说说里的照片）。
<p>
<p>
##**结语：**##
自己一个人瞎搞了一个多星期，肯定还有很多地方不规范，不够优化。不足之处请多指出！
