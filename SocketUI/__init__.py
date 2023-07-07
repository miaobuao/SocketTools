import socket
import logging
from PyQt5.QtWidgets import QApplication
from threading import Thread, Lock
import time
import selectors
import sys

from .ui import SocketToolsUI
logging.getLogger().setLevel(logging.DEBUG)

CHECK_ALIVE_INTERVAL = 10

class Server(Thread):
    def __init__(self, ip, port, flag, 
                onRecv=None, onOneJoin=None,
                onOneLeave=None) -> None:
        super().__init__()
        self.flag = flag
        self.sel = selectors.DefaultSelector()

        self.ip = ip
        self.port = port
        self.conns = [] # type: list[tuple[socket.socket, socket._RetAddress]]
        self.onRecv = onRecv
        self.onOneJoin = onOneJoin
        self.onOneLeave = onOneLeave
        self.sk = socket.socket()
        self.sk.bind((self.ip, self.port))

    def run(self):
        # sk = socket.socket()
        sk = self.sk
        sk.setblocking(False)
        sk.settimeout(0.0)
        self.sel.register(
            sk,
            selectors.EVENT_READ,
            self.accept
        )
        
        sk.listen()
        while self.flag['status']:
            for k, mask in self.sel.select(0.2):
                cb = k.data
                cb(k.fileobj, mask)
        for conn, addr in self.conns:
            conn.close()
        self.conns = []
        sk.close()
        del sk
        
    def accept(self, conn: socket.socket, mask):
        try:
            conn, addr = conn.accept()
            conn.setblocking(False)
            self.sel.register(conn, selectors.EVENT_READ, self.read)
            if call := self.onOneJoin:
                call(addr)
            self.conns.append((conn, addr))
        except:
            pass
    
    def read(self, conn: socket.socket, mask):
        data = conn.recv(4096)
        addr = None
        for _conn, _addr in self.conns:
            if _conn is conn:
                addr = _addr
                break
        if data:
            msg = data.decode("utf8").strip()
            if (call := self.onRecv) and addr:
                call(addr, msg)
        else:
            self.sel.unregister(conn)
            self.conns.remove((conn, addr))
            if call := self.onOneLeave:
                call(addr)
            conn.close()
    
    def send(self, data: str):
        msg = data.encode("utf8")
        for conn, addr in self.conns[::-1]:
            try:
                conn.send(msg)
                logging.info(f"===> {addr}")
            except BrokenPipeError:
                if leave := self.onOneLeave:
                    leave(str(conn.getpeername()))
                self.conns.remove((conn, addr))
    
    def close(self):
        self.flag['status'] = False

def getIp():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)
    return ip

class SocketTools:
    def __init__(self, args=sys.argv) -> None:
        self.app = QApplication(args)
        self.ui = SocketToolsUI()
        self.ui.show()
        self.server = None      # type: None | Server
                
    def start_ip_listener(self):
        def ip_listener():
            while True:
                self.ui.ipLabel.setText(getIp())
                time.sleep(1)
        t = Thread(target=ip_listener)
        t.start()
    
    def exec(self):
        self.start_ip_listener()
        flag = {
            "status": True
        }
        @self.ui.alert_error(OSError, error_callback=lambda _: self.ui.update(False))
        def onStart(*args, **kwargs):
            logging.info("start socket server")
            if self.server is not None:
                self.server.close()
                self.server.join()
                self.server = None
            flag["status"] = True
            port = self.ui.get_port()
            self.server = Server(
                "0.0.0.0",
                port,
                flag,
                onRecv=self.ui.add_history_recv_msg,
                onOneJoin=self.ui.add_history_one_connect,
                onOneLeave=self.ui.add_history_one_disconnect
            )
            self.server.start()
            self.ui.add_history_on_server_start((getIp(), port))
            
        def onStop(*args, **kwargs):
            logging.info("stop socket server")
            if self.server is not None:
                self.server.close()
                self.server.join()
                self.ui.add_history_on_server_stop((getIp(), self.server.port))
                self.server = None
        
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
    app = SocketTools()
    status = app.exec()
    del app
    return status
