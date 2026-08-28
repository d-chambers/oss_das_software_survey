---
key: pypi/dfiber
source: pypi
name: dfiber
package: dfiber
description: A Python package to query Dfiber, execute queries, and return results as a DataFrame
registry_url: https://pypi.org/project/dfiber/
version: 0.1.2
last_release: '2025-01-28'
repository_url: https://github.com/dview-io/dfiber
repository_declared_in_metadata: true
license_stated: MIT
author: Kauts Shukla
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Dfiber

## Project Description

**Dfiber** is a Python utility that simplifies connecting to Dview's Aqua and executing SQL queries. It supports flexible authentication methods, including:

- **API Key**
- **User Email/Password**
- **Cookies**

Dfiber automatically handles the connection setup and provides seamless query execution, ensuring efficient interaction with your data sources.
## Features

- Library for connecting with Dview
- Flexible authentication methods
- Executes SQL queries and returns results

## Installation

To install Dfiber, use the following pip command:

```bash
pip install dfiber
```
## Note
- Before using Dfiber, make sure that the `DFIBER_ENDPOINT` environment variable is set on your system. This variable defines the connection endpoint to Dfiber's service
```bash
export DFIBER_ENDPOINT="dfiber://<host>:<port>/<catalog>/<schema>"
```

## Usage

### Dfiber Authentication Methods
* First, import the necessary classes from the dfiber package to work with credentials and authentication methods:

```python
from dfiber import Credentials
from dfiber import AuthMethod
```
1. ##### API Key Authentication  (Preferred Way)
* If you prefer API key-based authentication, you can generate an API key from the [Dview.io profile page](https://cloud.dview.io/profile). Simply create your key and use it in the api_key field.
```python
# Credentials for API key-based authentication
credentials = Credentials(
    api_key="<api_key>",  # Required for api-key-based authentication
    auth_method=AuthMethod.API_KEY  # Specify the chosen auth method
)
```
2. ##### UserEmail-Password Authentication
* To use email-password-based authentication, you must provide both a user email and a password. This method is ideal for logging in with your personal account credentials.

```python
# Credentials for email-password-based authentication
credentials = Credentials(
    email="<email>", # Required for email-password-based authentication
    password="<password>", # Required for email-password-based authentication
    auth_method=AuthMethod.EMAIL_PASSWORD  # Specify the chosen auth method
)
```

3. ##### Cookie Based Authentication
* For cookie-based authentication, pass the cookie token that you obtained after logging in with your email and password. This cookie can be used for subsequent requests to authenticate automatically. Only the cookie is required for this method—there’s no need to provide the email or password again.
* However, the cookie has a specific time limit and will expire after a set period. Once the cookie expires, you will need to log in again to obtain a new cookie token.
```python

# Credentials for cookie-based authentication
credentials = Credentials(
    cookie="<cookie>",  # Required for cookie-based authentication
    auth_method=AuthMethod.COOKIE  # Specify the chosen auth method
)
```

#### Note:
Here Credentials can also be passed as a dictionary in this way:

```python
credentials_dict = {
    "email": "<email>",
    "password": "<password>",
    "auth_method": AuthMethod.EMAIL_PASSWORD
}
```

### Querying using Dfiber Class

* `Dfiber` class allows you to easily interact with Dview's services. The primary way to use it is by passing your credentials, catalog, and an optional schema. Additionally, you can specify the Dfiber endpoint either via environment variable `DFIBER_ENDPOINT` or directly through the class constructor.

#### Dfiber Class Overview

- **catalog**: This is a required parameter and must always be provided. It specifies which catalog to query against.
######
- **schema**: This is optional in both the `dfiber_endpoint` string and the Dfiber class constructor. If a schema is provided in both places (environment variable and the constructor), the one passed to the class takes precedence.
######
- **dfiber_endpoint**: This is an optional parameter that can be passed to the Dfiber. If it's not provided, Dfiber will look for the `DFIBER_ENDPOINT` environment variable. If both are provided, the constructor’s parameter will override the environment variable.
######
- **cosmos_endpoint**: This is an optional parameter for the Dfiber class. If not provided, it will fallback to the value of the `DVIEW_COSMOS_ENDPOINT` environment variable. If both the parameter and environment variable are set, the parameter passed to the constructor will take precedence.

######

The Dfiber Endpoint follows the format:
```bash
DFIBER_ENDPOINT="dfiber://<host>:<port>/<catalog>/<schema>"
```
Here, `<host>`, `<port>`, `<catalog>`, and `<schema>` need to be replaced with appropriate values. The schema part is optional, and if omitted, Dfiber will use the schema you provide directly.

## Examples

##### 1. Using Dfiber Class with Catalog Only

- In this case, the Dfiber class will use the `DFIBER_ENDPOINT` from your environment variable (if it's set) and the catalog passed to the class. If the schema is omitted in both the Dfiber endpoint and class, you can still specify it directly within your query, and Dfiber will handle the query accordingly.

```python
from dfiber import Dfiber, AuthMethod

# Define credentials
credentials_dict = {
    "email": "<email>",
    "password": "<password>",
    "auth_method": AuthMethod.EMAIL_PASSWORD
}

# Dfiber instance with catalog only, Dfiber will pick up endpoint from the environment variable
dfiber = Dfiber(credentials=credentials_dict, catalog="<catalog>")

# Execute a query
result_df = dfiber.execute_query("<your_query>")
```
##### 2. Using Custom Dfiber Endpoint and catalog override

- If you wish to pass a custom `dfiber_endpoint` directly in the constructor, Dfiber will override the one set in the environment variable(`DFIBER_ENDPOINT`).  
- The catalog in the `dfiber_endpoint` can be overridden by the catalog passed into the Dfiber class.

```python
from dfiber import Dfiber, AuthMethod, Credentials

# Define credentials
credentials = Credentials(
    cookie="<cookie>",
    auth_method=AuthMethod.COOKIE
)

# Dfiber instance with custo
