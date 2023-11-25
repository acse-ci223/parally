import socket


class Server:
    """
    A simple server class that listens on a given host and port.
    """
    def __init__(self, host, port):
        """
        __init__ Initialises the Server object.

        Parameters
        ----------
        host : string
            Host address to listen on.
        port : int
            Port to listen on. Must be between 1024 and 65535.
        """
        self.host = host
        self.port = port
        self.sock = None

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
