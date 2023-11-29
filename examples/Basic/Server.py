import random
from parally import Server

HOST = "localhost"
PORT = 65432

parameters = [{"a": random.randint(0, 10),
               "b": random.randint(0, 10)} for i in range(10)]


def print_result(result):
    """
    print_result Prints the result of the worker.

    Parameters
    ----------
    result : any
        The result of the worker.
    """
    print(result)


if __name__ == "__main__":
    server = Server(HOST, PORT, verbose=True)
    server.bind_parameters(parameters)
    server.on_completed(print_result)
    server.on_error(print_result)
    server.set_verbose(True)
    server.start()
