---
key: pypi/fiberfox
source: pypi
name: fiberfox
package: fiberfox
description: High-performance (D)DoS vulnerability testing toolkit. Various L4/7 attack vectors. Async
  networking.
registry_url: https://pypi.org/project/fiberfox/
version: 0.3.7
last_release: '2022-04-13'
repository_url: https://github.com/kachayev/fiberfox
repository_declared_in_metadata: true
license_stated: MIT
author: Oleksii Kachaiev
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# FiberFox 🦊  

High-performance (D)DoS vulnerability testing toolkit. Implements various L4/7 attack vectors. The async approach to networking helps to lower CPU/RAM requirements while performing even complex network interactions.

**NOTE** 👻 The toolkit doesn't have the capabilities needed for proper performance testing of the target servers or networks. The goal is to understand the level of protection, by performing attacks specially designed to abuse common pitfalls and bypass common protection measures.

**WARNING**❗ Do not test infrastructure (servers, websites, network devices, etc) without the owner's consent. Package default settings are tuned to avoid a large unintended impact when running tests.

Inspired by [MHDDoS](https://github.com/MHProDev/MHDDoS) project.

![analysis](docs/fiberfox_analysis.png)

## Install

From PyPI:

```shell
$ pip install fiberfox
```

From sources:

```shell
$ git clone https://github.com/kachayev/fiberfox.git
$ cd fiberfox
$ python setup.py install
```

Build Docker image:

```shell
$ git clone https://github.com/kachayev/fiberfox.git
$ cd fiberfox
$ docker build -t fiberfox .
```

## Usage

Example:

```shell
$ fiberfox \
    --targets tcp://127.0.0.1:8080 http://127.0.0.1:8081 \
    --concurrency 512 \
    --rpc 1024 \
    --strategy STRESS \
    --duration-seconds 3600 \
    --proxies-config ./proxies.txt
```

Features:
* `--concurrency` (or `-c`) defines the number of async coroutines to run. Fiber doesn't create a new OS thread so you can run a lot of them with insignificant overhead. For TCP attack vectors, number of fibers roughly corresponds to the max number of open TCP connections. For UDP attacks, running too many fibers typically makes performance worse.
* Multiple targets are supported. Each fiber picks up a target by cycling over the list of them. If the fiber session is too long (e.g. when using attack vectors like `SLOW` or `CONNECTIONS`), make sure to set up more fibers than you have targets.
* Connections could be established using HTTP/SOCK4/SOCK5 proxies. Available proxies could be setup from the static configuration file or dynamically resolved from proxy providers. The tool automatically detects "dead" proxies and removes them from the pool.

More documentation about flags:

```
$ python fiberfox --help
usage: fiberfox [-h] [--targets [TARGETS ...]] [--targets-config TARGETS_CONFIG] [-c CONCURRENCY] [-s {UDP,TCP,STRESS,BYPASS,CONNECTION,SLOW,CFBUAM,AVB,GET}] [--rpc RPC] [--packet-size PACKET_SIZE]
               [-d DURATION_SECONDS] [--proxies [PROXIES ...]] [--proxies-config PROXIES_CONFIG] [--proxy-providers-config PROXY_PROVIDERS_CONFIG] [--log-level {DEBUG,INFO,ERROR,WARN}]
               [--connection-timeout-seconds CONNECTION_TIMEOUT_SECONDS]

options:
  -h, --help            show this help message and exit
  --targets [TARGETS ...]
                        List of targets, separated by spaces (if many)
  --targets-config TARGETS_CONFIG
                        File with the list of targets (target per line). Both local and remote files are supported.
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Total number of fibers (for TCP attacks means max number of open connections)
  -s {UDP,TCP,STRESS,BYPASS,CONNECTION,SLOW,CFBUAM,AVB,GET}, --strategy {UDP,TCP,STRESS,BYPASS,CONNECTION,SLOW,CFBUAM,AVB,GET}
                        Flood strategy to utilize
  --rpc RPC             Number of requests to be sent to each connection
  --packet-size PACKET_SIZE
                        Packet size (in bytes)
  -d DURATION_SECONDS, --duration-seconds DURATION_SECONDS
                        How long to keep sending packets, in seconds
  --proxies [PROXIES ...]
                        List of proxy servers, separated by spaces (if many)
  --proxies-config PROXIES_CONFIG
                        File with a list of proxy servers (newline-delimited). Both local and remote files are supported.
  --proxy-providers-config PROXY_PROVIDERS_CONFIG
                        Configuration file with proxy providers (following MHDDoS configuration file format). Both local and remote files are supported.
  --reflectors-config REFLECTORS_CONFIG
                        File with the list of reflector servers (IP per line). Only required for amplification attacks. Both local and remote files are supported.
  --log-level {DEBUG,INFO,ERROR,WARN}
                        Log level (defaults to INFO)
  --connection-timeout-seconds CONNECTION_TIMEOUT_SECONDS
                        Proxy connection timeout in seconds (default: 10s)
```

## Attack Vectors

An attack vector is defined by `--strategy` option when executing the script.

Note: the package is under active development, more methods will be added soon.

### L4

L4 attacks are designed to target transport layers and thus are mainly used to overload network capacities. Requires minimum knowledge of the target.


| Strategy   | Layer | Transport | Design | Notes |
|----------- |-------|-----------|--------|-------|
| `UDP` | L4 | UDP | Simple flood: sends randomly generated UDP packets to the target | Automatically throttles fiber on receiving `NO_BUFFER_AVAILABLE` from the network device. To prevent this from happening do not configure more than 2 fibers per target when testing UDP flood attack. |
| `TCP` | L4 | TCP | Simple flood: sends RPC randomly generated TCP packets into an open TCP connection. | Supports configuration for the size of a single packet and the number of packets to be sent into each open connection. |
| `CONNECTION` | L4 | TCP | Opens TCP connections and keeps them alive as long as possible. | To be effective, this type of attack requires a higher number of fibers than usual. Note that modern servers are pretty good at handling open inactive connections. |

### UDP-based Amplification Attacks

A special class of L4 attacks.

UDP is a connectionless protocol. It does not validate the source IP address unless explicit processing is done by the application layer. It m
