# encoding=utf-8
import re
import datetime


class InformationSpider(object):
    """ 功能：爬取QQ个人信息（和空间信息） """

    def __init__(self, spiderMessage, changer):
        self.message = spiderMessage
        self.changer = changer
        self.hash_gender = {0: 'Unknown', 1: '男', 2: '女'}
        self.hash_constellation = {0: '白羊座', 1: '金牛座', 2: '双子座', 3: '巨蟹座', 4: '狮子座', 5: '处女座', 6: '天秤座', 7: '天蝎座',
                                   8: '射手座', 9: '魔羯座', 10: '水瓶座', 11: '双鱼座'}
        self.hash_bloodtype = {0: 'Unknown', 1: 'A', 2: 'B', 3: 'O', 4: 'AB', 5: 'Others'}
        self.hash_marriage = {0: 'Unknown', 1: '单身', 2: '已婚', 3: '保密', 4: '恋爱中', 5: '已订婚', 6: '分居', 7: '离异'}

    def beginer(self):
        failure = 0
        while failure < self.message.fail_time:
            myInformation = {}
            try:
                myInformation["_id"] = self.message.qq
                myInformation["Blogs_WeGet"] = 0
                myInformation["Moods_WeGet"] = 0
                myInformation["FriendsNum"] = 0
                result1 = self.get_personal_information(myInformation)  # 获取个人信息
                result2 = self.get_qzone_information0(myInformation)  # 获取空间信息
                result3 = self.get_qzone_information1(myInformation)  # 获取空间访问量
                if not (result1 and result2 and result3):  # 如果个人信息或者空间信息获取失败
                    return {}
                return myInformation
            except Exception:
                failure += 1
        return {}  # 如果失败次数太大

    def get_personal_information(self, information):
        """ 获取个人信息 """
        url00 = "http://base.s2.qzone.qq.com/"  # 此请求有两种域名情况
        url01 = "http://user.qzone.qq.com/p/base.s2/"
        url1 = "cgi-bin/user/cgi_userinfo_get_all?uin=%s&vuin=%s&fupdate=1&g_tk=%s" % (
            self.message.qq, self.message.account, str(self.message.gtk))
        r = self.message.s.get(url00 + url1, timeout=self.message.timeout)
        if r.status_code == 403:
            r = self.message.s.get(url01 + url1, timeout=self.message.timeout)
            if r.status_code == 403:
                return False
        text = r.text
        while u'请先登录' in r.text:  # Cookie失效
            try:
                self.changer.changeCookie(self.message)
                url1 = "cgi-bin/user/cgi_userinfo_get_all?uin=%s&vuin=%s&fupdate=1&g_tk=%s" % (
                    self.message.qq, self.message.account, str(self.message.gtk))
                r = self.message.s.get(url00 + url1, timeout=self.message.timeout)
                if r.status_code == 403:
                    r = self.message.s.get(url01 + url1, timeout=self.message.timeout)
                    if r.status_code == 403:
                        return False
                text = r.text
            except Exception, e:
                print "InformationSpider.get_personal_information:获取Cookie失败，此线程关闭！"
                exit()
        gender = re.findall('"sex":(\d+)', text)  # 性别
        age = re.findall('"age":(\d+)', text)  # 年龄
        birthday = re.findall('"birthday":"(.*?)"', text)  # 生日
        birthyear = re.findall('"birthyear":(\d+)', text)  # 出生年
        constellation = re.findall('"constellation":(\d+)', text)  # 星座
        bloodtype = re.findall('"bloodtype":(\d+)', text)  # 血型
        marriage = re.findall('"marriage":(\d+)', text)  # 婚姻状况
        living_country = re.findall('"country":"(.*?)"', text)  # 居住地（国家）
        living_province = re.findall('"province":"(.*?)"', text)  # 居住地（省份）
        living_city = re.findall('"city":"(.*?)"', text)  # 居住地（城市）
        hometown_country = re.findall('"hco":"(.*?)"', text)  # 故乡（国家）
        hometown_provine = re.findall('"hp":"(.*?)"', text)  # 故乡（省份）
        hometown_city = re.findall('"hc":"(.*?)"', text)  # 故乡（城市）
        career = re.findall('"career":"(.*?)"', text)  # 职业
        company = re.findall('"company":"(.*?)"', text)  # 公司名称
        company_country = re.findall('"cco":"(.*?)"', text)  # 公司地址（国家）
        company_province = re.findall('"cp":"(.*?)"', text)  # 公司地址（省份)
        company_city = re.findall('"cc":"(.*?)"', text)  # 公司地址（城市）
        company_address = re.findall('"cb":"(.*?)"', text)  # 公司详细地址

        try:
            information["Gender"] = self.hash_gender[int(gender[0])]
        except Exception:
            information["Gender"] = "Unknown"
        try:
            information["Age"] = int(age[0])
        except Exception:
            information["Age"] = -1
        try:
            str_birthday = str(birthyear[0]) + "-" + birthday[0]
            information["Birthday"] = datetime.datetime.strptime(str_birthday, "%Y-%m-%d") - datetime.timedelta(
                hours=8)
        except Exception:
            information["Birthday"] = datetime.datetime.strptime("1700-01-01", "%Y-%m-%d") - datetime.timedelta(
                hours=8)
        try:
            information["Constellation"] = self.hash_constellation[int(constellation[0])]
        except Exception:
            information["Constellation"] = "Unknown"
        try:
            information["Bloodtype"] = self.hash_bloodtype[int(bloodtype[0])]
        except Exception:
            information["Bloodtype"] = "Unknown"
        try:
            information["Marriage"] = self.hash_marriage[int(marriage[0])]
        except Exception:
            information["Marriage"] = "Unknown"
        try:
            information["Living_country"] = living_country[0]
        except Exception:
            information["Living_country"] = "Unknown"
        try:
            information["Living_province"] = living_province[0]
        except Exception:
            information["Living_province"] = "Unknown"
        try:
            information["Living_city"] = living_city[0]
        except Exception:
            information["Living_city"] = "Unknown"
        try:
            information["Hometown_country"] = hometown_country[0]
        except Exception:
            information["Hometown_country"] = "Unknown"
        try:
            information["Hometown_provine"] = hometown_provine[0]
        except Exception:
            information["Hometown_provine"] = "Unknown"
        try:
            information["Hometown_city"] = hometown_city[0]
        except Exception:
            information["Hometown_city"] = "Unknown"
        try:
            information["Career"] = career[0]
        except Exception:
            information["Career"] = "Unknown"
        try:
            information["Company"] = company[0]
        except Exception:
            information["Company"] = "Unknown"
        try:
            information["Company_country"] = company_country[0]
        except Exception:
            information["Company_country"] = "Unknown"
        try:
            information["Company_province"] = company_province[0]
        except Exception:
            information["Company_province"] = "Unknown"
        try:
            information["Company_city"] = company_city[0]
        except Exception:
            information["Company_city"] = "Unknown"
        try:
            information["Company_address"] = company_address[0]
        except Exception:
            information["Company_address"] = "Unknown"
        return True

    def get_qzone_information0(self, information):
        """ 获取空间信息 """
        url = "http://snsapp.qzone.qq.com/cgi-bin/qzonenext/getplcount.cgi?hostuin=" + self.message.qq
        r = self.message.s.get(url, timeout=self.message.timeout)
        if r.status_code == 403:
            return False
        text = r.text
        if "-4009" in text:
            return False
        rz = re.findall('"RZ":.*?(\d+)', text)  # 日志数
        ss = re.findall('"SS":.*?(\d+)', text)  # 说说数
        xc = re.findall('"XC":.*?(\d+)', text)  # 相册数
        ly = re.findall('"LY":.*?(\d+)', text)  # 留言数
        currentTime = re.findall('"now":(\d+)', text)  # 当前时间（Unix时间戳）

        try:
            information["Blog"] = int(rz[0])
        except Exception:
            information["Blog"] = -1
        try:
            information["Mood"] = int(ss[0])
        except Exception:
            information["Mood"] = -1
        try:
            information["Picture"] = int(xc[0])
        except Exception:
            information["Picture"] = -1
        try:
            information["Message"] = int(ly[0])
        except Exception:
            information["Message"] = -1
        try:
            information["CurrentTime"] = datetime.datetime.fromtimestamp(int(currentTime[0])) - datetime.timedelta(
                hours=8)
        except Exception:
            information["CurrentTime"] = datetime.datetime.strptime("1700-01-01", "%Y-%m-%d") - datetime.timedelta(
                hours=8)
        return True

    def get_qzone_information1(self, information):
        """ 获取空间访问量 """
        url = "http://r.qzone.qq.com/cgi-bin/main_page_cgi?uin=" + self.message.qq + "&param=3_" + self.message.qq + "_0%7C8_8_2116417293_0_1_0_0_1%7C16&g_tk=" + str(
            self.message.gtk)
        r = self.message.s.get(url, timeout=self.message.timeout)
        if r.status_code == 403:
            return False
        text = r.text
        if "-4009" in text:
            return False
        elif "module_8" not in text:
            try:
                self.changer.changeCookie(self.message)
            except Exception:
                print "InformationSpider.get_qzone_information1:获取Cookie失败，此线程关闭！"
                exit()
        try:
            pageView_temp1 = re.split('"modvisitcount"', text)[1]
            pageView_temp2 = re.split('"mod":0', pageView_temp1)[1]
            pageView = re.findall('"totalcount":(\d+)', pageView_temp2)  # 空间访问量
            information["PageView"] = pageView[0]
        except Exception:
            information["PageView"] = -1
        return True
