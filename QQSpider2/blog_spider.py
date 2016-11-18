# coding=utf-8
import re
import datetime
import itertools
from bs4 import BeautifulSoup
from multiprocessing.dummy import Pool


class BlogSpider(object):
    """ 功能：爬取QQ日志 """

    def __init__(self, spiderMessage, changer):
        self.message = spiderMessage
        self.changer = changer

    def beginer(self):
        blog_list = self.get_blog_list()  # 获取日志ID列表
        if blog_list:
            pool = Pool(self.changer.my_messages.thread_num_Blog)
            myBlog = pool.map(self.get_blog, itertools.izip(blog_list.keys(), blog_list.values()))
            pool.close()
            pool.join()
            fail = myBlog.count(-1)  # 对于获取失败的日志，需要清除
            for i in range(fail):
                myBlog.remove(-1)
            return myBlog

    def get_blog_list(self):  # 获取日志ID列表
        """ 获取日志ID列表 """
        bloglist = {}
        posnum = 0
        failure = 0
        pagedown = True
        while pagedown and failure < self.message.fail_time:
            try:
                url = 'https://h5.qzone.qq.com/proxy/domain/b11.qzone.qq.com/cgi-bin/blognew/get_abs?hostUin=%s&uin=%s&blogType=0&cateName=&cateHex=&statYear=2016&reqInfo=7&pos=%s&num=15&sortType=0&absType=0&source=0&rand=0.2309432572650698&ref=qzone&g_tk=%s&verbose=1' % (
                    self.message.qq, self.message.account, posnum, self.message.gtk)
                r = self.message.s.get(url, timeout=self.message.timeout)
                if r.status_code == 403:
                    break
                text = r.text
                while u'请登录空间' in text:  # Cookie失效
                    try:
                        self.changer.changeCookie(self.message)
                        r = self.message.s.get(url, timeout=self.message.timeout)
                        if r.status_code == 403:
                            return bloglist
                        text = r.text
                    except Exception:
                        print "BlogSpider.get_blog_list:获取Cookie失败，此线程关闭！"
                        exit()
                bidlist = re.findall('"blogId":(\d+),.*?"pubTime":"(.*?)",.*?"title":"(.*?)",.*?"commentNum":(\d+)',
                                     text, re.S)  # 发表时间、日志标题、评论数
                if len(bidlist) == 0:
                    return bloglist
                for elem in bidlist:
                    try:
                        pubTime = datetime.datetime.strptime(elem[1], "%Y-%m-%d %H:%M")
                        if pubTime > self.changer.my_messages.blog_after_date:
                            bloglist[elem[0]] = {
                                "_id": self.message.qq + "_" + elem[0],
                                "QQ": self.message.qq,
                                "Title": "《" + elem[2] + "》",
                                "PubTime": pubTime - datetime.timedelta(hours=8),
                                "Comment": int(elem[3])
                            }
                            pagedown = True
                        else:
                            pagedown = False
                    except Exception, e:
                        pass
                posnum += 15
            except Exception, e:
                failure += 1
        return bloglist

    def get_blog(self, blogs):
        """ 提供一个日志的ID，下载并返回该日志的内容 """
        blog_content = ''
        blog_id = blogs[0]
        myBlog = blogs[1]
        failure = 0
        while failure < self.message.fail_time:
            try:
                b_url = 'http://b11.qzone.qq.com/cgi-bin/blognew/blog_output_data?uin=%s&blogid=%s' % (
                self.message.qq, blog_id)
                r = self.message.s.get(b_url, headers=self.changer.my_messages.myheader, timeout=self.message.timeout)
                if r.status_code == 403:
                    return -1
                else:
                    b_content = r.text.strip()
                    soup = BeautifulSoup(b_content, "html.parser")
                    blog = soup.find('div', id='blogDetailDiv')
                    if blog == None:  # 如果没有获取到内容
                        return -1
                    else:
                        for string in blog.stripped_strings:
                            blog_content += string
                        temp = re.findall('"orguin":(\d+).*?"orgblogid":(\d+)', soup.text, re.S)
                        myBlog["isTransfered"] = True if u'[转]' in soup.text else False  # 判断日志是否属于转载
                        myBlog["Source"] = temp[0][0] + '_' + temp[0][1] if len(temp) != 0 else ''  # 起始的日志，用 QQ_日志ID 标识
                        myBlog["Blog_cont"] = blog_content
                        myBlog["URL"] = "http://user.qzone.qq.com/%s/blog/%s" % (myBlog['QQ'], blog_id)
                        result = self.get_blog_message(myBlog)  # 获取点赞数、分享数、转载数
                        if result == -1:
                            return -1
                        return myBlog
            except Exception, e:
                failure += 1
        return -1  # 如果失败次数太大则返回失败

    def get_blog_message(self, myBlog):
        """ 获取日志的点赞数、分享数、转载数 """
        myBlog["Like"] = -1  # 初始值设为-1，如果最终保存到本地的值仍为-1，即说明获取失败
        myBlog["Share"] = -1
        myBlog["Transfer"] = -1
        try:
            if myBlog["isTransfered"] and len(myBlog["Source"]) != 0:
                temp1 = myBlog["Source"]
            elif not myBlog["isTransfered"]:
                temp1 = myBlog["_id"]
            else:
                return -1
            temp2 = temp1.split("_")
            temp_qq = temp2[0]
            temp_Blog = temp2[1]
            b_url = 'http://user.qzone.qq.com/p/r/cgi-bin/user/qz_opcnt2?_stp=1455865807042&unikey=http%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fblog%2F' + temp_Blog + '%3C.%3Ehttp%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fblog%2F' + temp_Blog + '%3C%7C%3Ehttp%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fblog%2F' + temp_Blog + '%3C.%3Ehttp%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fblog%2F' + temp_Blog + '&face=0%3C%7C%3E0&fupdate=1&g_tk=' + str(
                self.message.gtk)
            r = self.message.s.get(b_url, headers=self.changer.my_messages.myheader, timeout=self.message.timeout)
            if r.status_code == 403:
                return -1
            else:
                b_content = r.text.strip()
                soup = BeautifulSoup(b_content, "html.parser")
                temp3 = re.findall('"like":(\d+).*?"share":(\d+).*?"forward":(\d+)', soup.text, re.S)  # 利用正则去获取
                if len(temp3) != 0:
                    myBlog["Like"] = int(temp3[0][0])
                    myBlog["Share"] = int(temp3[0][1])
                    myBlog["Transfer"] = int(temp3[0][2])
        except Exception, e:
            return -1
