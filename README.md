##**详情请见博客：《 [QQ空间爬虫分享（一天可抓取 400 万条数据）](http://blog.csdn.net/bone_ace/article/details/50771839) 》**##
<p>
<p>
如果出现报错：
```
Traceback (most recent call last):
  File ".\inti.py", line 20, in <module>
    my_messages.backups() # 备份爬虫信息
NameError: name 'my_messages' is not defined
```

<p>
<p>
多半的原因是 BitVector 模块用不了，可自行调试。
<p>
如果确定是BitVector用不了的话可以用 "BitVector模块报错解决" 里面的两个文件替换掉原有文件，不使用BitVector判重，改用python的list判重（数据量不大的话效果是一样的）。

<br/>
<br/>
-------------------------------------------------------&nbsp;&nbsp;&nbsp;分界线&nbsp;&nbsp;&nbsp;-------------------------------------------------------
<br/>
20160830更新：
<br/>
本项目的代码还是五个月前的，抓取规则可能有所改变，不保证代码可以正常运行。很抱歉此代码不再更新，仅供参考，QQ交流群：563830972。
有兴趣的朋友可以pull一下更新代码。
感谢各位的关注和支持！
