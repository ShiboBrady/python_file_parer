#!/usr/bin/env python3
import mysql.connector
import traceback, json, sys

def UpdateAchievement(kidId, pinyin, model):
	print ('Ready to update: ', kidId, pinyin, model)
	mysql_conf = dict(host='mysql.wanquwoo.com', database='wanquwoo', port = 3307, 
	    user='wanquwoo', passwd='c41b51a2c20d19ece45e8a98466a3818')
	conn = mysql.connector.MySQLConnection(**mysql_conf)
	try:
		cursor = conn.cursor()
		cursor.execute('SELECT achievement_pinyin FROM Child WHERE id = %s', (kidId,))
		if cursor.rowcount == 0:
			print ('Get kid %d error.', kidId)
			return
		data = json.loads(cursor.fetchone()['achievement_pinyin'])
		data['total']['pinyin'] = pinyin
		data['total']['model'] = model
		data = json.jumps(data, ensure_ascii=False, separators=(',', ':'))
		cursor.execute('UPDATE Child set achievement_pinyin=%s WHERE id = %s', (data, kidId))
		if cursor.rowcount == 1:
			conn.commit()
			print ('update successed.')
		else:
			print ('update error.')
	except:
		traceback.print_exc()
	finally:
		conn.close()

def GetParameter():
	if (len(sys.argv) != 4):
		print ('Usage: exec kidId pinyin model')
		exit(1)
	userInput = []
	for i in range(1, len(sys.argv)):
		userInput.append(sys.argv[i])
	print (userInput)
	return userInput

if __name__ == '__main__':
	UpdateAchievement(*GetParameter())