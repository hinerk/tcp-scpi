# TCP SCPI Controller

Use like:

```python
from src.tcp_scpi.tcp_scpi import SCPIClient

scpi = SCPIClient('192.168.1.11', port=5555)
scpi.connect()
print(scpi.query('*IDN?'))
scpi.close()

# or

with SCPIClient('192.168.1.11', port=5555) as scpi:
    print(scpi.query('*IDN?'))
```
