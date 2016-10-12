#coding:utf-8
import mysql.connector
import traceback
import smtplib
from email.mime.text import MIMEText
import time, datetime

# mailto_list = ["liuyuqi@360.cn", "lixin3-iri@360.cn", "wangerfei@360.cn"] #收件人列表
mailto_list = ["453430198@qq.com", "zhangshibo706@163.com"] #收件人列表
mailto_cc = []
mailto_bcc = ["zhangshibo@pilosmart.com"]
mail_host = "smtp.ym.163.com"  #设置服务器
mail_user = "service1@pilosmart.com" #用户名
mail_pass = "9bc8401d"   #口令 
mail_postfix = "pilosmart.com"  #发件箱的后缀
mail_theme = "AR应用统计数据" #邮件主题
mail_user_format = "{mail_user}<{mail_user}>" #发件人格式
mail_content = "{date}有{count}个账号激活。"

def getYesterday(day): 
    today = datetime.date.today()
    yesterday = today + datetime.timedelta(days = day)  
    return yesterday.strftime('%Y-%m-%d')

def writeToLogFile(msg):
    with open("send_result.log", "a", encoding='utf-8') as file:
        file.write(msg + '\n');

class StatisticsActiveInfo():
    def __init__(self, conn, startTime, endTime):
        self.conn = conn;
        self.startTime = startTime;
        self.endTime = endTime;
        self.formatYestodayDate = "{}年{}月{}日".format(*startTime.split('-'))

    def Run(self):
        try:
            cursor = self.conn.cursor()
            sql = 'SELECT count(*) as `count` \
                   FROM activationlog \
                   WHERE app_version LIKE "%360%" \
                   AND time > "{startTime}" AND time < "{endTime}" \
                   AND account_id != 0'.format(startTime=self.startTime, endTime=self.endTime)
            writeToLogFile('sql is: ' + sql)
            cursor.execute(sql)
            result = cursor.fetchone()[0]
            title = mail_theme
            content = mail_content.format(date = self.formatYestodayDate, count = result)
            writeToLogFile(content)
            self.SendEmail(title, content)
        except Exception as e:
            traceback.print_exc()

    def SendEmail(cls, title, content):
        me = mail_user_format.format(mail_user=mail_user, mail_postfix=mail_postfix)
        try:
            server = smtplib.SMTP(mail_host)
            server.login(mail_user,mail_pass)
            msg = MIMEText(content, _subtype = 'plain',_charset = 'UTF-8')
            # for item in mailto_list:
            msg['Subject'] = title  
            msg['From'] = me
            msg['To'] = ";".join(mailto_list)
            msg['Cc'] = ";".join(mailto_cc)
            msg['Bcc'] = ";".join(mailto_bcc)
            server.sendmail(me, mailto_list + mailto_cc + mailto_bcc, msg.as_string())
            server.close()
        except Exception as e:
            writeToLogFile("Send mail failed, " + str(e))

if __name__ == '__main__':
    mysql_conf = dict(
        host='mysql.wanquwoo.com', 
        port = 3306, 
        user='wanquwoo', 
        passwd='c41b51a2c20d19ece45e8a98466a3818',
        db='wanquwoo',
        charset='utf8',
    )
    startTime = getYesterday(-1)
    endTime = getYesterday(0)
    writeToLogFile('startTime: ' + startTime)
    writeToLogFile('endTime: ' + endTime)
    conn = mysql.connector.connect(**mysql_conf)
    try:
        statisticsActiveInfo = StatisticsActiveInfo(conn, startTime, endTime)
        statisticsActiveInfo.Run();
    finally:
        conn.close()