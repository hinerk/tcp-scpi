import socket
from logging import getLogger


logger = getLogger(__name__)


class SCPIClient:
    def __init__(self, ip, port=5025, timeout=3, newline='\n'):
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._sock = None
        self._newline = newline

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __repr__(self):
        return (f'{self.__class__.__name__}(ip={repr(self._ip)}, '
                f'port={repr(self._port)}, timeout={repr(self._timeout)}, '
                f'newline={repr(self._newline)})')

    def connect(self):
        self._sock = socket.create_connection((self._ip, self._port),
                                              timeout=self._timeout)

    def send(self, command):
        if not command.endswith('\n'):
            command += '\n'
        logger.debug(f'sending {repr(command)}')
        self._sock.sendall(command.encode())

    def receive(self, buf_size=4096):
        received = self._sock.recv(buf_size)
        logger.debug(f"received {repr(received)}")
        return received.decode().strip()

    def query(self, command):
        self.send(command)
        return self.receive()

    def close(self):
        if self._sock:
            self._sock.close()
