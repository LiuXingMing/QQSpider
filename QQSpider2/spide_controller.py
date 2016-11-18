# coding=utf-8
import datetime
import blog_spider
import mood_spider
import friend_spider
import information_spider
import public_methods
from multiprocessing.dummy import Pool


class SpideController(object):
    """ 功能：控制去抓取日志、说说、个人信息，并保存到MongoDB """

    def __init__(self, my_messages=None):
        self.my_messages = my_messages
        self.changer = public_methods.Changing(self.my_messages)  # 新建一个对象，用来更换QQ，更换Cookie

    def beginer(self):
        restNum = self.my_messages.rconn.llen('QQSpider:QQForSpide')
        while restNum > 0:
            step = restNum if restNum < 1000 else 1000
            pool = Pool(self.my_messages.thread_num_QQ)
            pool.map(self.store_dairy, range(step))
            pool.close()
            pool.join()
            restNum = self.my_messages.rconn.llen('QQSpider:QQForSpide')

    def store_dairy(self, _):
        """ 获取空间信息，保存到本地 """
        try:
            qq = self.my_messages.rconn.rpop('QQSpider:QQForSpide')
            if not qq:
                return
        except Exception, e:
            return
        try:
            spidermessage = public_methods.SpiderMessage(qq)
            blogspider = blog_spider.BlogSpider(spidermessage, self.changer)
            moodspider = mood_spider.MoodSpider(spidermessage, self.changer)
            friendspider = friend_spider.FriendSpider(spidermessage)
            informationspider = information_spider.InformationSpider(spidermessage, self.changer)

            self.changer.changeQQ(spidermessage)  # 对于待爬的每个QQ，更换QQ登录
            text_information = informationspider.beginer()  # 开始抓取个人信息
            if text_information:
                text_blog = blogspider.beginer()  # 开始抓取QQ的日志
                text_mood = moodspider.beginer()  # 开始抓取QQ的说说
                text_friend = friendspider.beginer()  # 开始抓取QQ的好友
                if text_blog:
                    try:
                        text_information["Blogs_WeGet"] = len(text_blog)
                        self.my_messages.db['Blog'].insert(text_blog)
                    except Exception, e:
                        pass
                if text_mood:
                    try:
                        text_information["Moods_WeGet"] = len(text_mood)
                        self.my_messages.db['Mood'].insert(text_mood)
                    except Exception, e:
                        pass
                if text_friend:
                    try:
                        text_information["FriendsNum"] = len(text_friend) - 2  # 去掉"_id"和"Num"两个字段，剩下的就是Friend了
                        self.my_messages.db['Friend'].insert(text_friend)
                    except Exception, e:
                        pass
                try:
                    self.my_messages.db['Information'].insert(text_information)
                except Exception, e:
                    pass
                print "%s success:%s (Friends:%d, Blogs:%d, Moods:%d)" % (datetime.datetime.now(),
                                                                          qq, text_information["FriendsNum"],
                                                                          text_information["Blogs_WeGet"],
                                                                          text_information["Moods_WeGet"])
                for elem in spidermessage.newQQ:
                    if not self.my_messages.filter.isContains(elem):  # 判断该QQ是否已经爬过
                        self.my_messages.filter.insert(elem)
                        self.my_messages.rconn.lpush('QQSpider:QQForSpide', elem)  # 加入待爬列表
            else:
                print '%s failure:%s (None - http://user.qzone.qq.com/%s)' % (datetime.datetime.now(), qq, qq)
        except Exception, e:
            print '%s error:%s' % (datetime.datetime.now(), qq)
