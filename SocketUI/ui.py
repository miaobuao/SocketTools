import sys
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, 
    QTextEdit, QGridLayout, QApplication, QPushButton,
    QListWidget, QListWidgetItem, QMessageBox
)
import traceback
import logging

logging.getLogger ().setLevel(logging.INFO)

class SocketToolsUI(QWidget):
    def __init__(self, parent=None, title='Socket UI'):
        super(SocketToolsUI, self).__init__(parent)
        self.started = False

        self.ipLabel = QLabel('0.0.0.0')
        self.portEdit = QLineEdit()
        self.portEdit.setInputMask("00000")
        self.startBtn = QPushButton("Start")
        self.stopBtn = QPushButton("Stop")
        self.sendBtn = QPushButton("Send")

        self.historyView = QListWidget()
        self.msgEdit = QTextEdit()
        
        def onStart():
            self.update(True)
        def onStop():
            self.update(False)
    
        self.startBtn.clicked.connect(onStart)
        self.stopBtn.clicked.connect(onStop)
        
        self.grid = grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("IP"), 1, 0)
        grid.addWidget(self.ipLabel, 1, 1)
        grid.addWidget(QLabel("Port"), 1, 2)
        grid.addWidget(self.portEdit, 1, 3)
        grid.addWidget(self.startBtn, 1, 4)
        
        grid.addWidget(self.historyView, 2, 0, 1, 0)
        
        grid.addWidget(self.msgEdit, 3, 0, 1, 0)
        grid.addWidget(self.sendBtn, 4, 0)

        self.setLayout(grid)

        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle(title)
        
    def add_history(self, data: str):
        self.historyView.insertItem(0, QListWidgetItem(data))
        
    def add_history_one_connect(self, addr):
        self.add_history(f"connect: {addr}")
    
    def add_history_one_disconnect(self, addr):
        self.add_history(f"disconnect: {addr}")
    
    def add_history_recv_msg(self, addr, msg):
        self.add_history(f"[{addr[0]}:{addr[1]}]: {msg}")
    
    def add_history_send_msg(self, msg):
        self.add_history(f"> {msg}")
        
    def add_history_on_server_start(self, addr):
        self.add_history(f"Server > START: {addr[0]}:{addr[1]}")
        
    def add_history_on_server_stop(self, addr):
        self.add_history(f"Server > STOP: {addr[0]}:{addr[1]}")
        
    def get_msg(self):
        return self.msgEdit.toPlainText()
    
    def get_port(self):
        return int(self.portEdit.text())
    
    def update(self, started):
        self.started = started
        if started:
            self.grid.replaceWidget(self.startBtn, self.stopBtn)
            self.startBtn.hide()
            self.stopBtn.show()
        else:
            self.grid.replaceWidget(self.stopBtn, self.startBtn)
            self.startBtn.show()
            self.stopBtn.hide()
            
    def alert_error(self, *exceptions, error_callback=None):
        def _try(func, E):
            def _subfunc(*args, **kwargs):
                try:
                    return func()
                except Exception as e:
                    QMessageBox.critical(self, E.__name__, str(e))
                    if error_callback:
                        error_callback(e)
                    logging.debug(traceback.format_exc())
            return _subfunc
        def wrap(func):
            if exceptions:
                for E in exceptions:
                    func = _try(func, E)
            return func
        return wrap
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = SocketToolsUI()
    form.show()
    sys.exit(app.exec_())
