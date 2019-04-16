import sys
from PyQt5.QtWidgets import QApplication, \
    QAbstractItemView,QErrorMessage,QMessageBox, QWidget,QListWidget,QVBoxLayout,QHBoxLayout,QGridLayout,QTextEdit,QPushButton,QSizePolicy
from PyQt5.QtCore import pyqtSignal
from PyQt5 import  QtCore
from os import listdir
from os.path import isfile, join

import os, sys, _thread, socket

BACKLOG = 500  # how many pending connections queue will hold
MAX_DATA_RECV = 9999990  # max number of bytes we receive at once




class proxygui(QWidget):
    mypath = './data/'
    grpname=''
    site=''
    NonBLOCKED=[]
    def loadgrps(self):
        print(self.mypath)
        onlyfiles = [f for f in listdir(self.mypath) if isfile(join(self.mypath, f))]
        print(onlyfiles)
        return onlyfiles
    def loadsites(self):
        print(self.mypath)
        lines=[]
        with open(self.mypath + self.grpname, 'r') as text_file:
            lines = text_file.read().splitlines()
        print(lines)
        return lines

    def savetogrp(self):
        f = open(self.mypath+self.grpname, "a+")
        site=self.textEdit2.toPlainText()
        f.write(site+"\n")
        f.close()
        print("save "+site+"to"+self.grpname)
        self.list2.addItem(site)
        self.textEdit2.setText('')


    def delsite(self):
        if self.site != "":
            with open(self.mypath + self.grpname, 'r') as f:
                lines = f.read().splitlines()
            lines_2=[]
            os.remove(self.mypath + self.grpname)
            f = open(self.mypath + self.grpname, 'w')
            for s in lines:
                if s != self.site:
                    f.write(s+"\n")
            f.close()
            allsite = self.loadsites()
            self.list2.clear()
            for s in allsite:
                self.list2.addItem(s.strip())
            self.site=""

    def addgrp(self):
        print("clicked")
        gr = self.textEdit1.toPlainText()
        self.list.addItem(gr)
        self.textEdit1.setText('')
        file = open(self.mypath +gr, 'w')
        file.close()
        print("file "+gr+"created")

    def delgrp(self):
        print("del clicked")
        if self.grpname != "":
            #self.list.takeItem(self.grpname)
            os.remove(self.mypath +self.grpname)
            print("file "+self.grpname+" delete successful")
            self.grpname=""
            self.list.clear()
            onlyfiles = self.loadgrps()
            for s in onlyfiles:
                self.list.addItem(s)

    def selectsite(self, item):
        self.site=str(item.text())

    def selectgrp(self,item):
        print('click an item')
        print( str(item.text()))
        self.grpname=str(item.text())
        allsite=self.loadsites()
        self.list2.clear()
        for s in allsite:
            self.list2.addItem(s.strip())

    def running(self):
        print(self.grpname)
        allgroups=""
        items = self.list.selectedItems()
        self.NonBLOCKED=[]
        for i in range(len(items)):
            self.grpname=str(self.list.selectedItems()[i].text())
            allgroups+=self.grpname+" "
            for s in self.loadsites():
                self.NonBLOCKED.append(s)
        print(self.NonBLOCKED)
        if len(items)==0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Please choose one of this groups or create new.")
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            msg2 = QMessageBox()
            msg2.setIcon(QMessageBox.Information)
            msg2.setText("Proxy Run for : " + allgroups)
            msg2.setWindowTitle("Info")
            msg2.exec_()
            self.thread1 = QThread1()
            self.thread1.set_nb(self.NonBLOCKED)
            self.thread1.start()




    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.list = QListWidget()
        self.list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.list2 = QListWidget()
        onlyfiles=self.loadgrps()
        print("file loads")
        print(onlyfiles)
        for s in onlyfiles:
            self.list.addItem(s)
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        hlayout= QHBoxLayout()
        #w = QWidget()
        self.resize(800, 250)
        self.move(300, 300)
        self.setWindowTitle('proxy filtering for groups!')
        self.show()
        self.textEdit1 = QTextEdit("New Groups")
        self.textEdit2 = QTextEdit("New Site")
        self.textEdit1.setFixedHeight(30)
        self.textEdit2.setFixedHeight(30)
        btn1 = QPushButton('Insert')
        btn1_1 = QPushButton('Delete Group')
        btn2 = QPushButton('Save')
        btn2_1 = QPushButton('Delete Site')
        btn3 = QPushButton('RUN')
        gridLayout = QGridLayout()
        gridLayout.addWidget(self.textEdit1, 0, 0)
        gridLayout.addWidget(btn1, 0, 1)
        gridLayout.addWidget(btn1_1, 0, 2)
        gridLayout.addWidget(self.textEdit2, 0, 3)
        gridLayout.addWidget(btn2, 0, 4)
        gridLayout.addWidget(btn2_1, 0, 5)
        gridLayout.addWidget(self.list, 1, 0,1,3)
        gridLayout.addWidget(self.list2, 1, 3,1,3)
        gridLayout.addWidget(btn3, 2, 0, 1, 6)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setRowStretch(0, 1)
        gridLayout.setRowStretch(1, 1)

        btn3.clicked.connect(self.running)
        btn1.clicked.connect(self.addgrp)
        btn1_1.clicked.connect(self.delgrp)
        btn2.clicked.connect(self.savetogrp)
        btn2_1.clicked.connect(self.delsite)
        self.list.itemClicked.connect(self.selectgrp)
        self.list2.itemClicked.connect(self.selectsite)


        self.setLayout(gridLayout)

