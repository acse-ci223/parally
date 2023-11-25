import socket

class Client:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.connect((self._host, self._port))

    def send(self, msg):
        self._socket.sendall(msg.encode('utf-8'))

    def recv(self):
        return self._socket.recv(1024).decode('utf-8')

    def close(self):
        self._socket.close()