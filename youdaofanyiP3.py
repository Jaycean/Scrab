#!/usr/bin/env python
# -*- coding:utf-8 -*-

import urllib.request
import http.client
import requests
import json
import re

from urllib import request,parse

isOut = False
while True:
    if isOut == True:
        break
    
    # 通过抓包的方式获取的url，并不是浏览器上显示的url
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null"

    # 完整的headers
    headers = {
            "Accept" : "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With" : "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0",
            "Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
        }

    # 用户接口输入
    key = input(u"请输入需要翻译的文字:")
    if key == "CloseMe":
        isOut = True
        continue
    
    formdata = {
    "i":key,
    "from":"auto",
    "to":"auto",
    "smartresult":"dict",
    "client":"fanyideskweb",
    "salt":"1511219405946",
    "sign":"f8965f67a1d3eee8a69ddf8ccc5f582b",
    "doctype":"json",
    "version":"2.1",
    "keyfrom":"fanyi.web",
    "action":"FY_BY_REALTIME",
    "typoResult":"false"
    }
    data=bytes(parse.urlencode(formdata),encoding='utf-8')
    #利用Request将headers，dict，data整合成一个对象传入urlopen
    req = request.Request(url,data,headers,method='POST')
    response=request.urlopen(req)
    info = response.read().decode('utf-8')

    # 经过urlencode转码
    ##print(info)
    ##print(type(info))

    strRule = re.compile('"tgt":(.*?)}')
    info2 = strRule.findall(info)
    for i in info2:
               i = i.replace('"',"")
               #print(type(i))
               with open("youdaoP3.txt", 'ab+') as f:
                          f.write(i.encode('utf-8'))
                          f.write('\n'.encode('utf-8'))
