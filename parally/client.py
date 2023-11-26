"""Client module for the parally package."""

import json
import socket

__all__ = ['Client']


class Client:
    """
    A simple client class that connects to a given host and port.
    """
    def __init__(self, host, port):
        """
        __init__ Initializes the client.

        Parameters
        ----------
        host : str
            The host to connect to.
        port : int
            The port to connect to.
        """
        self._host = host
        self._port = port
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._running = False
        self._input_parameters = {}
        self.function = None

    def run_function(self, function) -> None:
        """
        input_function Sets the function to run on the server.

        Parameters
        ----------
        function : function
            The function to run on the server.
        """
        self.function = function

    def start(self) -> None:
        """
        start Starts the client.
        """
        self._socket.connect((self._host, self._port))
        print(f"Connected to server {self._host}:{self._port}")
        while True:
            print("Waiting for data...")
            data = self._socket.recv(1024)
            if not data:
                continue
            data = json.loads(data.decode())
            print(f"Received data: {data}")
            # self._socket.sendall(json.dumps({'action': 'received'}).encode())
            if data['action'] == 'run':
                self._input_parameters = data['parameters']
                print("Running function with parameters {}".format(
                    self._input_parameters))
                try:
                    result = self.function(self._input_parameters)
                    to_send = json.dumps({'action': 'result', 'data': result})
                    self._socket.sendall(to_send.encode())
                except (ValueError, TypeError) as e:
                    to_send = json.dumps({'action': 'error', 'error': str(e)})
                    self._socket.sendall(to_send.encode())
            elif data['action'] == 'done':
                continue

    def close(self) -> None:
        """
        close Closes the client.
        """
        self._socket.close()
