# encoding=utf-8
import re
import requests


class FriendSpider(object):
    """ 功能：爬取该QQ的好友 """

    def __init__(self, spiderMessage):
        self.message = spiderMessage

    def beginer(self):
        friends = {"_id": self.message.qq}
        try:
            url = "http://ic2.s2.qzone.qq.com/cgi-bin/feeds/feeds_html_module?i_uin=" + self.message.qq + "&i_login_uin=3352188148&mode=4&previewV8=1&style=31&version=8&needDelOpr=true&transparence=true&hideExtend=false&showcount=5&MORE_FEEDS_CGI=http%3A%2F%2Fic2.s2.qzone.qq.com%2Fcgi-bin%2Ffeeds%2Ffeeds_html_act_all&refer=2&paramstring=os-mac|100"
            r = requests.get(url, timeout=self.message.timeout)
            friendlist = re.findall('href="http://user.qzone.qq.com/(\d{4,})"', r.text)
            friendlist = list(set(friendlist))  # 去重
            if friendlist.count(self.message.qq) > 0:
                friendlist.remove(self.message.qq)
        except Exception, e:
            self.message.newQQ = []
            return {}

        self.message.newQQ = friendlist
        num = 0
        for friend in friendlist:  # 以F1、F2……为字段名记录第一个、第二个好友
            num += 1
            friends['F%d' % num] = friend
        friends["Num"] = num
        return friends
