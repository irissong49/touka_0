#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, render_template, request
import socket,time
import json

f=open("config.json","r")
config=json.load(f)
f.close()


HOST=config['logicKernelHost']#'127.0.0.1'
PORT=config['logicKernelPort']#50007
WEBPORT=config['websitePort']


dialog=["<br>**NLP module unreachable**<br>>>>Switching to substitute mode Eliza...","<br>**logic kernel connected**<br>>>>Current Avaliable functional keyword: maimai/arknights/xx区风险查询(shanghai only)","<br>Hello, random stranger. I'm Touka."]



app = Flask(__name__)


def writelog(msg):
    fp = open("websiteLog.txt",'a')
    try:
        fp.write( time.asctime( time.localtime(time.time()) )+str(msg)+"\n")
    finally:
        fp.close()
    return


def sendmsg(cmd):

    c=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    c.connect((HOST,PORT))
    c.sendall(cmd.encode('utf-8'))      #把命令发送给对端
    writelog("sending to server:"+cmd)
    data=[]
    header=c.recv(10240)     #把接收的数据定义为变量
    server_reply_length=eval(header.decode('utf-8'))#how long this message will be 
    for i in range(server_reply_length):
        server_reply=c.recv(10240).decode('utf-8')
        #  server_reply="placeholder "
        data.append(server_reply)

    writelog("from server:"+str(data))
    c.close()
    return data

@app.route('/',methods=['GET','POST'])
def index():
    print("=0=")
    print(request.values.get('key'))
    if request.method == "POST":
        msg = request.form.get('text')

        if msg != "":
            writelog("from website:"+msg)
            server_reply=sendmsg(msg)
        dialog.append("You: "+msg)
        for r in server_reply:
            dialog.append(r)
        if msg =="clear!":
            for i in range(len(dialog)-3):#keep the first 3 stuff
                dialog.pop(-1)
    return render_template("playground3.html",line=dialog)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=WEBPORT, debug=True)
