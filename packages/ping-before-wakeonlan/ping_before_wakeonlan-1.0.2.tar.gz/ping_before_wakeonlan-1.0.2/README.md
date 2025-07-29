# ping-before-wakeonlan

[![PyPI version](https://img.shields.io/pypi/v/ping-before-wakeonlan.svg)](https://pypi.org/project/ping-before-wakeonlan)
[![PyPI Downloads](https://static.pepy.tech/badge/ping-before-wakeonlan)](https://pepy.tech/projects/ping-before-wakeonlan)

Meet this Python Wake-on-LAN (WOL) Tool! It smartly checks your device status with integrated ping before sending the magic packet, ensuring efficiency. Set max wake devices, prevent power surges.

# Installation

```
% pip install ping-before-wakeonlan
```

or

```
% python3 -m venv venv
% source venv/bin/activate
% pip install ping-before-wakeonlan
% ./venv/bin/ping-before-wakeonlan
```

```
{
    "count": 0,
    "device": {
        "failed": [],
        "handled": [],
        "input": [],
        "online": [],
        "skip": []
    },
    "info": [
        "--device-info not set empty",
        "stdin empty"
    ],
    "maxCount": 5,
    "ping": "ping -c 1 -W 3",
    "version": "1.0.0"
}
usage: cmd.py [-h] [--max-wol-device MAX_WOL_DEVICE] [--send-mode {sequential,random}] [--silently] [--ping-cmd PING_CMD]
              [--device-info DEVICE_INFO]

A Simple Tool for Ping and WOL Usage

options:
  -h, --help            show this help message and exit
  --max-wol-device MAX_WOL_DEVICE
                        WOL device number per a run
  --send-mode {sequential,random}
                        Adjust the order of input device
  --silently            Process Report
  --ping-cmd PING_CMD   Ping command for test device
  --device-info DEVICE_INFO
                        a file path with JSON format with [{"ip": "192.168.1.2", "macAddress":"XX:XX:XX:XX:XX:XX"} ]
```

# Usage

```
% cat /tmp/device.json
[
   {
       "ip": "192.168.1.1",
       "mac_address": "00:00:00:00:00:01"
   },
   {
       "ip": "192.168.1.2",
       "mac_address": "00:00:00:00:00:02"
   },
   {
       "ip": "192.168.1.3",
       "mac_address": "00:00:00:00:00:03"
   },
   {
       "ip": "192.168.1.4",
       "mac_address": "00:00:00:00:00:04"
   },
   {
       "ip": "192.168.1.5",
       "mac_address": "00:00:00:00:00:05"
   },
   {
       "ip": "192.168.1.6",
       "mac_address": "00:00:00:00:00:06"
   },
   {
       "ip": "192.168.1.7",
       "mac_address": "00:00:00:00:00:07"
   }
]

% ping-before-wakeonlan --device-info /tmp/device.json
Process: 1 / 7: Device: {'ip': '192.168.1.3', 'mac_address': '00:00:00:00:00:03'}
Process: 2 / 7: Device: {'ip': '192.168.1.2', 'mac_address': '00:00:00:00:00:02'}
Process: 3 / 7: Device: {'ip': '192.168.1.1', 'mac_address': '00:00:00:00:00:01'}
Process: 4 / 7: Device: {'ip': '192.168.1.4', 'mac_address': '00:00:00:00:00:04'}
Process: 5 / 7: Device: {'ip': '192.168.1.5', 'mac_address': '00:00:00:00:00:05'}
{
    "count": 5,
    "device": {
        "failed": [],
        "handled": [
            {
                "ip": "192.168.1.3",
                "mac_address": "00:00:00:00:00:03"
            },
            {
                "ip": "192.168.1.2",
                "mac_address": "00:00:00:00:00:02"
            },
            {
                "ip": "192.168.1.1",
                "mac_address": "00:00:00:00:00:01"
            },
            {
                "ip": "192.168.1.4",
                "mac_address": "00:00:00:00:00:04"
            },
            {
                "ip": "192.168.1.5",
                "mac_address": "00:00:00:00:00:05"
            }
        ],
        "input": [
            {
                "ip": "192.168.1.3",
                "mac_address": "00:00:00:00:00:03"
            },
            {
                "ip": "192.168.1.2",
                "mac_address": "00:00:00:00:00:02"
            },
            {
                "ip": "192.168.1.1",
                "mac_address": "00:00:00:00:00:01"
            },
            {
                "ip": "192.168.1.4",
                "mac_address": "00:00:00:00:00:04"
            },
            {
                "ip": "192.168.1.5",
                "mac_address": "00:00:00:00:00:05"
            },
            {
                "ip": "192.168.1.6",
                "mac_address": "00:00:00:00:00:06"
            },
            {
                "ip": "192.168.1.7",
                "mac_address": "00:00:00:00:00:07"
            }
        ],
        "online": [],
        "skip": [
            {
                "ip": "192.168.1.6",
                "mac_address": "00:00:00:00:00:06"
            },
            {
                "ip": "192.168.1.7",
                "mac_address": "00:00:00:00:00:07"
            }
        ]
    },
    "info": [
        "cmd: ['ping', '-c', '1', '-W', '3', '192.168.1.1'], item: {'ip': '192.168.1.1', 'mac_address': '00:00:00:00:00:01'}",
        "processOutput: b'PING 192.168.1.1 (192.168.1.1): 56 data bytes\\n\\n--- 192.168.1.1 ping statistics ---\\n1 packets transmitted, 0 packets received, 100.0% packet loss\\n', processError: None"
    ],
    "maxCount": 5,
    "ping": "ping -c 1 -W 3",
    "status": true,
    "version": "1.0.0"
}
```

or

```
% cat /tmp/device.json | ping-before-wakeonlan
```
