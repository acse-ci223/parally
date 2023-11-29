"""Client module for the parally package."""

import json
import socket

from .server import Logs

__all__ = ['Client']


class Client:
    """
    A simple client class that connects to a given host and port.
    """
    def __init__(self, host, port, verbose=False):
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
        self._verbose = verbose
        self._logs = Logs()

    def get_logs(self) -> list:
        """
        get_logs Gets the logs.

        Returns
        -------
        list
            The logs.
        """
        return self._logs.get_logs()

    def run_function(self, function) -> None:
        """
        input_function Sets the function to run on the server.

        Parameters
        ----------
        function : function
            The function to run on the server.
        """
        try:
            if not callable(function):
                raise TypeError("Callback must be a function.")
            self.function = function

            self._logs.info("Callback function set.", verbose=self._verbose)
        except TypeError as e:
            self._logs.error(e, verbose=self._verbose)

    def start(self) -> None:
        """
        start Starts the client.
        """
        self._socket.connect((self._host, self._port))
        self._logs.info(f"Connected to server {self._host}:{self._port}",
                        verbose=self._verbose)
        self._running = True
        while self._running:
            try:
                self._socket.sendall(json.dumps({'action': 'ready'}).encode())
            except Exception:
                self._logs.error("Server closed connection.",
                                 verbose=self._verbose)
                self.close()
                break
            try:
                data = self._socket.recv(1024)
            except Exception:
                pass
            if not data:
                continue
            data = json.loads(data.decode())
            self._logs.info(f"Received data: {data}", verbose=self._verbose)
            if data['action'] == 'run':
                self._input_parameters = data['parameters']
                self._logs.info("Running function with parameters {}".format(
                    self._input_parameters),
                                verbose=self._verbose)
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
        self._running = False
        self._logs.info("Closing client.", verbose=self._verbose)
        self._socket.close()

    def _default_callback(self, results) -> None:
        """
        default_callback A default callback function.

        Parameters
        ----------
        results : list
            A list of results.
        """
        print(results)
