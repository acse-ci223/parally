import time
from parally import Server

HOST = "localhost"
PORT = 65432

parameters = [
    {"a": 1, "b": 2},
    {"a": 3, "b": 4},
    {"a": 5, "b": 6},
]

def print_result(result):
    print(result)

if __name__ == "__main__":
    server = Server(HOST, PORT)
    server.bind_parameters(parameters)
    server.start()
    server.on_completed(print_result)
    server.on_error(print_result)