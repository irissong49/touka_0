#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import re
#import sys, getopt
#import os
import requests
from bs4 import BeautifulSoup
import math
import geocoder
import pandas as pd
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import random

def damaidane():

    MAIMAI_URL="http://wc.wahlap.net/maidx/rest/location"


    #===pa===

    url=MAIMAI_URL

    headers = {
                    'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                }
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
    all_maimai=eval(soup.get_text())




    #====search====
    #究极relax之我会飞 

    print("输入省/直辖市：")
    province=input()
    print("稍等一会，在爬了在爬了")
    search_result=[]
    for maimai in all_maimai:
        if maimai['province']==province:
            search_result.append(maimai)
    for i in range(len(search_result)):
        print("\r{}/{}".format(i,len(search_result)),end="")
        geo=geocoder.arcgis(search_result[i]['address']).latlng
        search_result[i]["coordinate"]=geo




    print("输入地址：")
    address=input()
    target=geocoder.arcgis(address).latlng
    targetx,targety=target
    targetx=targetx*1000
    targety=targety*1000

    empty_list=[]
    print("稍等一会，在算了在算了")
    for i in range(len(search_result)):
        print("\r{}/{}".format(i,len(search_result)),end="")
        if type(search_result[i]['coordinate'])!=list:
            empty_list.append(i)
            continue
        x,y=search_result[i]['coordinate']
        x=1000*x
        y=1000*y
        dis=math.sqrt(pow(x-targetx,2)+pow(y-targety,2))

        search_result[i]['dis_to_target']=dis

    for i in empty_list:
        tmp=search_result.pop(i)
        print("{}地图上找不到坐标，没算进去".format(tmp['arcadeName']))

    print("到{}最近的maimaiDX排序如下：".format(address))
    distance_ranking=sorted(search_result,key=lambda x:x['dis_to_target'])


    #===show===

    print(pd.DataFrame(distance_ranking))
    return

def aknz():
    #a temporary search
    #搜搜舟，搞中文需要编码
    REP_NOT_FOUND="invalid name, totally."
    REP_404="seems the website is broken."

    char_name=input()


    from urllib.parse import urlencode
    import requests
    from bs4 import BeautifulSoup
    
    payload = {"": char_name}
    url="https://prts.wiki/w/"+urlencode(payload)[1:]
    headers = {
                    'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                }
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
    if res.__repr__() == '<Response [404]>':
        #加强错字助手
        payload = {'wd':u'明日方舟 '+char_name}

        url = 'http://www.baidu.com/s'

        res = requests.get(url, params=payload, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')

        raw_content=soup.get_text().split("\n")
        filtered_content=[]
        result=-1
        for content in raw_content:
            if '仍然搜索' in content:
                result=content.split("\xa0")
                break
        #百度也不知道你在说啥
        if result==-1:
            print(REP_NOT_FOUND)
        char_name=result[1].split('明日方舟')[1].replace('”','').replace(" ","").replace('“','')
        
        payload = {"": char_name}
        url="https://prts.wiki/w/"+urlencode(payload)[1:]
        headers = {
                        'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                        '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    }
        res = requests.get(url,headers = headers)
        soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
        
        
    #valid name, but 404
    if res.__repr__() == '<Response [404]>':
            print("REP_404")

            
    #clear empty lines to a list
    raw_content=soup.get_text().split("\n")
    filtered_content=[]
    for content in raw_content:
        if content=="":
            continue
        else:
            filtered_content.append(content)
            
    #TODO:read a json from this  
    reformat_dict={
        '再部署时间':1,
        '初始部署费用':1,
        '阻挡数':1,
        '攻击间隔':1,
        '初始开放':'综合体检测试'
    }

    #create a real profile dict
    filtered_dict2={}
    for k,v in reformat_dict.items():
        if type(v)==int:
            filtered_dict2[k]=filtered_content[filtered_content.index(k):filtered_content.index(k)+v+1]
        else:
            filtered_dict2[k]=filtered_content[filtered_content.index(k):filtered_content.index(v)]
        
    print(filtered_dict2['初始开放'][1:])
    return

def main():
    line=0
    print("hi bro")
    print("say something")
    print("I'm currently doing some work on maimai and arknights")
    print("or you can simply talk with me")


    while line!="end":
        line=input()
        line=line.lower()

        if line in ["end","bye","exit()"]:
            print("see you later, aligator")
            line="end"
        elif "maimai" in line:
            print("It's slow. Don't type anything before i tell you to do so. Also, please use chinese for this function.")
            damaidane()
        elif "arknights" in line:
            print("whose data do you wanna see?")
            aknz()
        else:
            if "what" in line or "how" in line or "do you" in line or "?" in line:
                print(line.split(" ")[-1].replace("?","")+" is not very important for me...")
            elif "yes" in line or "no" in line:
                print("I see.")
            elif "my" in line:
                print(line.replace("my","your")+"!")
            elif "i " in line:
                print(line.replace("i","you").replace("am","are")+"!")
            elif "i'm " in line:
                print(line.replace("i'm","you are")+"!")
            elif "you " in line:
                print(line.replace("you ","i").replace("are","am")+"!")
            elif "you're" in line:
                print(line.replace("you're","i am")+"!")
            else:
                tmp=random.randint(0,10)
                if tmp==0:
                    print("that's cool")
                elif tmp <4:
                    print(line+"?")
                elif tmp <8:
                    print(line+"!")
                elif tmp <9:
                    print("i like your idea")
                else:
                    print("please go on")
if __name__ == "__main__":
    main()
