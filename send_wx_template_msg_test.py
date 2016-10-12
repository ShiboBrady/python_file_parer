#!/usr/bin/env python3
import traceback, json
import http.client

def v1_weixin_send_template_msg(accessToken, msg):
  try:
      conn = http.client.HTTPSConnection('api.weixin.qq.com')
      conn.request('POST', '/cgi-bin/message/template/send?access_token={}'.format(accessToken), json.dumps(msg))
      res = conn.getresponse().read()
      res = json.loads(res.decode())
      print (res)
      print ('errcode = {}, errmsg = {}'.format(res['errcode'], res['errmsg']))
  except:
    print ('send template msg error.')
    traceback.print_exc()

def GetAcceccToken():
    try:
        conn = http.client.HTTPSConnection('api.weixin.qq.com')
        conn.request('GET', '/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'.format('wxfc2f0f8e03077125', 'ca506a71e2ff68af8374b9449928363e'), json.dumps(msg))
        res = conn.getresponse().read()
        res = json.loads(res.decode())
        if 'access_token' in res:
            print ('access_token = {}'.format(res['access_token']))
            return res['access_token']
        else:
            print ('errcode = {}, errmsg = {}'.format(res['errcode'], res['errmsg']))
            exit(1)
    except:
        print ('get access_token error.')
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    msg =  {
           "touser":"oI6mIs4xqajMjnz5LwaDLxz8Vgq0",
           "template_id":"MKWexvCfgao8_RjWY3RCjjD6KYhN6UK7LkXC8TlzVdA",
           "url":"http://120.25.76.162:8989/pinyin_share_main_page.html?code=abcdefg&pinyin=a",
           "data":{
                   "name": {
                       "value":"小趣",
                       "color":"#173177"
                   },
                   "time":{
                       "value":"5分23秒",
                       "color":"#173177"
                   }
           }
       }
    #v1_weixin_send_template_msg(GetAcceccToken(), msg)
    v1_weixin_send_template_msg('dfdfdf', msg)

