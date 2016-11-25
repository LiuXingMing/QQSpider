##**QQSpider1:**##
<br/>
详情请见博客： [《QQ空间爬虫分享（一天可抓取 400 万条数据） 》](http://blog.csdn.net/bone_ace/article/details/50771839)
如果出现报错：
```
Traceback (most recent call last):
  File ".\init.py", line 20, in <module>
    my_messages.backups() # 备份爬虫信息
NameError: name 'my_messages' is not defined
```

<br/>
多半的原因是 BitVector 模块用不了，可自行调试。
<br/>
如果确定是BitVector用不了的话可以用 "BitVector模块报错解决" 里面的两个文件替换掉原有文件，不使用BitVector判重，改用python的list判重（数据量不大的话效果是一样的）。

<br/>
<br/>
-------------------------------------------------------&nbsp;&nbsp;&nbsp;分界线&nbsp;&nbsp;&nbsp;-------------------------------------------------------
<br/>
<br/>
##**QQSpider2:**##
更新后的版本，详情请见博客： [《QQ空间爬虫分享（2016年11月18日更新）》](http://blog.csdn.net/Bone_ACE/article/details/53213779)

<br/>
有同学反映，爬QQ空间的很多都是学生想爬一些数据做统计研究的，本不是计算机专业，爬起来比较困难，希望有现成的数据出售。但是因为工作变动，其实今年3月份 程序开发完后我就没有跑过了，所以手上也没有数据。不过接下来我会开一两台机器跑这个爬虫，如果需要数据可以邮件联系我（bone_ace@163.com）。

遇到什么问题请尽量留言，方便后来遇到同样问题的同学查看。也可加一下QQ交流群：<a target="_blank" href="http://shang.qq.com/wpa/qunwpa?idkey=d3bd977692493ea2764aec73f6ead724e3b339c2e4f3999383331a0fab20e2a9"><img border="0" src="http://pub.idqqimg.com/wpa/images/group.png" alt="QSpider" title="QSpider"></a>。

<br/>
<br/>
