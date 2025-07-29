## Overview

`aionsxt` is a Python package designed to interact with VMware NSX-T environments asynchronously. It provides tools for managing NSX-T resources and exporting configurations using modern async programming patterns.

## Main Modules

### `nsxt_client.py`
This module provides the core asynchronous client for communicating with the NSX-T API.

**Key Features:**
- Asynchronous HTTP requests to NSX-T Manager.
- Authentication and session management.
- Methods for retrieving and managing NSX-T resources (e.g., logical switches, routers, segments).

**Example Usage:**
```python
from aionsxt.nsxt_client import NSXTClient
import asyncio

async def main():
    client = NSXTClient(host="nsxt.example.com", username="username", password="password")
    await client.login()
    switches = await client.get_logical_switches()
    print(switches)
    await client.logout()

asyncio.run(main())
```

### `nsxt_export.py`
This module provides utilities to export NSX-T configurations.

**Key Features:**
- Export NSX-T objects and configurations to JSON or other formats.
- Support for selective or full export of NSX-T resources.
- Designed to work seamlessly with `NSXTClient`.

**Example Usage:**
```python
from aionsxt.nsxt_client import NSXTClient
from aionsxt.nsxt_export import export_logical_switches
import asyncio

async def main():
    client = NSXTClient(host="nsxt.example.com", username="username", password="password")
    await client.login()
    await export_logical_switches(client, output_file="switches.json")
    await client.logout()

asyncio.run(main())
```

## Installation

```bash
pip install aionsxt
```

## Requirements

- Python 3.7+
- `aiohttp` or similar async HTTP library

## License

This project is licensed under the MIT License.


