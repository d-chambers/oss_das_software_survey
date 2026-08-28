---
key: pypi/itksnap-dss
source: pypi
name: itksnap-dss
package: itksnap-dss
description: Python client for ITK-SNAP Distributed Segmentation Service (DSS)
registry_url: https://pypi.org/project/itksnap-dss/
version: 0.1.0
last_release: '2026-02-04'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: Paul Yushkevich <pyushkevich@gmail.com>
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Alfabis Python Client for ITK-SNAP DSS

A Python client library for interacting with the ITK-SNAP Distributed Segmentation Service (DSS) middleware as a service provider.

## Overview

The ITK-SNAP DSS (Distributed Segmentation Services) is an architecture that enables medical image segmentation algorithms to be deployed as web services. This Python client allows algorithm developers to create service providers that claim processing tickets, download input data, perform segmentation, and upload results back to the DSS middleware server.

For comprehensive DSS documentation, visit: https://alfabis-server.readthedocs.io/en/latest/

## DSS Architecture

The DSS system consists of three layers:

- **Client**: GUI (ITK-SNAP) or command-line tools (itksnap-wt) that submit processing requests
- **Middleware**: Web application (e.g., https://dss.itksnap.org) that orchestrates communication
- **Service Providers**: Algorithm implementations that process tickets (this library helps you build these)

## Installation

```bash
pip install itksnap-dss
```

## Quick Start

### 1. Connect and Authenticate

```python
from itksnap_dss import DSSClient

# Connect to DSS middleware server
client = DSSClient('https://dss.itksnap.org')

# Authenticate (you'll be prompted for a token from the server)
client.login()
```

### 2. List Available Services

```python
# See which services you're registered to provide
services = client.dssp_list_services()
print(services)
#              service version                                      hash provider
# 0        MRI-NeckCut   1.0.0  e0a316038e9cbe6a000e07c82758532a8863f51f     test
# 1  RegistrationExample   0.1.0  b7392368dc5dcec910bb8b87006ae38fd1f2cb32  testlab
```

### 3. Claim and Process a Ticket

```python
# Extract service hash from the services list
service_hash = services['hash'].iloc[0]

# Claim a ticket for this service
ticket_df = client.dssp_claim_ticket(
    services=[service_hash],
    provider='testlab',
    provider_code='instance_1'
)

if ticket_df is not None:
    ticket_id = ticket_df['ticket'].iloc[0]
    print(f"Claimed ticket {ticket_id}")
    
    # Download input files
    client.dssp_download_ticket(ticket_id, f'/tmp/ticket_{ticket_id}')
    
    # Process the data (your algorithm here)
    # ...
    
    # Update progress and log messages
    client.dssp_log(ticket_id, 'info', 'Processing started')
    client.dssp_set_progress(ticket_id, 0.5)  # 50% complete
    
    # Attach intermediate results
    client.dssp_attach(ticket_id, 'Quality metrics', 'metrics.txt', 'text/plain')
    client.dssp_log(ticket_id, 'info', 'Quality check passed')
    
    # Mark as complete
    client.dssp_set_progress(ticket_id, 1.0)
    client.dssp_set_status(ticket_id, 'success')
else:
    print("No tickets available")
```

### 4. Wait for Tickets (Daemon Mode)

```python
# Continuously wait for tickets with timeout
while True:
    ticket_df = client.dssp_wait_for_ticket(
        services=[service_hash],
        provider='testlab',
        provider_code='instance_1',
        timeout=300,  # Wait up to 5 minutes
        interval=15   # Check every 15 seconds
    )
    
    if ticket_df is not None:
        # Process ticket...
        pass
```

## Service Provider Workflow

A typical service provider follows this workflow:

1. **List Services** - Check which services you're registered for
2. **Claim Ticket** - Get the next available processing job
3. **Download Files** - Retrieve input data for the ticket
4. **Process Data** - Run your segmentation algorithm
5. **Update Progress** - Keep users informed during processing
6. **Log Messages** - Provide status updates, warnings, or errors
7. **Attach Files** - Upload intermediate results or quality metrics
8. **Upload Results** - Send processed data back to server (Note: upload method not yet implemented in this client)
9. **Mark Status** - Set ticket as 'success' or 'failed'

## API Reference

### Connection & Authentication

#### `DSSClient(server, verify=True)`
Initialize a connection to the DSS middleware server.

**Parameters:**
- `server` (str): Server URL (e.g., 'https://dss.itksnap.org')
- `verify` (bool): Verify SSL certificates (default: True)

#### `login(token=None)`
Authenticate with the server using a 40-character token.

**Equivalent CLI:** `itksnap-wt -dss-auth <server>`

### Service Management

#### `dssp_list_services()`
List all services you're registered as a provider for.

**Returns:** DataFrame with columns: service, version, hash, provider

**Equivalent CLI:** `itksnap-wt -dssp-services-list`

### Ticket Management

#### `dssp_claim_ticket(services, provider, provider_code)`
Claim the next available ticket for one or more services.

**Parameters:**
- `services` (List[str]): Service git hashes
- `provider` (str): Provider identifier
- `provider_code` (str): Unique instance identifier

**Returns:** DataFrame with ticket info, or None if no tickets available

**Equivalent CLI:** `itksnap-wt -dssp-services-claim <service_hash_list> <provider> <instance_id>`

#### `dssp_wait_for_ticket(services, provider, provider_code, timeout=300, interval=15)`
Wait for a ticket to become available.

**Equivalent CLI:** `itksnap-wt -dssp-services-claim <service_hash_list> <provider> <instance_id> <timeout>`

#### `dssp_download_ticket(ticket, outdir)`
Download all input files for a ticket to a directory.

**Equivalent CLI:** `itksnap-wt -dssp-tickets-download <id> <dir>`

### Progress & Logging

#### `dssp_set_progress(ticket, progress, chunk_start=0.0, chunk_end=1.0)`
Update processing progress (values in range [0, 1]).

**Equivalent CLI:** `itksnap-wt -dssp-tickets-set-progress <id> <start> <end> <value>`

#### `dssp_log(ticket, category, message)`
Add a log message (category: 'info', 'warning', or 'error').

**Equivalent CLI:** `itksnap-wt -dssp-tickets-log <id> <type> <msg>`

#### `dssp_attach(ticket, desc, filename, mime_type='')`
Attach a file to be linked with the next log message.

**Equivalent CLI:** `i
