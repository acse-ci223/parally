import socket

class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.sock.settimeout(1)

    def accept(self):
        try:
            client, address = self.sock.accept()
            return client, address
        except socket.timeout:
            return None, None

    def close(self):
        self.sock.close()