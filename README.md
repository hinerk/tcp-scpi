# TCP SCPI Controller

A minimal TCP/IP client for communicating with SCPI-compliant instruments.

This client sends commands and queries over a TCP socket and automatically
checks for SCPI errors after each operation.

## Features

- Easy send/query interface
- Automatic SCPI error checking after each command
- Context manager support for clean connection handling
- Customizable error query behavior (`:SYSTem:ERRor?`)

## Installation

No installation needed. Just drop `tcp_scpi.py` into your project or import
as a module.

## Usage

```python
from src.tcp_scpi.tcp_scpi import SCPIClient

# Manual connection
scpi = SCPIClient('192.168.1.11', port=5555)
scpi.connect()
print(scpi.query('*IDN?'))
scpi.close()

# Context manager (recommended)
with SCPIClient('192.168.1.11', port=5555) as scpi:
    print(scpi.query('*IDN?'))
```

# SCPI Error Checking

After each `send()` or `query()`, the client automatically checks for
instrument-reported errors using the SCPI command `:SYSTem:ERRor?`.

## How It Works

SCPI instruments maintain an internal error queue. After each operation,
the client queries this queue in a loop until it receives the "no error"
message (`0,"No error"` by default).

If any errors are found, a `SCPIError` is raised listing all reported messages.

This behavior ensures that communication issues or invalid commands are
detected early.

You can customize the error-checking behavior using the `error_cmd` and
`no_error_msg` parameters:

```python
SCPIClient(
    ip='192.168.1.11',
    error_cmd=':SYSTem:ERRor?',
    no_error_msg='0,"No error"'
)
```
