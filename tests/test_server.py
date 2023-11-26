import pytest
import parally.server


class TestServer:

    def test_init(self):
        server = parally.server.Server('localhost', 5000)
        assert server.host == 'localhost'
        assert server.port == 5000
        assert server._workers == {}
