from flask import Flask, render_template, request
import playground
import socket,time

import socket



dialog=["Hi, stranger."]


#!/usr/bin/env python
# -*- coding:utf-8 -*-


app = Flask(__name__)



@app.route('/',methods=['GET','POST'])
def index():
    if request.method == "POST":
        msg = request.form.get('text')
        server_reply="placeholder "
        dialog.append("You: "+msg)
        dialog.append(server_reply)
    return render_template("playground3.html",line=dialog)

if __name__ == '__main__':
    app.run('127.0.0.1', port=5000, debug=True)
