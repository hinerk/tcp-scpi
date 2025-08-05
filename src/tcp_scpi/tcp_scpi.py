import socket
from logging import getLogger


logger = getLogger(__name__)


class SCPIError(Exception):
    """Exception raised for SCPI communication errors."""
    pass


class SCPIClient:
    """
    A client for communicating with SCPI instruments over TCP/IP sockets.

    Supports sending commands, receiving responses, and querying the instrument,
    with automatic SCPI error checking after each operation.
    """

    def __init__(
        self,
        host: str,
        port: int = 5025,
        timeout: float = 0.5,
        command_termination: bytes = b'\n',
        error_cmd: str = ":SYSTem:ERRor?",
        no_error_msg: str = '0,"No error"',
    ):
        """
        Initialize the SCPIClient.

        :param host: URL of the SCPI device.
        :param port: TCP port to connect to (default: 5025).
        :param timeout: Socket timeout in seconds (default: 0.5).
        :param command_termination: Character used to terminate SCPI commands
        (default: '\\n').
        :param error_cmd: SCPI command used to query errors
        (default: ':SYSTem:ERRor?').
        :param no_error_msg: Expected response indicating no error
        (default: '0,"No error"').
        """
        self._host = host
        self._port = port
        self._timeout = timeout
        self._sock: socket.socket | None = None
        self._command_termination = command_termination
        self._error_cmd = error_cmd
        self._no_error_msg = no_error_msg

    def __enter__(self):
        """
        Enable use of the client as a context manager.
        Automatically connects on entry.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Automatically closes the connection on context manager exit.
        """
        self.close()

    def __repr__(self):
        return (f'{self.__class__.__name__}(ip={repr(self._host)}, '
                f'port={repr(self._port)}, timeout={repr(self._timeout)}, '
                f'command_termination={repr(self._command_termination)})')

    def connect(self):
        """
        Establish a socket connection to the SCPI instrument.
        """
        self._sock = socket.create_connection(
            (self._host, self._port), timeout=self._timeout)

    def _send(self, command: str):
        """
        Send a raw command to the instrument.

        Intended for internal usage: unlike SCPIClient.send(), this method
        doesn't read out any errors after issuing a command.

        :param command: Command string to send.
        """
        if not command.endswith('\n'):
            command += '\n'
        logger.debug(f'sending {repr(command)}')
        self._sock.sendall(command.encode())

    def _receive(self, buf_size: int = 4096):
        """
        Receive a response from the instrument.

        :param buf_size: Maximum number of bytes to read (default: 4096).
        :return: Decoded response string (whitespace stripped).
        """
        received = b""
        while True:
            chunk = self._sock.recv(buf_size)
            received += chunk
            logger.debug(f'received chunk {chunk!r}')
            if chunk[-1:] == self._command_termination:
                break
        logger.debug(f"received {received!r}")
        return received.decode().strip()

    def _query(self, command: str):
        """
        Send a command and immediately return the response.

        Intended for internal usage: unlike SCPIClient.query(), this method
        doesn't read out any errors after issuing a command.

        :param command: SCPI command string.
        :return: Response string from the instrument.
        """
        self._send(command)
        return self._receive()

    def send(self, command: str):
        """
        Send a command to the instrument and check for SCPI errors.

        :param command: SCPI command string.
        :raises SCPIError: If the instrument reports any errors.
        """
        self._send(command)
        if errors := self._read_errors():
            errors = ", ".join(errors)
            raise SCPIError(f"sending {repr(command)} failed with: {errors}")

    def receive(self):
        """
        Receive data from the instrument.

        :return: Response string from the instrument.
        """
        return self._receive()

    def query(self, command: str):
        """
        Send a query command to the instrument and return the response,
        with SCPI error checking.

        :param command: SCPI command string.
        :return: Response string from the instrument.
        :raises SCPIError: If the instrument reports any errors.
        """
        response = self._query(command)
        if errors := self._read_errors():
            errors = ", ".join(errors)
            raise SCPIError(f"querying {repr(command)} failed with: {errors}")
        return response

    def close(self):
        """
        Close the socket connection if open.
        """
        if self._sock:
            self._sock.close()

    def _read_errors(self):
        """
        Read SCPI errors until no more are reported.

        :return: List of error messages (empty if no errors).
        """
        errors = []
        while (error_msg := self._query(self._error_cmd)) != self._no_error_msg:
            errors.append(error_msg)
        return errors
