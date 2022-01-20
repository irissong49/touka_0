#!/usr/bin/python
# -*- coding: UTF-8 -*-
#import re
#import sys, getopt
#import os
from logging import StreamHandler
from geocoder.locationiq import LocationIQResult
import requests
from bs4 import BeautifulSoup
import math
import geocoder
import pandas as pd
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
import random


import socket
import os
import time
import json
import sys

HOST='127.0.0.1'
PORT=50007

all_maimai=[]
search_result=[]

end_word_list=["exit()",":q","-1"]
pwbook={"q":"asbtw","y":"szmyn","v":"bctl"}



class redirect:
#capture standout print
    def __init__(self):
        self.content = []

    def write(self,str):
        if str!='\n':
            self.content.append(str)
    def flush(self):
        self.content = []


def passwordCheck(text):
    split_text=text.split(" ")
    if len(split_text)!=4:
        return False
    text=split_text[2]
    returntext=split_text[3]
    k=text[0]
    i=text[1]
    v=text[2]
    try:
        assert(pwbook[k][eval(i)]==v)
        assert(v!="-")
        pwbook[k]=pwbook[k].replace(v,"-")
    except:
        return False
    return returntext

class nearestMaimai():
    def __init__(self):
        self.MAIMAI_URL="http://wc.wahlap.net/maidx/rest/location"

        self.url=self.MAIMAI_URL

        self.headers = {
                            'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                            '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    }   
        self.all_maimai=[]
        self.search_result=[]
    def updateJson(self):
        #request
        res = requests.get(self.url,headers = self.headers)
        soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
        self.all_maimai=eval(soup.get_text())
        
        #dict by province , not used right now but save for future use
        #TODO: handle overtime error
        maimai_dict={}
        for i,maimai in enumerate(all_maimai):
            print("updating maimai geo data{}/{}".format(i, len(all_maimai)))
            thisprovince = maimai['province']
            geo=geocoder.arcgis(maimai['address']).latlng
            maimai["coordinate"]=geo
            if thisprovince in maimai_dict.keys():
                maimai_dict[thisprovince].append(maimai)
            else:
                maimai_dict[thisprovince]=[]
                maimai_dict[thisprovince].append(maimai)
        #all maimai with geo data
        maimai_with_geo=[]
        for k,v in maimai_dict.items():
            maimai_with_geo+=v
        #save
        out_file = open("data/maimai_province_dict.json", "w")
        json.dump(maimai_dict,out_file)  
        out_file.close()
        
        out_file = open("data/maimai_with_geo.json", "w")
        json.dump(maimai_dict,out_file)  
        out_file.close()
        return


    def nearestMaimai_0(self,address):
        reply=[]
        if address in end_word_list:
            return(("好，那就不查了。",-1))
        #load data
        f = open("data/maimai_with_geo.json", "r")
        maimai_with_geo=json.load(f)
        f.close()
        
        #search geo coordinate 
        target=geocoder.arcgis(address).latlng
        if type(target)==type(None):
            return(("我连接的数据库找不到这个地方，请换个详细点的地址试试。",self.nearestMaimai_0))
        
        targetx,targety=target
        targetx=targetx*1000
        targety=targety*1000
        empty_list=[]

        for i in range(len(maimai_with_geo)):
            if type(maimai_with_geo[i]['coordinate'])!=list:
                empty_list.append(maimai_with_geo[i])
                continue
            x,y=maimai_with_geo[i]['coordinate']
            x=1000*x
            y=1000*y
            dis=math.sqrt(pow(x-targetx,2)+pow(y-targety,2))
            maimai_with_geo[i]['dis_to_target']=dis
            
        #TODO: check if removed maimai is the same province with target. if yes, keep alert
        for tmp in empty_list:
            maimai_with_geo.remove(tmp)
            #reply.append("{}地图上找不到坐标，没算进去".format(tmp['arcadeName']))

        reply.append("部分地图上找不到坐标的没计入。到{}最近的10个maimaiDX机厅排序如下：".format(address))
        distance_ranking=sorted(maimai_with_geo,key=lambda x:x['dis_to_target'])
        reply.append(pd.DataFrame(distance_ranking[0:11]).to_html(classes='data'))
        return((reply,-1))



    def nearestMaimai_1(self,s):
        province=s
        self.search_result=[]
        for maimai in self.all_maimai:
            if maimai['province']==province:
                self.search_result.append(maimai)
        if len(self.search_result)==0:
            return ("要么是你们省没有dx要么是你打错了！再检查一下吧！汉字！不带‘省/市’字！",-1)

        for i in range(len(self.search_result)):
            print("\r{}/{}".format(i,len(self.search_result)),end="")

            geo=geocoder.arcgis(self.search_result[i]['address']).latlng
            self.search_result[i]["coordinate"]=geo

        return(("接下来的步骤很慢还请耐心等待！那么，详细的地址是?：",self.nearestMaimai_2))


    def nearestMaimai_2(self,s):
        address=s
        reply=[]
        target=geocoder.arcgis(address).latlng
        targetx,targety=target
        targetx=targetx*1000
        targety=targety*1000
        empty_list=[]
        for i in range(len(self.search_result)):
            #print("\r{}/{}".format(i,len(search_result)),end="")
            if type(self.search_result[i]['coordinate'])!=list:
                empty_list.append(i)
                continue
            x,y=self.search_result[i]['coordinate']
            x=1000*x
            y=1000*y
            dis=math.sqrt(pow(x-targetx,2)+pow(y-targety,2))

            self.search_result[i]['dis_to_target']=dis

        for i in empty_list:
            tmp=self.search_result.pop(i)
            reply.append("{}地图上找不到坐标，没算进去".format(tmp['arcadeName']))

        reply.append("到{}最近的maimaiDX排序如下：".format(address))
        distance_ranking=sorted(self.search_result,key=lambda x:x['dis_to_target'])
        reply.append(pd.DataFrame(distance_ranking[0:15]).to_html(classes='data'))

        return((reply,-1))

