#!/usr/bin/env python
# -*- coding:utf-8 -*-
from flask import Flask, render_template, request
import socket,time

HOST='127.0.0.1'
PORT=50007

dialog=["Hi, stranger.\n I'm Touka. Talk to me.\n NLP module is not connected yet. But you can ask me things about MaiMai/Arknights."]
app = Flask(__name__)


#!/usr/bin/python
import socket
      #定义socket类型，网络通信，TCP
"""
HOST='127.0.0.1'
PORT=50009
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((HOST,PORT))       #要连接的IP与端口
"""

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
 
"""
def sendmsg(s,cmd):
    s.sendall(cmd.encode('utf-8'))      #把命令发送给对端
    writelog("sending to server:"+cmd)
    data=s.recv(1024)     #把接收的数据定义为变量
    writelog("from server:"+data.decode('utf-8'))
    return data


while 1:
    cmd=input("Please input cmd:")       #与人交互，输入命令
    s.sendall(cmd.encode('utf-8'))      #把命令发送给对端
    data=s.recv(1024)     #把接收的数据定义为变量
    print(data.decode('utf-8'))         #输出变量
    if cmd == '1' :
        break
s.close()   #关闭连接
"""


@app.route('/',methods=['GET','POST'])
def index():
    if request.method == "POST":
        msg = request.form.get('text')

        if msg != "":
            writelog("from website:"+msg)
            server_reply=sendmsg(msg)
        dialog.append("You: "+msg)
        for r in server_reply:
            dialog.append(r)
        if msg =="clear!":
            for i in range(len(dialog)):
                dialog.pop(-1)
    return render_template("playground3.html",line=dialog)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
