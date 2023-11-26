"""Server module for the parally package."""

from datetime import datetime
import random
import socket
import json
from multiprocessing import Process
from typing import Tuple
from colorama import Fore, Style, just_fix_windows_console
just_fix_windows_console()

__all__ = ['Server']


def freeze(o) -> list:
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
        return list(frozenset({k: freeze(v) for k, v in o.items()}.items()))
    if isinstance(o, (set, tuple, list)):
        return list(freeze(v) for v in o)
    return o


def make_hash(o) -> int:
    """
    makes a hash out of anything that contains only
    list,dict and hashable types including string and numeric types

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


class Logs:
    def __init__(self):
        self._logs = []
        self.colors = {
            "info": Fore.GREEN,
            "error": Fore.RED,
            "warning": Fore.YELLOW,
            "debug": Fore.MAGENTA,
            "timestamp": Fore.WHITE,
            "output": Fore.CYAN,
            "reset": Style.RESET_ALL
        }

    def info(self, msg, verbose=False):
        if verbose:
            print("{}{}: {}info-> {}{}".format(
                self.colors['timestamp'],
                datetime.now().strftime("%H:%M:%S"),
                self.colors['info'],
                self.colors['reset'],
                msg))
        self._logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "info",
            "message": msg
        })

    def error(self, msg, verbose=False):
        if verbose:
            print("{}{}: {}error-> {}{}".format(
                self.colors['timestamp'],
                datetime.now().strftime("%H:%M:%S"),
                self.colors['error'],
                self.colors['reset'],
                msg))
        self._logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "error",
            "message": msg
        })

    def warning(self, msg, verbose=False):
        if verbose:
            print("{}{}: {}warning-> {}{}".format(
                self.colors['timestamp'],
                datetime.now().strftime("%H:%M:%S"),
                self.colors['warning'],
                self.colors['reset'],
                msg))
        self._logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "warning",
            "message": msg
        })

    def debug(self, msg, verbose=False):
        if verbose:
            print("{}{}: {}debug-> {}{}".format(
                self.colors['timestamp'],
                datetime.now().strftime("%H:%M:%S"),
                self.colors['debug'],
                self.colors['reset'],
                msg))
        self._logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "debug",
            "message": msg
        })

    def output(self, msg, verbose=False):
        if verbose:
            print("{}{}: {}output-> {}{}".format(
                self.colors['timestamp'],
                datetime.now().strftime("%H:%M:%S"),
                self.colors['debug'],
                self.colors['output'],
                msg))
        self._logs.append({
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "type": "output",
            "message": msg
        })

    def get_logs(self):
        return self._logs

    def clear_logs(self):
        self._logs = []


class State:
    """
    A simple state class that handles the state of a worker.
    """
    def __init__(self):
        """
        __init__ Initialises the State object.
        """
        self._running = False
        self._assigned = False
        self._done = False

    def set_running(self, running) -> None:
        """
        set_running Sets the running state of the worker.

        Parameters
        ----------
        running : bool
            The running state of the worker.
        """
        self._running = running

    def set_assigned(self, assigned) -> None:
        """
        set_assigned Sets the assigned state of the worker.

        Parameters
        ----------
        assigned : bool
            The assigned state of the worker.
        """
        self._assigned = assigned

    def set_done(self, done) -> None:
        """
        set_done Sets the done state of the worker.

        Parameters
        ----------
        done : bool
            The done state of the worker.
        """
        self._done = done

    def is_running(self) -> bool:
        """
        is_running Checks if the worker is running.

        Returns
        -------
        bool
            True if the worker is running, False otherwise.
        """
        return self._running

    def is_assigned(self) -> bool:
        """
        is_assigned Checks if the worker is assigned.

        Returns
        -------
        bool
            True if the worker is assigned, False otherwise.
        """
        return self._assigned

    def is_done(self) -> bool:
        """
        is_done Checks if the worker is done.

        Returns
        -------
        bool
            True if the worker is done, False otherwise.
        """
        return self._done


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
        self._socket = (conn, addr)
        self._state = State()
        self._input_parameters = {}
        self._result = None
        self._received_data = bytes()
        self._error = None

    def terminate(self) -> None:
        """
        terminate Terminates the worker.
        """
        self._state = State()
        self._input_parameters = {}
        self._result = None
        self._received_data = bytes()
        self._error = None

    def assign_task(self, parameters) -> None:
        """
        assign_task Assigns a task to the worker.

        Parameters
        ----------
        parameters : dict
            Parameters to be passed to the worker.
        """
        self._state.set_assigned(True)
        self._input_parameters = parameters

    def is_assigned(self) -> bool:
        """
        is_assigned Checks if the worker has been assigned a task.

        Returns
        -------
        bool
            True if the worker has been assigned a task, False otherwise.
        """
        return self._state.is_assigned()

    def unassign_task(self) -> None:
        """
        unassign_task Unassigns the task from the worker.
        """
        self._state.set_assigned(False)
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
        return self._state.is_running()

    def is_done(self) -> bool:
        """
        is_done Checks if the worker is done.

        Returns
        -------
        bool
            True if the worker is done, False otherwise.
        """
        return self._state.is_done()

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
        to_send = json.dumps({
            'action': 'run',
            'parameters': self._input_parameters
        })
        self._socket[0].send(to_send.encode())
        self._state.set_running(True)
        return True

    def check_status(self) -> bool:
        """
        check_status Checks the status of the worker.
        """
        data = self._socket[0].recv(1024)
        if not data:
            return False
        data += self._received_data
        try:
            data = json.loads(data.decode())
            if data['action'] == 'result':
                self._result = {
                    "input": self._input_parameters,
                    "result": data['data']
                }
                self._state.set_done(True)
                return True
            if data['action'] == 'error':
                self._error = data['error']
                self._state.set_done(True)
                return False
            if data['action'] == 'received':
                return False
        except json.decoder.JSONDecodeError:
            self._error = 'Invalid JSON received.'
            self._state.set_done(True)
            return False
        return False


class Server:
    """
    A simple server class that listens on a given host and port.
    """
    def __init__(self, host, port, verbose=False):
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
        self._verbose = verbose
        self._logs = Logs()

    def start(self) -> None:
        """
        start Starts the server.
        """
        try:
            if self._to_complete == 0:
                raise ValueError(
                    "No parameters to bind. Make sure you run \
                        Server.bind_parameters() first.")
            if self._callback is None:
                raise ValueError(
                    "No callback function initialized. Make sure you run \
                        Server.on_completed(my_callback_function) first.")
            if self._callback_error is None:
                raise ValueError(
                    "No error function initialized. Make sure you run \
                        Server.on_error(my_error_function) first.")
            if self.running:
                raise ValueError("Server is already running.")
            if self.port < 1024 or self.port > 65535:
                raise ValueError("Port must be between 1024 and 65535.")
            if self.host == '':
                self.host = 'localhost'

            self._logs.info("Starting server on {}:{}".format(
                self.host, self.port), verbose=self._verbose)

            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            self._sock.bind((self.host, self.port))
            self._sock.listen()

            self._logs.info("Server started.", verbose=self._verbose)

            self.running = True
            self._process = Process(target=self._update)
            self._process.start()
            self._logs.info("Server process started.", verbose=self._verbose)
        except ValueError as e:
            self._logs.error(e, verbose=self._verbose)

    def _accept(self) -> Tuple[socket.socket, tuple]:
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
            return (socket.socket(socket.AF_INET, socket.SOCK_STREAM), ('', 0))

    def bind_parameters(self, parameters) -> None:
        """
        bind_parameters Binds a list of parameters to the server.

        Parameters
        ----------
        parameters : list
            A list of parameters to be bound to the server.
        """
        try:
            if not isinstance(parameters, list):
                raise TypeError("Parameters must be a list.")
            self._to_complete = len(parameters)
            self._parameters = parameters

            self._logs.info("Parameters bound.", verbose=self._verbose)
        except TypeError as e:
            self._logs.error(e, verbose=self._verbose)

    def on_completed(self, callback) -> None:
        """
        on_completed Sets the callback function to be called
        when the server has completed all tasks.

        Parameters
        ----------
        callback : function
            The callback function to be called when the
            server has completed all tasks.
        """
        try:
            if not callable(callback):
                raise TypeError("Callback must be a function.")
            self._callback = callback

            self._logs.info("Callback function set.", verbose=self._verbose)
        except TypeError as e:
            self._logs.error(e, verbose=self._verbose)

    def on_error(self, callback):
        """
        on_error Sets the callback function to be called
        when the server has encountered an error.

        Parameters
        ----------
        callback : function
            The callback function to be called
            when the server has encountered an error.
        """
        try:
            if not callable(callback):
                raise TypeError("Callback must be a function.")
            self._callback_error = callback

            self._logs.info("Error function set.", verbose=self._verbose)
        except TypeError as e:
            self._logs.error(e, verbose=self._verbose)

    def _update(self) -> None:
        """
        update Updates the server.
        """
        self._logs.info("Waiting for connection...", verbose=self._verbose)

        client, address = self._accept()

        self._logs.info("Connection from {}".format(address),
                        verbose=self._verbose)
        while self.running:
            if client is not None and address not in self._workers.keys():
                self._workers[address] = Worker(client, address)

            for key, _ in self._workers.items():
                if not self._workers[key].is_assigned():
                    input_p = random.choice(self._parameters)
                    self._workers[key].assign_task(input_p)
                    self._assigned[key] = {
                        "status": "assigned",
                        "parameters": input_p
                    }
                    self._workers[key].run()

                    self._logs.info("Assigned parameters: {} to {}".format(
                        self._workers[key].get_parameters(), key),
                        verbose=self._verbose)

                elif (self._workers[key].is_assigned() and not
                      self._workers[key].is_running()):
                    self._workers[key].run()

                if self._workers[key].is_running():
                    self._workers[key].check_status()

                if self._workers[key].is_done():
                    if self._workers[key].get_error() is not None:
                        if self._callback_error is not None:
                            self._callback_error(
                                self._workers[key].get_error())
                        else:
                            self._logs.error(
                                self._workers[key].get_error(),
                                verbose=self._verbose)
                            continue
                    else:
                        self._completed.append(self._workers[key].get_result())

                        self._logs.info(
                            "Completed parameters: {} from {}".format(
                                self._workers[key].get_parameters(), key),
                            verbose=self._verbose)

                        self._logs.output(self._workers[key].get_result(),
                                          verbose=self._verbose)

                        self._parameters.remove(
                            self._workers[key].get_parameters())

                    self._workers[key].terminate()

            if len(self._completed) == self._to_complete:
                if self._callback is not None:
                    self._logs.info("All tasks completed.",
                                    verbose=self._verbose)
                    self._logs.output(self._completed, verbose=self._verbose)
                    self._callback(self._completed)
                self._logs.info("Stopping server...", verbose=self._verbose)
                self.stop()

    def stop(self) -> list:
        """
        stop Stops the server.

        Returns
        -------
        list
            A list of results.
        """
        try:
            if not self.running:
                raise ValueError("Server is not running.")
            self.running = False
            return self._completed
        except ValueError as e:
            self._logs.error(e, verbose=self._verbose)
        return []