def aknz(s):
    #a temporary search
    #搜搜舟，搞中文需要编码
    REP_NOT_FOUND="……百度都猜不到你到底想打啥名字！"
    REP_404="prts好像坏掉了耶。"

    char_name=s

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
    #{start pattern: end pattern(str)/fixed line num for this attribute(int)}
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
        
    reply=filtered_dict2['初始开放'][1:]
    return((reply,-1))


def execText(text):
    text=passwordCheck(text)
    if text==False:
        return (("permission denied",-1))
    writelog("executing "+text)
    __console = sys.stdout
    r = redirect()
    sys.stdout = r
    try:
        exec(text)
        print("Success")
    except Exception as e:
        print("Exception:")
        print(str(e))
    finally:
        print("End")

    sys.stdout = __console
    reply=r.content
    return ((reply,-1))

def queryCovidRisk(text):
    headers = {
                    'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                }
    payload = {"": text}
    url="http://m.sh.bendibao.com/news/yqdengji/?qu="+urlencode(payload)[1:]
    #url="http://m.bendibao.com/news/yqdengji/city.php"
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
    reply = soup.get_text().replace("\n","").split("每日更新")[1].split("防疫工具箱")[0].replace(" ","是")
    return ((reply,-1))

def writelog(msg):
    fp = open("serverLog.txt",'a')
    try:
        fp.write( time.asctime( time.localtime(time.time()) )+str(msg)+"\n")
    finally:
        fp.close()
    return

def main():
    line=0
    s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.bind((HOST,PORT))
    s.listen(5)
    writelog("Server started listening...")
    registedEvent=-1
    
    maimai=nearestMaimai()

    #TODO:need to deal more with this part

    while True:
        conn,addr=s.accept()
        writelog("established a connection from:"+str(addr))
        reply=[]
        line=conn.recv(1024).decode('utf-8')
        writelog("received from clinet: "+line)

        line=line.lower()

        #====if there is a registed event====
        if registedEvent!=-1:
            #TODO:this part doesn't seem neat...
            r,nextEvent=registedEvent(line)
            reply.append(r)
            registedEvent=nextEvent

        #====logic for answer====
        elif line in ["end","bye","exit()",":q",":q!"]:
            reply.append( "see you later, alligator")
            writelog("===========end-of-this-connection===========")
            break
        elif "maimai" in line:
            #maimai=nearestMaimai()
            #r,registedEvent=maimai.nearestMaimai_0(line)
            #reply.append(r)
            reply.append( "请告诉我你现在的位置，我帮你看看附近有哪些舞萌dx")
            registedEvent=maimai.nearestMaimai_0
        elif "arknights" in line:
            reply.append( "想要查找哪位干员的资料？")
            registedEvent=aknz
        elif "sudo -i" in line:
            reply,registedEvent=execText(line)
        elif "风险" in line:
            reply,registedEvent=queryCovidRisk(line[:2])

        #==not the functional modules, start NLP(?)==
        else:
            if "what" in line or "how" in line or "do you" in line or "?" in line:
                reply.append( line.split(" ")[-1].replace("?","")+" ?... not very important for me...")
            elif "yes" in line or "no" in line:
                reply.append( "I see.")
            elif "my" in line:
                reply.append( line.replace("my","your")+"!")
            elif "i " in line:
                reply.append( line.replace("i","you").replace("am","are")+"!")
            elif "i'm " in line:
                reply.append( line.replace("i'm","you are")+"!")
            elif "you " in line:
                reply.append( line.replace("you ","i").replace("are","am")+"!")
            elif "you're" in line:
                reply.append( line.replace("you're","i am")+"!")
            elif "ip" in line:
                reply.append(str(HOST)+str(PORT))
            else:
                tmp=random.randint(0,10)
                if tmp==0:
                    reply.append( "that's cool")
                elif tmp <4:
                    reply.append( line+"?")
                elif tmp <8:
                    reply.append( line+"!")
                elif tmp <9:
                    reply.append( "i like your idea")
                else:
                    reply.append( "please go on")


        writelog("send to client:"+str(reply))
        if type(reply)==str:
            reply=[reply]
        conn.sendall(str(len(reply)).encode('utf-8'))
        for rr in reply:
            time.sleep(0.1)
            rr=str(rr).encode('utf-8')
            conn.sendall(rr)
        conn.close()
    s.close()

if __name__ == "__main__":
    main()

