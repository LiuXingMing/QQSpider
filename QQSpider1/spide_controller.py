# coding=utf-8
import time
import pymongo
import blog_spider
import mood_spider
import friend_spider
import information_spider
import public_methods
from multiprocessing.dummy import Pool as ThreadPool


class SpideController(object):
    """ 功能：控制去抓取日志、说说、个人信息，并保存到MongoDB """

    def __init__(self, my_messages=None):
        self.my_messages = my_messages
        self.changer = public_methods.Changing(self.my_messages)  # 新建一个对象，用来更换QQ，更换Cookie
        self.mongo = pymongo.MongoClient('localhost', 27017)
        self.db = self.mongo['QQ']  # 打开MongoDB的QQ数据库

    def beginer(self):
        while self.my_messages.qq_for_spide_num > 0:  # 如果待爬列表里有QQ则继续抓取
            index1 = self.my_messages.step  # 待爬QQ列表太大，出于性能考虑，采用下标的方式取QQ
            if index1 > self.my_messages.qq_for_spide_num:
                index1 = self.my_messages.qq_for_spide_num
            qqlist = self.my_messages.qq_for_spide[:index1]
            self.my_messages.qq_for_spide = self.my_messages.qq_for_spide[index1:]
            self.my_messages.qq_for_spide_num -= index1

            pools = ThreadPool(self.my_messages.thread_num_QQ)
            pools.map(self.store_dairy, qqlist)  # 开启线程
            pools.close()
            pools.join()

            result = self.my_messages.backups()  # 备份
            print time.ctime(), "备份成功！（已爬：%d  待爬：%d  失败：%d）" % result

    def store_dairy(self, qq):
        """ 获取空间信息，保存到本地 """
        try:
            spidermessage = public_methods.SpiderMessage()
            blogspider = blog_spider.BlogSpider(spidermessage, self.changer)  # 新建一个日志爬虫对象
            moodspider = mood_spider.MoodSpider(spidermessage, self.changer)  # 新建一个说说爬虫对象
            friendspider = friend_spider.FriendSpider(spidermessage)  # 新建一个好友爬虫对象
            informationspider = information_spider.InformationSpider(spidermessage, self.changer)  # 新建一个个人信息爬虫对象
            self.changer.changeQQ(spidermessage, qq)  # 对于待爬的每个QQ，更换QQ登录
            text_information = informationspider.beginer()  # 开始抓取个人信息
            if text_information:
                text_blog = blogspider.beginer()  # 开始抓取QQ的日志
                text_mood = moodspider.beginer()  # 开始抓取QQ的说说
                text_friend = friendspider.beginer()  # 开始抓取QQ的好友
                if text_blog:
                    try:
                        self.db.Blog.insert(text_blog)
                        text_information["Blogs_WeGet"] = len(text_blog)
                    except Exception, e:
                        pass
                if text_mood:
                    try:
                        self.db.Mood.insert(text_mood)
                        text_information["Moods_WeGet"] = len(text_mood)
                    except Exception, e:
                        pass
                if text_friend:
                    try:
                        self.db.Friend.insert(text_friend)
                        text_information["FriendsNum"] = len(text_friend) - 2  # 去掉"_id"和"Num"两个字段，剩下的就是Friend了
                    except Exception, e:
                        pass
                self.db.Information.insert(text_information)
                print "Downloading success:%s (Friends:%d, Blogs:%d, Moods:%d)" % (
                    qq, text_information["FriendsNum"], text_information["Blogs_WeGet"],
                    text_information["Moods_WeGet"])
                self.my_messages.qq_had_spided.append(qq)
                try:
                    for elem in spidermessage.newQQ:
                        if not self.my_messages.qqbitset[int(elem)]:  # 判断该QQ是否已经爬过
                            self.my_messages.qqbitset[int(elem)] = 1
                            self.my_messages.qq_for_spide.append(elem)  # 加入待爬列表
                            self.my_messages.qq_for_spide_num += 1
                except Exception, e:
                    pass
            else:
                self.my_messages.qq_fail_spided.append(qq)
        except Exception, e:
            self.my_messages.qq_fail_spided.append(qq)
