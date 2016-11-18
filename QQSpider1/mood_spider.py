# encoding=utf-8
import re
import time
import datetime
from multiprocessing.dummy import Pool as ThreadPool


class MoodSpider(object):
    """ 功能：爬取QQ说说 """

    def __init__(self, spiderMessage, changer):
        self.message = spiderMessage
        self.changer = changer

    def beginer(self):
        myMood = []
        failure = 0
        while failure < self.message.fail_time:
            try:
                page = 1
                while page > 0:  # 每次循环下载一页说说
                    url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=%s&pos=%d&num=20&g_tk=%s' % (
                        self.message.qq, (page - 1) * 20, self.message.gtk)
                    r = self.message.s.get(url, timeout=self.message.timeout)
                    if r.status_code == 403:
                        print self.message.qq, 'status_code is 403, now stop'
                        return myMood
                    text = r.text
                    while u'请先登录空间' in text:  # Cookie失效
                        try:
                            self.changer.changeCookie(self.message)
                            url = 'http://taotao.qq.com/cgi-bin/emotion_cgi_msglist_v6?uin=%s&pos=%d&num=20&g_tk=%s' % (
                                self.message.qq, (page - 1) * 20, self.message.gtk)
                            r = self.message.s.get(url, timeout=self.message.timeout)
                            if r.status_code == 403:
                                return myMood
                            text = r.text
                        except Exception:
                            print "MoodSpider.beginer:获取Cookie失败，此线程关闭！"
                            exit()
                    textlist = re.split('\{"certified"', text)[1:]  # 从第二条开始才是说说内容
                    if len(textlist) == 0:
                        return myMood
                    pools = ThreadPool(self.changer.my_messages.thread_num_Mood)
                    myMood1 = pools.map(self.get_mood, textlist)
                    pools.close()
                    pools.join()
                    outOfTime = myMood1.count(-1)  # -1表示含有不在规定时间内的说说
                    failget = myMood1.count(-2)  # 获取失败
                    for i in range(outOfTime):
                        myMood1.remove(-1)
                    for i in range(failget):
                        myMood1.remove(-2)
                    if outOfTime > 0:  # 如果存在-1，就不继续翻页爬了
                        page = -1
                    else:
                        page += 1
                    myMood += myMood1
                break  # 抓取完成
            except Exception:
                failure += 1
        return myMood

    def get_mood(self, texts):
        """ 从texts字符串里面抽取出说说信息 """
        myMood = {}
        created_time = re.findall('"created_time":(\d+)', texts)  # ----->获取时间
        if len(created_time) == 0:  # 如果正则没有获取到时间，则获取说说失败
            return -2
        else:
            temp_pubTime = datetime.datetime.fromtimestamp(int(created_time[0]))
        if temp_pubTime < self.changer.my_messages.mood_after_date:  # 如果说说时间不在规定时间内
            return -1
        myMood["PubTime"] = temp_pubTime - datetime.timedelta(hours=8)  # 发表时间,正则返回来的是Unix时间戳（例如：1454837425）

        tid = re.findall('"t1_termtype":.*?"tid":"(.*?)"', texts)  # ----->获取说说ID
        if len(tid) == 0:
            mid = 0
        else:
            mid = tid[0]  # 说说ID
        myMood["_id"] = self.message.qq + "_" + mid

        myMood["isTransfered"] = False  # ----->获取转载信息
        rt_sum = re.findall('"rt_sum":(\d+)', texts)
        if len(rt_sum) == 0:
            myMood["Transfer"] = 0  # 转载次数
        else:
            myMood["Transfer"] = int(rt_sum[0])

        mood_cont = re.findall('\],"content":"(.*?)"', texts)  # ----->获取说说内容
        if len(mood_cont) == 2:  # 如果长度为2则判断为属于转载
            myMood["Mood_cont"] = "评语:" + mood_cont[0] + "--------->转载内容:" + mood_cont[1]  # 说说内容
            myMood["isTransfered"] = True
        elif len(mood_cont) == 1:
            myMood["Mood_cont"] = mood_cont[0]
        else:
            myMood["Mood_cont"] = ""

        cmtnum = re.findall('"cmtnum":(\d+)', texts)  # ----->获取评论次数
        if len(cmtnum) == 0:
            myMood["Comment"] = 0
        else:
            myMood["Comment"] = int(cmtnum[0])  # 评论次数

        source_name = re.findall('"source_name":"(.*?)"', texts)  # ----->获取发表的工具（如某手机）
        if len(source_name) == 0:
            myMood["Tools"] = ""
        else:
            myMood["Tools"] = source_name.pop()

        myMood["QQ"] = self.message.qq  # ----->获取当前QQ

        myMood["URL"] = "http://user.qzone.qq.com/%s/mood/%s" % (self.message.qq, mid)  # ----->获取说说的URL

        pos_x = re.findall('"pos_x":"(.*?)"', texts)[0]  # ----->获取说说的定位
        pos_y = re.findall('"pos_y":"(.*?)"', texts)[0]
        if len(pos_x) != 0 and len(pos_y) != 0:
            myMood["Co-ordinates"] = pos_y + "," + pos_x
        else:
            myMood["Co-ordinates"] = ""

        rt_tid = re.findall('"rt_tid":"(.*?)"', texts)  # ----->获取说说的源头（转载）
        rt_uin = re.findall('"rt_uin":(\d+)', texts)
        pic_id = re.findall('"pic_id":"(\d+)', texts)
        if len(pic_id) != 0 and len(pic_id[0]) != 0:
            rt_uin = pic_id
        temp_qq = self.message.qq
        temp_mood = mid
        myMood["Source"] = ""
        if len(rt_uin) != 0 and len(rt_uin[0]) != 0 and len(rt_tid) != 0 and len(rt_tid[0]) != 0:
            myMood["Source"] = rt_uin[0] + "_" + rt_tid[0]
            if rt_uin != self.message.qq:
                myMood["isTransfered"] = True
                temp_qq = rt_uin[0]
                temp_mood = rt_tid[0]

        myMood["Like"] = -1  # ----->获取点赞次数
        url = 'http://r.qzone.qq.com/cgi-bin/user/qz_opcnt2?_stp=1455969198161&unikey=http%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fmood%2F' + temp_mood + '.1%3C.%3Ehttp%3A%2F%2Fuser.qzone.qq.com%2F' + temp_qq + '%2Fmood%2F' + temp_mood + '.1&face=0&fupdate=1&g_tk=' + str(
            self.message.gtk)
        try:
            r = self.message.s.get(url, timeout=self.message.timeout)
        except Exception, e:
            return -2
        if r.status_code == 200:
            like = re.findall('"like":(\d+)', r.text)
            if len(like) != 0:
                myMood["Like"] = int(like[0])
        return myMood
