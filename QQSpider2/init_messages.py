# coding=utf-8
import redis
import pymongo
import datetime
import public_methods


class InitMessages(object):
    """ 功能：信息初始化（读取保存在本地的信息，并设置爬虫的各项参数） """

    def __init__(self):
        self.myheader = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
                         'Referer': 'http://ctc.qzs.qq.com/qzone/newblog/blogcanvas.html'}  # 表头信息
        self.db = pymongo.MongoClient('localhost', 27017)['QQ']
        self.rconn = redis.Redis('localhost', 6379)  # 存放种子和Cookie
        self.filter = Filter(self.rconn)  # 去重队列
        self.thread_num_QQ = 4  # 同时下载几个QQ的日志，每个QQ的抓取使用不同的cookie登录
        self.thread_num_Blog = 4  # 同时下载QQ的几篇日志
        self.thread_num_Mood = 8  # 同时下载QQ的几条说说
        self.blog_after_date = datetime.datetime.strptime("2015-01-01", "%Y-%m-%d")  # 爬这个时间之后的日志
        self.mood_after_date = datetime.datetime.strptime("2016-01-01", "%Y-%m-%d")  # 爬这个时间之后的说说
        self.readMyQQ()  # 读取我的QQ列表，用来登录
        self.readQQForSpide()  # 待爬QQ列表
        self.fail_time = 2  # 打开网页失败几次不再打开
        self.timeout = 5  # 打开网页设置几秒为超时

    def readMyQQ(self, file_dir="./myQQ.txt"):
        """ 读取我的QQ信息（账号、密码），存入redis的string，键值格式如 'QQ--密码':'cookie' """
        with open(file_dir, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip().replace(' ', '--')
                if self.rconn.get('QQSpider:Cookies:' + line) == None:  # 先判断redis是否已经有该账号
                    cookie = public_methods.getCookie(account=line.split('--')[0], password=line.split('--')[1])
                    if len(cookie) > 0:
                        self.rconn.set('QQSpider:Cookies:' + line, cookie)
        cookieNum = ''.join(self.rconn.keys()).count('Cookies')
        if cookieNum == 0:
            print('QQ账号都没有cookie，请先获取cookie！')
            exit()
        else:
            print '剩余Cookie数: %s' % cookieNum

    def readQQForSpide(self, file_dir='QQForSpider.txt'):
        """ 读取待爬QQ，存入rredis的list """
        with open(file_dir, 'r') as f:
            for line in f.readlines():
                line = line.strip()
                if not self.filter.isContains(line):  # 先去重
                    self.filter.insert(line)
                    self.rconn.lpush('QQSpider:QQForSpide', line)
        print '剩余待爬QQ数: %s' % self.rconn.llen('QQSpider:QQForSpide')


class Filter(object):
    def __init__(self, server, name='QQSpider:Filter'):
        self.server = server
        self.name = name

    def isContains(self, str_input):
        str_input = int(str_input)
        return self.server.getbit(self.name, str_input) if (0 < str_input) and (str_input < 4500000000) else 1

    def insert(self, str_input):
        str_input = int(str_input)
        if (0 < str_input) and (str_input < 4500000000):
            self.server.setbit(self.name, str_input, 1)
