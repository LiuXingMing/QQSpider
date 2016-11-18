# coding=utf-8
import datetime
import BitVector
import public_methods


class InitMessages(object):
    """ 功能：信息初始化（读取保存在本地的信息，并设置爬虫的各项参数）。 """

    def __init__(self):
        self.myheader = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0',
                         'Referer': 'http://ctc.qzs.qq.com/qzone/newblog/blogcanvas.html'}  # 表头信息
        self.thread_num_QQ = 3  # 同时下载几个QQ的日志，每个QQ的访问使用不同的cookie登录
        self.thread_num_Blog = 2  # 同时下载QQ的几篇日志
        self.thread_num_Mood = 6  # 同时下载QQ的几条说说
        self.blog_after_date = datetime.datetime.strptime("2014-01-01", "%Y-%m-%d")  # 爬这个时间之后的日志
        self.mood_after_date = datetime.datetime.strptime("2015-01-01", "%Y-%m-%d")  # 爬这个时间之后的说说
        self.my_qq = self.readMyQQ()  # 我的QQ列表，用来登录
        self.qq_for_spide = self.readQQ("QQForSpider.txt")  # 待爬QQ列表
        self.qq_for_spide_num = len(self.qq_for_spide)  # 待爬QQ数量
        self.qq_had_spided = self.readQQ("QQHadSpided.txt")  # 已爬QQ列表
        self.qq_fail_spided = self.readQQ("QQFailSpided.txt")  # 爬取失败的QQ列表
        self.my_cookies = self.init_cookies(public_methods.GetCookie())  # QQ登录用的cookies
        self.cookie_num = len(self.my_cookies)  # 有效cookie的数量
        self.fail_time = 2  # 打开网页失败几次不再打开
        self.timeout = 3  # 打开网页设置几秒为超时
        self.step = 500  # 设置爬了step个QQ以后进行备份
        self.qqbitset = BitVector.BitVector(size=3500000000)  # 用35亿个位作判重
        self.init_qqbitset()
        if len(self.my_qq) == 0:
            print('QQ账号都没有cookie，请先获取cookie！')

    def readMyQQ(self, file_dir="./myQQ.txt"):
        """ 读取我的QQ信息（包括账号和密码） """
        qqlist = []
        f = open(file_dir, "r")
        for line in f.readlines():
            uin = {}
            line = line.split(' ')
            uin['no'] = line[0]
            uin['psw'] = line[1]
            qqlist.append(uin)
        f.close()
        return qqlist

    def readQQ(self, file_dir):
        """ 读取待爬QQ """
        qqlist = []
        with open(file_dir, 'r') as f:
            for line in f.readlines():
                qqlist.append(line.strip())
        return qqlist

    def writeQQ(self, text, file_dir, mode):
        """ 备份QQ（写入本地） """
        with open(file_dir, mode) as f:
            for qq in text:
                f.write(qq)
                f.write("\n")

    def init_cookies(self, getCookie):
        """ 获取Cookies """
        cookies = {}
        for qq in self.my_qq:
            cookie = getCookie.getCookie(account=qq['no'], password=qq['psw'])
            if cookie:  # 如果该QQ得到了cookie
                cookies[qq['no']] = cookie
            else:
                self.my_qq.remove(qq)
        return cookies

    def init_qqbitset(self):
        """ 初始化位内存，标识已爬、待爬、失败三个列表的QQ号为1 """
        for elem in self.qq_fail_spided:
            self.qqbitset[int(elem)] = 1
        for elem in self.qq_had_spided:
            self.qqbitset[int(elem)] = 1
        for elem in self.qq_for_spide:
            self.qqbitset[int(elem)] = 1

    def backups(self):
        """ 备份已爬、待爬、失败三个列表的QQ到本地 """
        len_had_spided = len(self.qq_had_spided)
        self.writeQQ(text=self.qq_had_spided, file_dir="QQHadSpided.txt", mode="w")
        len_fail_spided = len(self.qq_fail_spided)
        self.writeQQ(text=self.qq_fail_spided, file_dir="QQFailSpided.txt", mode="w")
        len_for_spide = len(self.qq_for_spide)
        self.writeQQ(text=self.qq_for_spide, file_dir="QQForSpider.txt", mode="w")
        return len_had_spided, len_for_spide, len_fail_spided
