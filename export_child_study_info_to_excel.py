#coding:utf8
import MySQLdb
import xlwt
import json
import traceback
import smtplib  
from email.mime.text import MIMEText  
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders
import time

mailto_list = ["453430198@qq.com"] #收件人列表
mail_host = "smtp.163.com"  #设置服务器
mail_user = "zhangshibo706" #用户名
mail_sender = "Poilsmart mail notifier"
mail_pass = "x230t550"   #口令 
mail_postfix = "163.com"  #发件箱的后缀
mail_theme = "信息" #邮件主题
mail_user_format = "{mail_sender}<{mail_user}@{mail_postfix}>" #发件人格式
mail_content = "附件为截止到{date}的儿童学习信息"

def SendEmail(filename):
    if filename == None or len(filename) == 0:
        return
    me = mail_user_format.format(mail_sender=mail_sender, mail_user=mail_user, mail_postfix=mail_postfix)
    try:
        msg=MIMEMultipart()
        body = MIMEText(mail_content.format(date=time.strftime('%m-%d')), _subtype = 'plain',_charset = 'UTF-8')
        msg.attach(body)
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(filename, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename=%s' % filename)
        msg.attach(part)

        msg['Subject'] = mail_theme  
        msg['From'] = me
        msg['To'] = ";".join(mailto_list)
        msg['date']=time.strftime('%a, %d %b %Y %H:%M:%S') 
        print msg['date']
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user,mail_pass)  
        server.sendmail(me, mailto_list, msg.as_string())  
        server.close()
        print "Send main successed."
    except Exception, e:
        print "Send mail failed, ", e

class GetChildInfo():
    def __init__(self, conn, filename, outputColumn):
        self.conn = conn
        self.filename = filename
        self.outputColumn = outputColumn
        self.data = {}

    def _decode_list(data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

    def GetInfo(self):
        cursor = conn.cursor()
        sql = 'SELECT id, achievement_words FROM child'
        try:
            cursor.execute(sql)
            allResult = cursor.fetchall()
            totalLines = len(allResult)
            print 'Totle has %d lines.' % totalLines
            for result in allResult:
                child_id = result[0]
                studyinfo = result[1]
                if studyinfo == None:
                    # print 'Child %s doesn\'t has study info.' % child_id
                    totalLines = totalLines - 1
                    continue
                itemlist = []
                try:
                    gameModeDataInfo = json.loads(studyinfo)['game_mode_data']
                except Exception, e:
                    print 'Parse json error: ', e
                gameModeDataInfo = self._decode_dict(gameModeDataInfo)
                for item in self.outputColumn:
                    for validitem in self.outputColumn[item]:
                        try:
                            itemlist.append(gameModeDataInfo[item][validitem])
                        except Exception, e:
                            print 'match item with db data and configure error, ', e
                self.data[child_id] = itemlist
            print 'Actual has %d lines.' % totalLines
        finally:
            cursor.close()

    def Export(self):
        file = xlwt.Workbook(encoding='utf-8')
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        alignment.vert = xlwt.Alignment.VERT_CENTER
        style = xlwt.XFStyle()
        style.alignment = alignment
        table = file.add_sheet('sheet1')
        table.write_merge(0, 1, 0, 0, 'id', style)
        step = 1
        for item in self.outputColumn:
            nextstep = step + len(self.outputColumn[item])
            table.write_merge(0, 0, step, nextstep - 1, item, style)
            for eachitem in self.outputColumn[item]:
                table.write(1, step, eachitem, style)
                step = step + 1
            step = nextstep

        step = 0
        row = 2
        for item in self.data:
            table.write(row, step, item, style)
            step = step + 1
            for eachitem in self.data[item]:
                table.write(row, step, eachitem, style)
                step = step + 1
            row = row + 1
            step = 0
        file.save(self.filename)
        print 'Have write to file ' + self.filename


if __name__ == "__main__":
    mysql_conf = dict(
        host='127.0.0.1', 
        port = 3306, 
        user='root', 
        passwd='123456',
        db='wanquwoo',
        charset='utf8',
    )
    outputColumn = {
        "学习模式":[
            "time",
            "word_count",
        ],
        "单人模式":[
            "time",
            "word_count",
        ],
        "对战模式":[
            "time",
            "word_count",
        ],
    }
    conn = MySQLdb.connect(**mysql_conf)
    try:
        filename = 'appinfo_' + time.strftime('%Y-%m-%d') + '.xls'
        getChildInfo = GetChildInfo(conn, filename, outputColumn)
        getChildInfo.GetInfo()
        getChildInfo.Export()
        SendEmail(filename)
    except Exception, e:
        print 'Error, ', e
    finally:
        conn.close()
