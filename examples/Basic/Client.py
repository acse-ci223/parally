from parally import Client

HOST = "localhost"
PORT = 65432


def my_function(a, b):
    return a + b


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.input_function(my_function)
    client.start()
