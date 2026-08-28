---
key: pypi/fibertrace
source: pypi
name: fibertrace
package: fibertrace
description: A library for simple logging
registry_url: https://pypi.org/project/fibertrace/
version: 0.1.5
last_release: '2023-08-09'
repository_url: https://github.com/bytesentinel-io/fibertrace.py
repository_declared_in_metadata: true
license_stated: null
author: ByteSentinel.io
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

<div align="center">
    <img src="./.assets/bytesentinel.png" width="250px" style="margin-left: 10px" />
</div>

<h1 align="center">
  Fibertrace
</h1>

<div align="center">
    <img src="https://img.shields.io/github/downloads/bytesentinel-io/fibertrace.py/total?style=for-the-badge" />
    <img src="https://img.shields.io/github/last-commit/bytesentinel-io/fibertrace.py?color=%231BCBF2&style=for-the-badge" />
    <img src="https://img.shields.io/github/issues/bytesentinel-io/fibertrace.py?style=for-the-badge" />
</div>

<br />

Fibertrace is a Python package that provides a logging utility for capturing and managing log entries in your applications. It offers a simple and customizable way to log messages with different log levels, timestamps, application names, modules, and user information.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/Z8Z8JPE9P)

# Installation

To use Fibertrace, make sure you have Python installed on your system. You can install the package using pip:

```shell
pip install fibertrace
```

# Usage

To get started with Fibertrace, you need to create a logger instance by calling the Logger class constructor. The constructor requires the log file path, application name, and a flag indicating whether to use JSON format for log entries.

```python
from fibertrace import Logger

log_file_path = "log.txt"
application = "MyApp"
json_format = False

logger = Logger(log_file_path, application, json_format)
```

Once you have created the logger, you can use it to log messages with different log levels such as `info`, `error`, and `debug`. For example:

```python
logger.info("This is an information message.")
logger.error("This is an error message.")
logger.debug("This is a debug message.")
```

The log messages will be written to the specified log file, along with the corresponding log level, timestamp, application name, module, and user information. Additionally, the log messages will be printed to the console.

# Conclusion

`Fibertrace` simplifies logging in Python applications by providing a flexible and configurable logging utility. It helps you capture and manage log entries with ease, allowing you to track the execution flow, debug issues, and monitor your application's behavior. Feel free to explore the package further and adapt it to your specific logging needs.
For more information and detailed examples, please refer to the package documentation and source code.
