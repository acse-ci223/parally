from parally import Client

HOST = "localhost"
PORT = 65432


def my_function(a, b):
    """
    my_function A simple function that adds two numbers.

    Parameters
    ----------
    a : int
        The first number.
    b : int
        The second number.

    Returns
    -------
    int
        The sum of the two numbers.
    """
    return a + b


if __name__ == "__main__":
    client = Client(HOST, PORT)
    client.input_function(my_function)
    client.start()
