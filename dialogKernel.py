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

f=open("config.json","r")
config=json.load(f)
f.close()


HOST=config['logicKernelHost']#'127.0.0.1'
PORT=config['logicKernelPort']#50007
WEBPORT=config['websitePort']

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
            return(("????????????????????????",-1))
        #load data
        f = open("data/maimai_with_geo.json", "r")
        maimai_with_geo=json.load(f)
        f.close()
        
        #search geo coordinate 
        target=geocoder.arcgis(address).latlng
        if type(target)==type(None):
            return(("?????????????????????????????????????????????????????????????????????????????????",self.nearestMaimai_0))
        
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
            #reply.append("{}???????????????????????????????????????".format(tmp['arcadeName']))

        reply.append("????????????????????????????????????????????????{}?????????10???maimaiDX?????????????????????".format(address))
        distance_ranking=sorted(maimai_with_geo,key=lambda x:x['dis_to_target'])
        reply.append(pd.DataFrame(distance_ranking[0:11]).drop(columns = ['placeId','id','coordinate']).to_html(classes='data'))
        return((reply,-1))



    def nearestMaimai_1(self,s):
        province=s
        self.search_result=[]
        for maimai in self.all_maimai:
            if maimai['province']==province:
                self.search_result.append(maimai)
        if len(self.search_result)==0:
            return ("????????????????????????dx??????????????????????????????????????????????????????????????????/????????????",-1)

        for i in range(len(self.search_result)):
            print("\r{}/{}".format(i,len(self.search_result)),end="")

            geo=geocoder.arcgis(self.search_result[i]['address']).latlng
            self.search_result[i]["coordinate"]=geo

        return(("????????????????????????????????????????????????????????????????????????????",self.nearestMaimai_2))


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
            reply.append("{}???????????????????????????????????????".format(tmp['arcadeName']))

        reply.append("???{}?????????maimaiDX????????????xDDDD???".format(address))
        distance_ranking=sorted(self.search_result,key=lambda x:x['dis_to_target'])
        reply.append("<pre>"+pd.DataFrame(distance_ranking[0:15]).to_html(classes='data')+"</pre>")

        return((reply,-1))

def aknz(s):
    #a temporary search
    #?????????????????????????????????
    REP_NOT_FOUND="???????????????????????????????????????????????????"
    REP_404="prts?????????????????????"

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
        #??????????????????
        payload = {'wd':u'???????????? '+char_name}

        url = 'http://www.baidu.com/s'

        res = requests.get(url, params=payload, headers=headers, timeout=5)
        soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')

        raw_content=soup.get_text().split("\n")
        filtered_content=[]
        result=-1
        for content in raw_content:
            if '????????????' in content:
                result=content.split("\xa0")
                break
        #??????????????????????????????
        if result==-1:
            print(REP_NOT_FOUND)
        char_name=result[1].split('????????????')[1].replace('???','').replace(" ","").replace('???','')
        
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
        '???????????????':1,
        '??????????????????':1,
        '?????????':1,
        '????????????':1,
        '????????????':'??????????????????'
    }

    #create a real profile dict
    filtered_dict2={}
    for k,v in reformat_dict.items():
        if type(v)==int:
            filtered_dict2[k]=filtered_content[filtered_content.index(k):filtered_content.index(k)+v+1]
        else:
            filtered_dict2[k]=filtered_content[filtered_content.index(k):filtered_content.index(v)]
        
    reply=filtered_dict2['????????????'][1:]
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

def queryCovidRisk(searchPlace):
    url="https://diqu.gezhong.vip/api.php"
    headers = {
                    'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                }
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.content,"html.parser",from_encoding='gb18030')
    

    data=eval(soup.get_text())

    updateTime=data['data']['end_update_time']
    hList=data['data']['highlist']
    mList=data['data']['middlelist']


    searchResult=[]
    searchResult1=[]
    searchResult2=[]

    for l in hList:
        if searchPlace in l['area_name']:
            searchResult1.append([l['area_name'],l['communitys']])
    if len(searchResult1)!=0:
        searchResult=[["====???????????????====",":("]]+searchResult1
        
    for l in mList:
        if searchPlace in l['area_name']:
            searchResult2.append([l['area_name'],l['communitys']])
    if len(searchResult2)!=0:
        searchResult=searchResult+[["====???????????????====",":("]]+searchResult2    
        

    if searchResult==[]:
        result="???????????????{}???{}??????????????????????????????".format(updateTime,searchPlace)
    else:
        result=["?????????{}????????????{}?????????????????????".format(updateTime,searchPlace),"<pre>"+pd.DataFrame(searchResult).to_html(classes='data')+"</pre>"]#str(pd.DataFrame(searchResult))
        
    return((result,-1))

    """
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
    reply = soup.get_text().replace("\n","").split("????????????")[1].split("???????????????")[0].replace(" ","???")
    return ((reply,-1))
    """

def queryWeather(line):
    #??????????????????????????????????????????????????????
    searchString=line.replace("??????","")
    payload = {"": searchString}
    url="https://www.tianqiapi.com/api/?appid=29619714&appsecret=CaGkH2Pa&version=v9&city={}&ip=0&callback=0".format(urlencode(payload)[1:])
    headers = {
                    'Cookie':'OCSSID=4df0bjva6j7ejussu8al3eqo03',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    '(KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                    "content-type": "application/x-www-form-urlencoded"
                }
    res = requests.get(url,headers = headers)
    soup = BeautifulSoup(res.content,"html.parser",from_encoding='utf8')
    soup = eval(soup.get_text())
    reply=""
    if 'city' not in soup.keys():
        reply="????????????????????????????????????????????????????????? ??????????????????api???????????????"
    else:
        for day in soup["data"]:
            #l2=[day['day'].split("??????")[1].replace("???",""),day['wea_day'],day['tem1'],day['tem2'],day['hours'][4]['tem']]
            s="???{}????????????{},????????????{},????????????{},????????????{}".format(day['day'].split("??????")[1].replace("???",""),day['wea_day'],day['tem1'],day['tem2'],day['hours'][4]['tem'])
            reply=reply+s+"\n"
    return((reply,-1))

def rollDice(inputstr):
    param=(inputstr+" ")[2:]
    upperlimit=100
    if param!=" " and param[0]=="d":
        try: 
            tmp = int(param[1:])
            upperlimit=tmp
        except:
            pass     
    reply=str(random.randint(1,upperlimit))
            
    return((reply,-1))



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
            reply.append( "?????????????????????????????????????????????????????????????????????dx")
            registedEvent=maimai.nearestMaimai_0
        elif "arknights" in line:
            reply.append( "????????????????????????????????????")
            registedEvent=aknz
        elif "sudo -i" in line:
            reply,registedEvent=execText(line)
        elif "??????" in line:
            reply,registedEvent=queryCovidRisk(line[:2])
        elif "??????" in line:
            reply,registedEvent=queryWeather(line)
        elif line[0:2]==".r":
            reply,registedEvent=rollDice(line)
        elif line=="kill kernel":
            exit()

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
                reply.append(str(HOST)+":"+str(PORT))
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

