# coding=utf-8
import time
import sys
import init_messages
import spide_controller

if __name__ == '__main__':
    """ 作用：QQ_spider的开始文件 """
    try:
        reload(sys)
        sys.setdefaultencoding("utf-8")  # 设置编码格式
        my_messages = init_messages.InitMessages()  # 读取本地的爬虫信息，并对爬虫进行参数初始化
        spider = spide_controller.SpideController(my_messages=my_messages)  # spider对象控制生成多线程爬虫
        print time.ctime(), "----------> Initial work completed! Now, We start:\n\n"
        spider.beginer()  # 开始爬虫
    except Exception, e:
        print e
        print time.ctime()
    finally:
        my_messages.backups()  # 备份爬虫信息
        print time.ctime(), 'Done!'
