#coding:utf-8
import MySQLdb
import json
import traceback
import smtplib  
from email.mime.text import MIMEText

serialCodeMaxUseTimes = 2 #一个序列号所允许得最大设备个数
accountIdMaxLoginTimes = 10 #一个账号所允许登陆的最大设备个数
mailto_list = ["453430198@qq.com"] #收件人列表
mail_host = "smtp.163.com"  #设置服务器
mail_user = "zhangshibo706@163.com" #用户名
mail_pass = "wca123456"   #口令 
mail_postfix = "163.com"  #发件箱的后缀
mail_theme = "账号异常信息" #邮件主题
mail_user_format = "{mail_user}<{mail_user}@{mail_postfix}>" #发件人格式
accountErrorPrefix = "这些用户账号情况异常：\n"
accountErrorFormat = "账号：{account_id}, 登陆设备数：{device_count}\n"
SerialsCodeErrorPrefix = "这些序列号情况异常：\n"
SerialsCodeErrorFormat = "序列号：{serial_code}, 扫描次数：{device_count}\n"

class NotNeedProcess(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class LockError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class StatisticsLogInfo():
    def __init__(self, conn):
        self.conn = conn;
        self.objectList = []

    def AddObject(self, object):
        self.objectList.append(object)

    def AddLock(self):
        cursor = self.conn.cursor()
        try:
            sql = 'LOCK TABLE `variables` WRITE, `activationstat` WRITE, `accountstat` WRITE, `accountlog` READ, `activationlog` READ'
            cursor.execute(sql)
        finally:
            cursor.close()

    def UnLock(self):
        cursor = self.conn.cursor()
        try:
            sql = 'UNLOCK TABLES'
            cursor.execute(sql)
        finally:
            cursor.close()

    def Start(self):
        errormsgList = []
        for object in self.objectList:
            try:
                self.AddLock()
                lastRowNum = object.GetLastRowNum(self.conn)
                newRowNum, errorInfo = object.GetNewDataAndUpdate(self.conn, lastRowNum)
                object.UpdataLastRowNum(self.conn, newRowNum)
                self.conn.commit()
                errormsgList.append(errorInfo)
            except NotNeedProcess, e:
                print e.value
            except Exception, e:
                print 'Error: ', e
                traceback.print_exc()
                self.conn.rollback()
            finally:
                self.UnLock()
        for errorInfo in errormsgList:
            self.SendEmail(errorInfo)


    def SendEmail(cls, errorInfo):
        if errorInfo == None or len(errorInfo) == 0:
            return
        me = mail_user_format.format(mail_user=mail_user, mail_postfix=mail_postfix)
        try:
            msg = MIMEText(errorInfo, _subtype = 'plain',_charset = 'UTF-8')
            msg['Subject'] = mail_theme  
            msg['From'] = me
            msg['To'] = ";".join(mailto_list)
            server = smtplib.SMTP()
            server.connect(mail_host)
            server.login(mail_user,mail_pass)  
            server.sendmail(me, mailto_list, msg.as_string())  
            server.close()
        except Exception, e:
            print "Send mail failed, ", e, "errorinfo is: ", errorInfo


class ActivationInfo():
    @classmethod
    def GetLastRowNum(cls, conn):
        cursor = conn.cursor()
        sql = 'SELECT activationlog_rowid FROM variables'
        print sql
        try:
            cursor.execute(sql)
            if cursor.rowcount == 0:
                sql = 'INSERT INTO variables (activationlog_rowid, accountlog_rowid) VALUES (%d, %d)' \
                        % (0, 0)
                print sql
                cursor.execute(sql)
                if cursor.rowcount != 1:
                    raise Exception('Insert into variables table failed.')
                return 0
            else:
                result = cursor.fetchone()
                return result[0]
        finally:
            cursor.close()

    @classmethod
    def GetNewDataAndUpdate(cls, conn, lastRowNum):
        cursor = conn.cursor()
        try:
            sql_maxid = 'SELECT MAX(id) AS id FROM activationlog'
            print sql_maxid
            cursor.execute(sql_maxid)
            if cursor.rowcount == 0:
                raise Exception('No data in accountlog')
            errorInfo = {}
            maxid = int(cursor.fetchone()[0])
            if maxid < lastRowNum:
                raise Exception('Max row num error')
            if maxid == lastRowNum:
                raise NotNeedProcess('data doesn\'t changed, not need process')

            sql_serial = 'SELECT serial_code, count(serial_code) AS use_times FROM (\
                        SELECT serial_code, device_id FROM activationlog \
                        WHERE account_id = 0 AND  id BETWEEN %d AND %d \
                        GROUP BY serial_code, device_id \
                    ) b GROUP BY serial_code' % (lastRowNum + 1, maxid)
            print sql_serial

            cursor.execute(sql_maxid)
            if cursor.rowcount == 0:
                raise Exception('No data in accountlog')
            errorInfo = {}
            maxid = int(cursor.fetchone()[0])
            if maxid < lastRowNum:
                raise Exception('Max row num error')
            if maxid == lastRowNum:
                raise NotNeedProcess('data doesn\'t changed, not need process')
            cursor.execute(sql_serial)
            result = cursor.fetchall()
            for serial_code, times in result:
                sql = 'SELECT serial_code, use_times FROM activationstat WHERE serial_code = "%s"' \
                        %  serial_code
                print sql
                cursor.execute(sql)
                if cursor.rowcount == 0:
                    sql = 'INSERT INTO activationstat (serial_code, use_times) VALUES ("%s", %d)' \
                        % (serial_code, int(times))
                    print sql
                    cursor.execute(sql)
                    if cursor.rowcount != 1:
                        raise Exception('Insert into table activationstat failed.')
                    if times > serialCodeMaxUseTimes:
                        errorInfo[serial_code] = int(times)
                else:
                    _, newTimes = cursor.fetchone()
                    times =  int(newTimes) + int(times)
                    sql = 'UPDATE activationstat SET use_times = %d WHERE serial_code = "%s"' \
                            % (int(times), serial_code)
                    print sql
                    cursor.execute(sql)
                    if cursor.rowcount != 1:
                        raise Exception('Update table activationstat failed.')
                if int(times) > serialCodeMaxUseTimes:
                        errorInfo[serial_code] = int(times)
            errormsg = ""
            if len(errorInfo) != 0:
                errormsg = errormsg + SerialsCodeErrorPrefix
                for item in errorInfo:
                    errormsg = errormsg + SerialsCodeErrorFormat.format(serial_code=item, device_count=errorInfo[item])
            return maxid, errormsg
        finally:
            cursor.close()

    @classmethod
    def UpdataLastRowNum(cls, conn, newRowNum):
        cursor = conn.cursor()
        sql = 'UPDATE variables SET activationlog_rowid = %d' \
                % int(newRowNum)
        print sql
        try:
            cursor.execute(sql)
            if cursor.rowcount != 1:
                raise Exception('Update variables table failed.')
        finally:
            cursor.close()

    @classmethod
    def SendEmail(cls, errorInfo):
        if len(errorInfo) == 0:
            return
        else:
            print errorInfo

class AccountInfo():
    @classmethod
    def GetLastRowNum(cls, conn):
        cursor = conn.cursor()
        sql = 'SELECT accountlog_rowid FROM variables'
        print sql
        try:
            cursor.execute(sql)
            if cursor.rowcount == 0:
                sql = 'INSERT INTO variables (activationlog_rowid, accountlog_rowid) VALUES (%d, %d)' \
                        % (0, 0)
                print sql
                cursor.execute(sql)
                if cursor.rowcount != 1:
                    raise Exception('Insert into variables table failed.')
                return 0
            else:
                result = cursor.fetchone()
                return result[0]
        finally:
            cursor.close()

    @classmethod
    def GetNewDataAndUpdate(cls, conn, lastRowNum):
        cursor = conn.cursor()
        try:
            sql_maxid = 'SELECT MAX(id) AS id FROM accountlog'
            print sql_maxid
            cursor.execute(sql_maxid)
            if cursor.rowcount == 0:
                raise Exception('No data in accountlog')
            errorInfo = {}
            maxid = int(cursor.fetchone()[0])
            if maxid < lastRowNum:
                raise Exception('Max row num error')
            if maxid == lastRowNum:
                raise NotNeedProcess('data doesn\'t changed, not need process')

            sql_deviceid = 'SELECT account_id, DATE_FORMAT(time, "%%Y-%%m-01") AS logintime, device_id, count(device_id) AS times \
                            FROM accountlog \
                            WHERE device_id <> "" AND id BETWEEN %d AND %d \
                            GROUP BY account_id, device_id, logintime \
                            ORDER BY account_id, logintime' % (lastRowNum + 1, maxid)

            sql_appversion = 'SELECT account_id, DATE_FORMAT(time, "%%Y-%%m-01") AS logintime, app_version \
                              FROM accountlog \
                              WHERE id BETWEEN %d AND %d \
                              GROUP BY account_id, logintime, app_version \
                              ORDER BY account_id' % (lastRowNum + 1, maxid)
            
            print sql_deviceid
            print sql_appversion
            
            cursor.execute(sql_deviceid)
            device_info = cursor.fetchall()
            cursor.execute(sql_appversion)
            app_info = cursor.fetchall()
            
            accountToDeviceId = {}
            for accountId, loginTime, deviceId, deviceCount in device_info:
                if accountId not in accountToDeviceId:
                    accountToDeviceId[accountId] = {}
                if loginTime not in accountToDeviceId[accountId]:
                    accountToDeviceId[accountId][loginTime] = {}
                accountToDeviceId[accountId][loginTime][deviceId] = deviceCount

            accountToApp = {}
            for accountId, loginTime, appInfo in app_info:
                if accountId not in accountToApp:
                    accountToApp[accountId] = {}
                if loginTime not in accountToApp[accountId]:
                    accountToApp[accountId][loginTime] = []
                accountToApp[accountId][loginTime].append(appInfo)

            for accountId in accountToDeviceId:
                deviceIdDict = accountToDeviceId[accountId]
                for logindate in deviceIdDict:
                    deviceInfo = deviceIdDict[logindate]
                    sql_account = 'SELECT account_id, `year_month`, login_count, app_count, \
                                   device_count, device_details, app_details \
                                   FROM accountstat \
                                   WHERE account_id = %d AND `year_month` = "%s"' \
                                   % (accountId, logindate)
                    print sql_account
                    cursor.execute(sql_account)
                    if cursor.rowcount == 0:
                        applist = accountToApp[accountId][logindate]
                        account_id = accountId
                        year_month = logindate
                        login_count = reduce(lambda x, y: x + y, [int(deviceInfo[var]) for var in deviceInfo])
                        app_count = len(applist)
                        device_count = len(deviceInfo)
                        device_details = json.dumps(deviceInfo)
                        app_details = ','.join(applist)
                        sql = 'INSERT INTO accountstat (account_id, `year_month`, login_count, \
                               app_count, device_count, device_details, app_details) \
                               VALUES ({account_id}, "{year_month}", {login_count}, {app_count}, \
                               {device_count}, \'{device_details}\', \'{app_details}\')' \
                               .format(**locals())
                        print sql
                        cursor.execute(sql)
                        if cursor.rowcount != 1:
                            raise Exception('Insert into table accountstat failed.')
                    elif cursor.rowcount == 1:
                        oldAccountInfoList = cursor.fetchone()
                        old_login_count,\
                        old_app_count,\
                        old_device_count,\
                        old_device_details,\
                        old_app_details = oldAccountInfoList[2:]

                        old_device_dict = json.loads(old_device_details)
                        old_app_list = old_app_details.split(',')

                        new_app_list = accountToApp[accountId][logindate]
                        applist = list(set(old_app_list).union(set(new_app_list)))

                        for item in deviceInfo:
                            new_device_count = deviceInfo[item]
                            if item in old_device_dict:
                                old_device_count = old_device_dict[item]
                                old_device_dict[item] = old_device_count + new_device_count
                            else:
                                old_device_dict[item] = new_device_count

                        account_id = accountId
                        login_count = reduce(lambda x, y: x + y, [int(old_device_dict[var]) for var in old_device_dict])
                        device_count = len(old_device_dict)
                        device_details = json.dumps(old_device_dict)
                        app_count = len(applist)
                        app_details = ','.join(applist)
                        sql = 'UPDATE accountstat \
                               SET login_count = {login_count}, \
                               app_count = {app_count}, \
                               device_count = {device_count}, \
                               device_details = \'{device_details}\', \
                               app_details = \'{app_details}\' \
                               WHERE account_id = {account_id}'\
                               .format(**locals())
                        print sql
                        cursor.execute(sql)
                        if cursor.rowcount != 1:
                            raise Exception('Update table accountstat failed.')
                    else:
                        raise Exception('There is more than one info in accountstat which accountid = %d, year_month = %s' \
                               % (accountId, logindate))

                sql_account_all_data = 'SELECT device_details \
                               FROM accountstat \
                               WHERE account_id = %d' \
                               % (accountId)
                print sql_account_all_data
                cursor.execute(sql_account_all_data)
                result = cursor.fetchall()
                thisAccountAllDeviceList = []
                for accountInfoEach in result:
                    oneMonthInfo = accountInfoEach[0]
                    oneMonthInfoDict = json.loads(oneMonthInfo)
                    oneMonthInfoList = [var for var in oneMonthInfoDict]
                    thisAccountAllDeviceList = list(set(oneMonthInfoList).union(set(thisAccountAllDeviceList)))

                if len(thisAccountAllDeviceList) > accountIdMaxLoginTimes:
                    errorInfo[accountId] = len(thisAccountAllDeviceList)
            
            errormsg = ""
            if len(errorInfo) != 0:
                errormsg = errormsg + accountErrorPrefix
                for item in errorInfo:
                    errormsg = errormsg + accountErrorFormat.format(account_id=item, device_count=errorInfo[item])
            return maxid, errormsg
        finally:
            cursor.close()

    @classmethod
    def UpdataLastRowNum(cls, conn, newRowNum):
        cursor = conn.cursor()
        sql = 'UPDATE variables SET accountlog_rowid = %d' \
                % int(newRowNum)
        print sql
        try:
            cursor.execute(sql)
            if cursor.rowcount != 1:
                raise Exception('Update variables table failed.')
        finally:
            cursor.close()

    @classmethod
    def SendEmail(cls, errorInfo):
        if len(errorInfo) == 0:
            return
        else:
            print errorInfo

if __name__ == "__main__":
    mysql_conf = dict(
        host='120.25.76.162', 
        port = 3306, 
        user='root', 
        passwd='123456',
        db='wanquwoo',
        charset='utf8',
    )
    # with MySQLdb.connect(**mysql_conf) as conn:
    conn = MySQLdb.connect(**mysql_conf)
    try:
        statisticsLogInfo = StatisticsLogInfo(conn)
        statisticsLogInfo.AddObject(ActivationInfo)
        statisticsLogInfo.AddObject(AccountInfo)
        statisticsLogInfo.Start()
    finally:
        conn.close()
