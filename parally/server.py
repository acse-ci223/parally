import random
import socket
import json
from multiprocessing import Process

__all__ = ['Server']


def freeze(o) -> (dict, list, tuple, set):
    """
    freezes a nested dictionary, list, tuple or set

    Parameters
    ----------
    o : dict, list, tuple, set
        The object to be frozen

    Returns
    -------
    dict, list, tuple, set
        The frozen object
    """
    if isinstance(o, dict):
        return frozenset({k: freeze(v) for k, v in o.items()}.items())
    if isinstance(o, (set, tuple, list)):
        return tuple([freeze(v) for v in o])
    return o


def make_hash(o) -> int:
    """
    makes a hash out of anything that contains only list,dict and hashable types including string and numeric types

    Parameters
    ----------
    o : dict, list, tuple, set
        The object to be hashed

    Returns
    -------
    int
        The hash of the object
    """
    return hash(freeze(o))


class Worker:
    """
    A simple worker class that handles the connection to a client.
    """
    def __init__(self, conn, addr):
        """
        __init__ Initialises the Worker object.

        Parameters
        ----------
        conn : socket.socket
            Socket connection to the client.
        addr : tuple
            Address of the client.
        """
        self._conn = conn
        self._addr = addr
        self._running = False
        self._assigned = False
        self._input_parameters = {}
        self._result = None
        self._received_data = bytes()
        self._error = None
        self._done = False

    def terminate(self) -> None:
        """
        terminate Terminates the worker.
        """
        self._running = False
        self._assigned = False
        self._result = None
        self._received_data = bytes()
        self._error = None
        self._done = False

    def assign_task(self, parameters) -> None:
        """
        assign_task Assigns a task to the worker.

        Parameters
        ----------
        parameters : dict
            Parameters to be passed to the worker.
        """
        self._assigned = True
        self._input_parameters = parameters

    def is_assigned(self) -> bool:
        """
        is_assigned Checks if the worker has been assigned a task.

        Returns
        -------
        bool
            True if the worker has been assigned a task, False otherwise.
        """
        return self._assigned

    def unassign_task(self) -> None:
        """
        unassign_task Unassigns the task from the worker.
        """
        self._assigned = False
        self._input_parameters = {}

    def get_parameters(self) -> dict:
        """
        get_parameters Returns the parameters assigned to the worker.

        Returns
        -------
        dict
            The parameters assigned to the worker.
        """
        return self._input_parameters

    def is_running(self) -> bool:
        """
        is_running Checks if the worker is running.

        Returns
        -------
        bool
            True if the worker is running, False otherwise.
        """
        return self._running

    def is_done(self) -> bool:
        """
        is_done Checks if the worker is done.

        Returns
        -------
        bool
            True if the worker is done, False otherwise.
        """
        return self._done

    def get_error(self) -> str:
        """
        get_error Returns the error message of the worker.

        Returns
        -------
        str
            The error message of the worker.
        """
        return self._error

    def get_result(self) -> dict:
        """
        get_result Returns the result of the worker.

        Returns
        -------
        dict
            The result of the worker.
        """
        return self._result

    def run(self) -> bool:
        """
        run Runs the worker.

        Returns
        -------
        bool
            True if the worker has been run, False otherwise.
        """
        to_send = json.dumps({'action': 'run', 'parameters': self._input_parameters})
        self._conn.send(to_send.encode())
        self._running = True
        return True

    def check_status(self):
        """
        check_status Checks the status of the worker.
        """
        data = self._conn.recv(1024)
        if not data:
            return False
        data += self._received_data
        try:
            data = json.loads(data.decode())
            if data['action'] == 'result':
                self._result = {
                    "input": self._input_parameters,
                    "result": data['result']
                }
                self._done = True
                return True
            elif data['action'] == 'error':
                self._error = data['error']
                self._done = True
                return False
        except json.decoder.JSONDecodeError:
            self._error = 'Invalid JSON received.'
            self._done = True
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
        self._sock = None
        self._process = None
        self.running = False
        self._workers = {}
        self._parameters = []
        self._assigned = {}
        self._completed = []
        self._to_complete = 0
        self._callback = None
        self._callback_error = None

    def start(self) -> None:
        """
        start Starts the server.
        """
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen()
        self.running = True
        self._process = Process(target=self.update)
        self._process.start()

    def _accept(self) -> (socket.socket, tuple):
        """
        _accept Accepts a connection from a client.

        Returns
        -------
        (socket.socket, tuple)
            The socket connection and the address of the client.
        """
        try:
            client, address = self._sock.accept()
            return (client, address)
        except socket.timeout:
            return (None, None)

    def bind_parameters(self, parameters) -> None:
        """
        bind_parameters Binds a list of parameters to the server.

        Parameters
        ----------
        parameters : list
            A list of parameters to be bound to the server.
        """
        self._to_complete = len(parameters)
        self._parameters = parameters

    def on_completed(self, callback) -> None:
        """
        on_completed Sets the callback function to be called when the server has completed all tasks.

        Parameters
        ----------
        callback : function
            The callback function to be called when the server has completed all tasks.
        """
        self._callback = callback

    def on_error(self, callback):
        """
        on_error Sets the callback function to be called when the server has encountered an error.

        Parameters
        ----------
        callback : function
            The callback function to be called when the server has encountered an error.
        """
        self._callback_error = callback

    def update(self) -> None:
        """
        update Updates the server.
        """
        while self.running:
            client, address = self._accept()
            print(f"Connection from {address}")

            if client is not None and address not in self._workers.keys():
                self._workers[address] = Worker(client, address)

            for key, worker in self._workers.items():

                if not self._workers[key].is_assigned():
                    input_p = random.choice(self._parameters)
                    self._workers[key].assign_task(input_p)
                    self._assigned[key] = {
                        "status": "assigned",
                        "parameters": input_p
                    }
                    print(f"Assigned parameters: {self._workers[key].get_parameters()} to {key}")

                elif self._workers[key].is_assigned() and not self._workers[key].is_running():
                    self._workers[key].run()

                if self._workers[key].is_running():
                    self._workers[key].check_status()

                if self._workers[key].is_done():
                    if self._workers[key].get_error() is not None:
                        self._callback_error(self._workers[key].get_error())
                    else:
                        self._completed.append(self._workers[key].get_result())
                        self._workers[key].terminate()
                        self._parameters.pop(0)

            if len(self._completed) == self._to_complete:
                self._callback(self.stop())

    def stop(self) -> list:
        """
        stop Stops the server.

        Returns
        -------
        list
            A list of results.
        """
        self._sock.close()
        self._process.terminate()
        self.running = False
        return self._completed
