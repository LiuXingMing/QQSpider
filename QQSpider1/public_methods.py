# encoding=utf-8
import requests
import time
from selenium import webdriver
import selenium.webdriver.support.ui as ui


class SpiderMessage(object):
    """ 功能：爬虫的参数信息（日志、说说、个人信息、好友四个爬虫共用）"""

    def __init__(self):
        self.s = requests.Session()
        self.qq = None  # 要爬的QQ
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

    def changeQQ(self, message, qq):
        """ 更换用来登录的QQ（Cookie）"""
        lastqq = self.my_messages.my_qq.pop()  # 更换一个QQ，用来登录
        self.my_messages.my_qq.insert(0, lastqq)
        message.qq = qq  # 日志爬虫要爬的QQ
        message.account = lastqq['no']  # 日志爬虫从my_messages中获取需要的登录信息
        message.password = lastqq['psw']
        temp_cookie = self.my_messages.my_cookies[lastqq['no']]
        message.gtk = self.getGTK(temp_cookie)
        message.s.cookies.update(temp_cookie)  # 更新Cookie
        message.fail_time = self.my_messages.fail_time
        message.timeout = self.my_messages.timeout

    def changeCookie(self, message):
        """ Cookie失效时进行更换Cookie """
        account = message.account
        password = message.password
        cookie = GetCookie().getCookie(account, password)  # 根据QQ号和密码获取Cookie
        if cookie:
            message.s.cookies.update(cookie)
            self.my_messages.my_cookies[account] = cookie
        else:  # 如果获取失败，则从换一个QQ的Cookie
            self.my_messages.my_qq.remove({'no': account, 'psw': password})
            self.my_messages.cookie_num -= 1
            if self.my_messages.cookie_num > self.my_messages.thread_num_QQ:
                self.changeQQ(message, message.qq)
            else:  # 如果已有Cookie数比爬虫线程还小，则报警Cookie不够，并关闭线程。
                print "QQ的Cookie缺货啦！！！！！！！！！！"
                exit()

    def getGTK(self, cookie):
        """ 根据cookie得到GTK """
        hashes = 5381
        for letter in cookie['p_skey']:
            hashes += (hashes << 5) + ord(letter)
        return hashes & 0x7fffffff


class GetCookie(object):
    def getCookie(self, account, password):
        """ 根据QQ号和密码获取cookie """
        failure = 0
        while failure < 2:
            try:
                browser = webdriver.PhantomJS()
                wait = ui.WebDriverWait(browser, 10)
                browser.get('http://qzone.qq.com/?s_url=http://user.qzone.qq.com/1813710279/')
                browser.switch_to_frame('login_frame')
                wait.until(lambda browser: browser.find_element_by_id('switcher_plogin'))
                plogin = browser.find_element_by_id('switcher_plogin')
                plogin.click()
                wait.until(lambda browser: browser.find_element_by_id('u'))
                u = browser.find_element_by_id('u')
                u.send_keys('%s' % (account))
                p = browser.find_element_by_id('p')
                p.send_keys('%s' % (password))
                wait.until(lambda browser: browser.find_element_by_xpath('//*[@id="login_button"]'))
                login = browser.find_element_by_xpath('//*[@id="login_button"]')
                time.sleep(2)
                login.click()
                time.sleep(1)
                try:
                    browser.switch_to_frame('vcode')
                    print 'Failed!----------------reason:该QQ首次登录Web空间，需要输入验证码！'
                    break
                except Exception:
                    pass
                try:
                    err = browser.find_element_by_id('err_m')
                    time.sleep(2)
                    d = err.text
                    print account, d
                    if u'您输入的帐号或密码不正确' in d:
                        print 'Failed!----------------reason:账号或者密码错误！'
                        break
                    if u'网络繁忙' in d:
                        time.sleep(2)
                except Exception, e:
                    # wait.until(lambda browser: browser.find_element_by_xpath(
                    #     '//*[@id="pageContent"]/div[1]/div[3]/div/div[2]/div[1]/div/b/b/textarea'))
                    # msg_b = browser.find_element_by_xpath(
                    #     '//*[@id="pageContent"]/div[1]/div[3]/div/div[2]/div[1]/div/b/b/textarea')
                    # msg_b.send_keys(u'Glory Be to Jehovah')
                    # wait.until(lambda browser: browser.find_element_by_xpath(
                    #     '//*[@id="pageContent"]/div[1]/div[3]/div/div[2]/div[1]/div/div[2]/div/div[2]/a'))
                    # btn = browser.find_element_by_xpath(
                    #     '//*[@id="pageContent"]/div[1]/div[3]/div/div[2]/div[1]/div/div[2]/div/div[2]/a')
                    # btn.click()
                    cookie = {}
                    for ck in browser.get_cookies():
                        cookie[ck['name']] = ck['value']
                    browser.quit()
                    print "Get the cookie of QQ:%s successfully!(共%d个键值对)" % (account, len(cookie))
                    return cookie
            except Exception:
                failure = failure + 1
            except KeyboardInterrupt, e:
                raise e
