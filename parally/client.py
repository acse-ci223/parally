import json
import socket

__all__ = ['Client']


class Client:
    """
    A simple client class that connects to a given host and port.
    """
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._running = False
        self._input_parameters = {}
        self.function = None

    def input_function(self, function):
        self.function = function

    def start(self):
        # self._socket.connect((self._host, self._port))
        # print(f"Connected to server {self._host}:{self._port}")
        # while True:
        #     print("Waiting for data...")
        #     data = self._socket.recv(1024)
        #     if not data:
        #         continue
        #     data = json.loads(data.decode())
        #     print(f"Received data: {data}")
        #     self._socket.sendall(json.dumps({'action': 'received'}).encode())
        #     if data['action'] == 'run':
        #         self._input_parameters = data['data']
        #         print(f"Running function with parameters {self._input_parameters}")
        #         try:
        #             result = self.function(self._input_parameters)
        #             to_send = json.dumps({'action': 'result', 'data': result})
        #             self._socket.sendall(to_send.encode())
        #         except Exception as e:
        #             to_send = json.dumps({'action': 'error', 'error': str(e)})
        #             self._socket.sendall(to_send.encode())
        #     elif data['action'] == 'done':
        #         continue
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self._host, self._port))
            print(f"Connected to {self._host}:{self._port}")
            while True:
                data = s.recv(1024)
                if not data:
                    break
                data = json.loads(data.decode())
                print(data)

    def close(self):
        self._socket.close()
