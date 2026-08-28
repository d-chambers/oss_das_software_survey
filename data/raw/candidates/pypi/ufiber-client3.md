---
key: pypi/ufiber-client3
source: pypi
name: ufiber-client3
package: ufiber-client3
description: Ubiquiti UFiber Client for firmware version 3
registry_url: https://pypi.org/project/ufiber-client3/
version: 1.0.1
last_release: '2022-12-16'
repository_url: https://github.com/baldoarturo/ufiber-client
repository_declared_in_metadata: true
license_stated: null
author: Arturo Baldo <baldoarturo@mail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# ufiber-client

This is a quick dirty project built to provide a quick dirty client for Ubiquiti UFiber OLTs, using firmware version 3.x

There is also a CLI attempt, but I couldn't find any ready to use packages to build a decent CLI.

More info about what am I doing this is on the following entries:

- <https://arturobaldo.com.ar/ufiber-olt-api/>
- <https://arturobaldo.com.ar/digging-into-ubiquitis-ufiber-olt/>

## olt.py

This is the core of the project. It uses the OLTCLient class to provide a middleware between you and the HTTP interface of the olt.

Initialize a new OLTClient instance with:

`client = olt.OLTClient(host, username, password)`

The initialization will handle the login for you, altough you can call the `login()` method manually.

If the OLT is network reacheable, and you have provided the right credentials, and the OLT WEB GUI is alive and well, you should be ready to start.

You can also connect using `cli.py`:

```Console
$ /cli.py
UFiber Client for fw version 3.1.3
UFiber> help

Documented commands (type help <topic>):
========================================
connect  help  onu  quit  show

UFiber> connect 10.20.0.101
Username:admin
Password:
Logging to 10.20.0.101 ...
Connection OK
UFiber>
```
