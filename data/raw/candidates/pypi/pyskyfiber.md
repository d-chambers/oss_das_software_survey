---
key: pypi/pyskyfiber
source: pypi
name: pyskyfiber
package: pyskyfiber
description: Skycoin Python Library
registry_url: https://pypi.org/project/pyskyfiber/
version: 0.27.0.dev1
last_release: '2019-12-08'
repository_url: https://github.com/fibercrypto/pyskyfiber
repository_declared_in_metadata: true
license_stated: null
author: Maykel Arias
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# PySkycoin

[![Build Status](https://travis-ci.com/fibercrypto/pyskycoin.svg?branch=develop)](https://travis-ci.com/fibercrypto/pyskycoin)

Python extension for Skycoin API.
A Python extension generated with SWIG to access Skycoin API from Python.

## Table of Contents

<!-- MarkdownTOC levels="1,2,3,4,5" autolink="true" bracket="round" -->
- [Installation](#installation)
- [Using the API](#usage)
  - [Naming](#naming)
  - [Parameters](#parameters)
    - [Handles](#handles)
    - [Byte Slices](#byte-slices)
    - [Structures](#structures)
    - [Fixed Size Arrays](#fixed-size-array)
    - [Other Slices](#other-slices)
    - [Memory Managemanet](#memory-management)
- [Make rules](#make-rules)
- [Development setup](#development-setup)
  - [Running tests](#running-tests)
  - [Releases](#releases)
    - [Update the version](#update-the-version)
    - [Pre-release testing](#pre-release-testing)
    - [Release signing](#release-signing)
    - [Alternative signing keys](#alternative-signing-keys)
    - [Creating release builds](#creating-release-builds)
    - [Creating release builds to manylinux](#creating-release-builds-to-manylinux)
- [Python wrapper for Skycoin Api](#python-wrapper-for-skycoin-api)
<!-- /MarkdownTOC -->

## Installation

Download the repository from http://github.com/fibercrypto/pyskycoin.git. 
Execute (`python setup.py install`) to install the library. Although executing (python setup.py develop) is a better choice for making changes to the library. However, when using tox these commands are not required at all because calling tox will make any necessary installation and execute the tests.

## Usage
### Naming

The exported function in PySkycoin have the following naming format: `SKY_package_func_name` where package is replace by the package where the original Skycoin function is and func_name is the name of the function. For example, `LoadConfig` function from `cli` package is called in Python `SKY_cli_LoadConfig`
### Parameters

All skycoin exported functions return an error object as the last of the return parameters. In Pyskycoin error is return as an integer and it is the first return parameter. The rest of the parameters are returned in the same order.

Receivers in Skycoin are the first of the input parameters. Simple types, like integer, float, string will be used as the corresponding types in Python.

#### Handles

Some of Skycoin types are too complex to be exported to a scripting language. So, handles are used instead. Therefore all functions taking a complex type will receive a handle instead of the original Skycoin type. For example, having these functions exported from Skycoin:

```go
	func LoadConfig() (Config, error)
	func (c Config) FullWalletPath() string
```


Config is a struct type that is treated as a handle in Pyskycoin. The usage in Python will be:

```python

import skycoin
	
def main:
	err, configHandle = skycoin.SKY_cli_LoadConfig()
	if err == skycoin.SKY_OK:  # 0 then no error
		fullWalletPath = skycoin.SKY_cli_FullWalletPath(configHandle)
		print fullWallerPath
		#Close the handle after using the it
		#so the garbage collector can delete the object associated with it. 
		skycoin.SKY_handle_close( configHandle )
	else: 
		#Error
		print err
```

#### Byte slices

Parameters of type byte[] will treated as string . Example, this function in Skycoin:

```go
func (s ScryptChacha20poly1305) Encrypt(data, password []byte) ([]byte, error)
```

Will be called like this:

```python
encrypt_settings = skycoin.encrypt__ScryptChacha20poly1305()
data = "Data to encrypt" #It will be passed as a parameter of type []byte
pwd = "password"         #As []byte too
err, encrypted = skycoin.SKY_encrypt_ScryptChacha20poly1305_Encrypt(encrypt_settings, data, pwd)
if err == skycoin.SKY_OK:
	print encrypted #Encrypted is string
```

#### Structures

Structures that are not exported as handles are treated like classes in Python. In the previous example type ScryptChacha20poly1305 is created in Python like:

```python
encrypt_settings = skycoin.encrypt__ScryptChacha20poly1305()
```

And passed as first parameter in call to SKY_encrypt_ScryptChacha20poly1305_Encrypt.

#### Fixed Sized Arrays

Parameters of fixed size array are wrapped in structures when called from python.

Given these types in Skycoin:

```go
	type PubKey [33]byte
	type SecKey [32]byte
```

And this exported function:

```go
	func GenerateDeterministicKeyPair(seed []byte) (PubKey, SecKey)
```
	
This is how it is used in Python:

```python
#Generates random seed
err, data = skycoin.SKY_cipher_RandByte(32)
assert err == skycoin.SKY_OK
pubkey = skycoin.cipher_PubKey()
seckey = skycoin.cipher_SecKey()
err = skycoin.SKY_cipher_GenerateDeterministicKeyPair(data, pubkey, seckey)
```

pubkey and seckey are objects of type structure containing a field name data for the corresponding type of PubKey and SecKey. Something like:

```cpp
	cipher_PubKey struct{
		data [33]byte;
	} cipher_PubKey;

	cipher_SecKey struct{
		data [32]byte;
	} ;
```

#### Other Slices

Other slices of type different than byte were wrapped inside classes. Calling the following function:

```go
func GenerateDeterministicKeyPairs(seed []byte, n int) []SecKey
```
	
Would be like:

```python
#Generates random seed
err, seed = skycoin.SKY_cipher_RandByte(32)
err, seckeys = skycoin.SKY_cipher_GenerateDeterministicKeyPairs(seed, 2)
for seckey in seckeys:
	pubkey = skycoin.cipher_PubKey()
	skycoin.SKY_cipher_PubKeyFromSecKey(seckey, pubkey)
	err = skycoin.SKY_cipher_PubKey_Verify(pubkey)
	assert err == skycoin.SKY_OK
```

## Example of how to verify address

```python
def addressIsValid(addr):
    addres = skycoin.cipher__Address()
    err = skycoin.SKY_cipher_DecodeBase58Address(addr, addres)
    return err != skycoin.SKY_OK
```


### Memory Management

Memory management is transparent to the user. Any object allocated inside the library is left to be managed by Python garbage collector.

## Make Rules

All these make rules require skycoin to be a g
