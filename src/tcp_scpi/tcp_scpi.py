import socket
from logging import getLogger


logger = getLogger(__name__)


class SCPIError(Exception):
    pass


class SCPIClient:
    def __init__(
            self,
            ip,
            port=5025,
            timeout=0.5,
            newline='\n',
            error_cmd=":SYSTem:ERRor?",
            no_error_msg='0,"No error"'
    ):
        """

        :param ip:
        :param port:
        :param timeout:
        :param newline:
        :param error_cmd:
        :param no_error_msg:
        """
        self._ip = ip
        self._port = port
        self._timeout = timeout
        self._sock: socket.socket | None = None
        self._newline = newline
        self._error_cmd = error_cmd
        self._no_error_msg = no_error_msg

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
        self._sock = socket.create_connection(
            (self._ip, self._port), timeout=self._timeout)

    def _send(self, command):
        if not command.endswith('\n'):
            command += '\n'
        logger.debug(f'sending {repr(command)}')
        self._sock.sendall(command.encode())

    def _receive(self, buf_size=4096):
        received = self._sock.recv(buf_size)
        logger.debug(f"received {repr(received)}")
        return received.decode().strip()

    def _query(self, command):
        self._send(command)
        return self._receive()

    def send(self, command):
        self._send(command)
        if errors := self._read_errors():
            errors = ", ".join(errors)
            raise SCPIError(f"sending {repr(command)} failed with: {errors}")

    def receive(self):
        self._receive()

    def query(self, command):
        response = self._query(command)
        if errors := self._read_errors():
            errors = ", ".join(errors)
            raise SCPIError(f"querying {repr(command)} failed with: {errors}")
        return response

    def close(self):
        if self._sock:
            self._sock.close()

    def _read_errors(self):
        errors = []
        while (error_msg := self._query(self._error_cmd)) != self._no_error_msg:
            errors.append(error_msg)
        return errors
