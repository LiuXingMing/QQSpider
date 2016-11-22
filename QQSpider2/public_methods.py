# encoding=utf-8
import requests
import time
import json
import random
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from yundama import identify


class SpiderMessage(object):
    """ 功能：爬虫的参数信息（日志、说说、个人信息、好友四个爬虫共用）"""

    def __init__(self, qq):
        self.s = requests.Session()
        self.qq = qq  # 要爬的QQ
        self.account = ''  # 用来登录的QQ账号
        self.password = ''  # 用来登录的QQ密码
        self.gtk = None
        self.newQQ = []  # 爬虫爬下来的QQ，准备加入待爬队列
        self.fail_time = None  # 失败几次不再循环
        self.timeout = None  # 超时时间


class Changing(object):
    """ 功能：更换QQ、更换Cookie """

    def __init__(self, my_messages):
        self.my_messages = my_messages

    def changeQQ(self, message):
        """ 更换用来登录的QQ（Cookie）"""
        redisKeys = self.my_messages.rconn.keys()
        while len(redisKeys) > 0:
            elem = random.choice(redisKeys)
            if 'Cookie' in elem:
                message.password = elem.split('--')[-1]
                message.account = elem.split('--')[0].split(':')[-1]
                cookie = json.loads(self.my_messages.rconn.get(elem))
                message.s.cookies.update(cookie)
                message.gtk = self.getGTK(cookie)
                message.fail_time = self.my_messages.fail_time
                message.timeout = self.my_messages.timeout
                return True
            else:
                redisKeys.remove(elem)
        return False

    def changeCookie(self, message):
        """ Cookie失效时进行更换Cookie """
        account = message.account
        password = message.password
        cookie = getCookie(account, password)  # 根据QQ号和密码获取Cookie
        if cookie:
            message.s.cookies.update(json.loads(cookie))
            self.my_messages.rconn.set('QQSpider:Cookies:%s--%s' % (account, password), cookie)
        else:  # 如果获取失败，则更换一个QQ的Cookie
            self.my_messages.rconn.delete('QQSpider:Cookies:%s--%s' % (account, password))
            cookieNum = ''.join(self.my_messages.rconn.keys()).count('Cookies')
            print '一个Cookie失效，且重新获取失败，剩余Cookie数: %s' % cookieNum
            if cookieNum > self.my_messages.thread_num_QQ:
                self.changeQQ(message)
            else:  # 如果已有Cookie数比爬虫线程还小，则报警Cookie不够，并关闭线程。
                print "QQ的Cookie缺货啦！！！！！！！！！！"
                exit()

    def getGTK(self, cookie):
        """ 根据cookie得到GTK """
        hashes = 5381
        for letter in cookie['p_skey']:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff


def getCookie(account, password, dama=False):
    """ 根据QQ号和密码获取cookie """
    failure = 0
    while failure < 2:
        try:
            dcap = dict(DesiredCapabilities.PHANTOMJS)
            dcap["phantomjs.page.settings.userAgent"] = (
                "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
            )
            browser = webdriver.PhantomJS(desired_capabilities=dcap)
            browser.get('http://qzone.qq.com/')

            try:
                access = browser.find_element_by_id('guideSkip')  # 继续访问触屏版按钮
                access.click()
                time.sleep(1)
            except Exception, e:
                pass

            account_input = browser.find_element_by_id('u')  # 账号输入框
            password_input = browser.find_element_by_id('p')  # 密码输入框
            go = browser.find_element_by_id('go')  # 登录按钮
            account_input.clear()
            password_input.clear()
            account_input.send_keys(account)
            password_input.send_keys(password)
            go.click()
            time.sleep(2)

            while '验证码' in browser.page_source:
                try:
                    print '需要处理验证码！'
                    browser.save_screenshot('verification.png')
                    if not dama:  # 如果不需要打码，则跳出循环
                        break
                    iframes = browser.find_elements_by_tag_name('iframe')
                    try:
                        browser.switch_to_frame(iframes[1])
                        input_verification_code = browser.find_element_by_id('cap_input')
                        submit = browser.find_element_by_id('verify_btn')
                        verification_code = identify()
                        print '验证码识别结果: %s' % verification_code
                        input_verification_code.clear()
                        input_verification_code.send_keys(verification_code)
                        submit.click()
                        time.sleep(1)
                    except Exception, e:
                        break
                except Exception, e:
                    browser.quit()
                    return ''
            if browser.title == 'QQ空间':
                cookie = {}
                for elem in browser.get_cookies():
                    cookie[elem['name']] = elem['value']
                print 'Get the cookie of QQ:%s successfully!(共%d个键值对)' % (account, len(cookie))
                browser.quit()
                return json.dumps(cookie)  # 将字典转成字符串
            else:
                print 'Get the cookie of QQ:%s failed!' % account
                return ''
        except Exception, e:
            failure = failure + 1
            if 'browser' in dir():
                browser.quit()
        except KeyboardInterrupt, e:
            raise e
    return ''
