import socket
import json

__all__ = ['Server']

class Worker:
    def __init__(self, conn, addr):
        self._conn = conn
        self._addr = addr
        self._is_running = False
        self._result = None
        self._assigned = False
        self._received_data = bytes()

    def terminate(self):
        self._is_running = False
        self._assigned = False
        self._result = None
        self._received_data = bytes()

    def assign_task(self):
        self._assigned = True

    def run(self):
        data_to_send = json.dumps({'action': 'run'})
        self._conn.send(data_to_send.encode())
        self._is_running = True
        return True

    def check_status(self):
        data = self._conn.recv(1024)
        if not data:
            return
        data += self._received_data
        try:
            data = json.loads(data.decode())
            if data['action'] == 'result':
                self._result = data['result']
                return True
        except json.decoder.JSONDecodeError:
            self._received_data = data
            return False


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
