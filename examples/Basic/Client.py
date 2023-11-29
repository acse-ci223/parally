import time
from parally import Client

HOST = "localhost"
PORT = 65432


def my_function(params):
    """
    my_function A simple function that adds two numbers.

    Parameters
    ----------
    params : dict
        The parameters to use for the function.

    Returns
    -------
    int
        The sum of the two numbers.
    """
    a = params['a']
    b = params['b']
    time.sleep(1)
    return a + b


if __name__ == "__main__":
    client = Client(HOST, PORT, verbose=True)
    client.run_function(my_function)
    client.start()