class QThread1(QtCore.QThread):
    NonBLOCKED=[]
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def set_nb(self, nb):
        self.NonBLOCKED = nb
        print(self.NonBLOCKED)

    def run(self):
        port = 9090

        # host and port info.
        host = ''  # blank for localhost

        print("Proxy Server Running on ", host, ":", port)


        try:
            # create a socket
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # associate the socket to host and port
            s.bind((host, port))

            # listenning
            s.listen(BACKLOG)

        except (RuntimeError, TypeError, NameError):
            if s:
                s.close()
            print("Could not open socket:", NameError)
            sys.exit(1)

        # get the connection from client
        while 1:
            conn, client_addr = s.accept()

            # create a thread to handle request
            _thread.start_new_thread(self.proxy_thread, (conn, client_addr))

        s.close()


    def proxy_thread(self,conn, client_addr):
        # get the request from browser
        request = conn.recv(MAX_DATA_RECV)

        # parse the first line
        print(request)
        first_line = str(request).split('\n')[0]

        # get url
        print(first_line)
        url = ''
        if len(first_line.split(' ')) > 1:
            url = first_line.split(' ')[1]
        isblock=True
        for i in range(0, len(self.NonBLOCKED)):

            if self.NonBLOCKED[i] in url:
                isblock=False

        print(url,isblock)
        if isblock:
            print("Blacklisted", first_line)
            conn.send(b'Web Site Morede nazar shoma filter mibashad!!!!!')
            conn.close()
            sys.exit(1)
            return
        print("Request", first_line)

        http_pos = url.find("://")  # find pos of ://
        if (http_pos == -1):
            temp = url
        else:
            temp = url[(http_pos + 3):]  # get the rest of url

        port_pos = temp.find(":")  # find the port pos (if any)

        # find end of web server
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos == -1 or webserver_pos < port_pos):  # default port
            port = 80
            webserver = temp[:webserver_pos]
        else:  # specific port
            port = int((temp[(port_pos + 1):])[:webserver_pos - port_pos - 1])
            webserver = temp[:port_pos]
        if port != 80:
            return
        try:
            # create a socket to connect to the web server
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((webserver, port))
            s.send(request)  # send request to webserver

            while 1:
                # receive data from web server
                data = s.recv(MAX_DATA_RECV)

                if (len(data) > 0):
                    # send to browser
                    conn.send(data)
                else:
                    break
            s.close()
            conn.close()
        except (RuntimeError, TypeError, NameError):
            if s:
                s.close()
            if conn:
                conn.close()
            print("Peer Reset", first_line)
            sys.exit(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = proxygui()
    sys.exit(app.exec_())