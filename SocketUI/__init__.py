import socket
import logging
from PyQt5.QtWidgets import QApplication
from threading import Thread, Event
import time
from types import FunctionType

from .ui import SocketToolsUI
logging.getLogger ().setLevel (logging.INFO)

class Server(Thread):
    def __init__(self, ip, port, event, onRecv=None, onOneJoin=None, onOneLeave=None) -> None:
        super().__init__()
        self.event = event
        self.sk = socket.socket()
        self.conns = [] # type: list[socket.socket]
        self.sk.bind((ip, port))
        self.onRecv = onRecv
        self.onOneJoin = onOneJoin
        self.onOneLeave = onOneLeave
        
    def run(self):
        self.event.set()
        
        def add_recver(conn: socket.socket, addr):
            def recver():
                while self.event.is_set():
                    ret = conn.recv(4096)
                    if not ret:
                        continue
                    msg = ret.decode('utf-8').strip()
                    if msg and self.onRecv:
                        self.onRecv(addr, msg)
            t = Thread(target=recver)
            t.start()
        
        def conn_listener():
            while self.event.is_set():
                conn, addr = self.sk.accept()
                logging.info(f"connect: {addr}")            
                add_recver(conn, addr)
                if self.onOneJoin:
                    self.onOneJoin(addr)
                self.conns.append(conn)
                
        self.sk.listen()
        t_conner = Thread(target=conn_listener)
        t_conner.start()
    
    def send(self, data: str):
        msg = data.encode("utf8")
        for conn in self.conns[::-1]:
            try:
                conn.send(msg)
            except BrokenPipeError:
                if leave := self.onOneLeave:
                    leave(conn.getsockname())
                self.conns.remove(conn)

    def close(self):
        self.event.clear()
        for conn in self.conns:
            conn.close()
        self.sk.close()

class SocketTools:
    def __init__(self, args) -> None:
        self.app = QApplication(args)
        self.ui = SocketToolsUI()
        self.ui.show()
        self.server = None      # type: None | Server
        
    def start_ip_listener(self):
        def ip_listener():
            while True:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                self.ui.ipLabel.setText(str(ip))
                time.sleep(1)
        t = Thread(target=ip_listener)
        t.start()
    
    def exec(self):
        self.start_ip_listener()
        
        @self.ui.alert_error(OSError)
        def onStart(*args, **kwargs):
            logging.info("start socket server")
            if self.server is not None:
                self.server.close()
            self.server = Server(
                "0.0.0.0",
                self.ui.get_port(),
                event=Event(),
                onRecv=self.ui.add_history_recv_msg,
                onOneJoin=self.ui.add_history_one_connect,
                onOneLeave=self.ui.add_history_one_disconnect
            )
            self.server.start()
            
        def onStop(*args, **kwargs):
            logging.info("stop socket server")
            if self.server is not None:
                self.server.close()
        
        def onSend(*args, **kwargs):
            if self.server:
                data = self.ui.get_msg()
                self.server.send(data)
                self.ui.add_history_send_msg(data)
            
        self.ui.startBtn.clicked.connect(onStart)
        self.ui.stopBtn.clicked.connect(onStop)
        self.ui.sendBtn.clicked.connect(onSend)
        return self.app.exec_()

def run():
    import sys
    app = SocketTools(sys.argv)
    status = app.exec()
    if app.server:
        app.server.close()
    sys.exit(status)
