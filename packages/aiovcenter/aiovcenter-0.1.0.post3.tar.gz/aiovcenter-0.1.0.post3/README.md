# aiovcenter

`aiovcenter` is an asynchronous Python library for interacting with VMware vCenter APIs. It provides convenient classes and methods to manage vCenter resources using asyncio.

## Features

- Async support for vCenter REST APIs
- Manage VMs, hosts, datastores, and networks
- Easy authentication and session management
- Typed responses and error handling

## Installation

```bash
pip install aiovcenter
```

## Usage

```python
import asyncio
from aiovcenter import VCenterClient

async def main():
    async with VCenterClient(
        host="vcenter.example.com",
        username="username",
        password="password",
        verify_ssl=False
    ) as client:
        vms = await client.vms.list()
        for vm in vms:
            print(vm.name)

asyncio.run(main())
```

## Documentation

- [API Reference](https://github.com/yourusername/aiovcenter#api-reference)
- [Examples](https://github.com/yourusername/aiovcenter#examples)

## License

This project is licensed under the MIT License.

