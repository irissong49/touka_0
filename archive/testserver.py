#!/usr/bin/python
import socket   #socket模块
import os
import time
HOST='127.0.0.1'
PORT=50009
s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #定义socket类型，网络通信，TCP
s.bind((HOST,PORT))   #套接字绑定的IP与端口
s.listen(5)         #开始TCP监听,监听1个请求



def writelog(msg):
    fp = open("serverLog.txt",'a')
    try:
        fp.write( time.asctime( time.localtime(time.time()) )+str(msg)+"\n")
    finally:
        fp.close()
    return



while True:
    conn,addr=s.accept()   #接受TCP连接，并返回新的套接字与IP地址
    writelog("established a connection from:"+str(addr))
    #while True:
    data=conn.recv(1024)    #把接收的数据实例化
    writelog("received from clinet: "+data.decode('utf-8'))
    conn.sendall('received'.encode('utf-8'))   #否则就把结果发给对端（即客户端）
        #if data.decode('utf-8') == '1' :
    conn.close()     #关闭连接
s.close()