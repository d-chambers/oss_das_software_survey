---
key: pypi/dss-netapi-python
source: pypi
name: dss.netapi-python
package: dss-netapi-python
description: A small Python3-layer for accessing Network-Data via the NetAPI.
registry_url: https://pypi.org/project/dss-netapi-python/
version: 0.0.3.dev5
last_release: '2023-12-06'
repository_url: null
repository_declared_in_metadata: false
license_stated: null
author: '"Tino Schöllhorn, Pavel Chachev, Olaf Kellermeier, Achim Oberg" <schoellhorn@ifm.uni-mannheim.de>,
  Pavel Chachev <pavel.dimitrov.chachev@uni-hamburg.de>, Olaf Kellermeier <olaf.kellermeier@uni-hamburg.de>,
  Achim Oberg <achim.oberg@uni-hamburg.de>'
probes:
- pypi:simple-index-sweep
probe_class: broad-acronym
found_by:
- search
first_seen: '2026-08-28'
---

# Table of Contents
- [Introduction](#introduction)
- [Installation and configuration](#installation-and-configuration)
- [Usage and examples](#usage-and-examples)
- [Development](#development)

# Introduction
Graphs or networks are everywhere and are of great interest for researchers.
Examples of interesting sources of social networks are: 
- Social Media such as Facebook, Twitter provide networks of "friends". 
- Crawlers provide networks of documents or hosts
- Collections of research papers can be regarded as interaction networks of 
individuals or organisations

The NetAPI aims to provide a framework to enables the use of 
project-specific data-structures and a normalized view of the requested graphs. 
Thus, this approach allows for specialization of researchers: 
researches providing a specific implementation of a NetAPI-Server 
using the raw data and other researchers accessing this data for answering 
specific research questions.  

The **NetAPI-Server** is a server component with endpoints providing access to such -
possibly dynamic - graphs. It provides the possibility to answer queries 
using a specific QueryEngine. 

In a NetAPI-Server implementations of *Graph Sources* provide events to create graphs. 
Typically a project requires a specific implementation which is responsible to create 
Events building a graph from the raw data.

A **NetAPI-Client** implementation enables researches to access the data of 
a NetAPI-Server in a standardized way - independent of the actual raw data. 
Thus networks of social media and crawled data can be accessed in the same manner. 

**This package** provides a Python3 client for accessing NetAPI-Server which simplifies 
creating and sending queries to the NetAPI and to transform the responses to a graph. 
This can then be easily be used for further processes in Python.

This architecture is depicted in the following image:

```

 ---------------          -------------------
| QueryEngine 	|  <==>  | dss.netapi-client |
 ---------------          -------------------
  NetAPI-Server              NetAPI-Client
   e.g. QKnow
   
```

# Installation and configuration
The `dss-netapi-python` package has to be installed via pip - 
the package installer for Python. Two variants can be installed: 
a published stable version or the current development version. 

Normally, it is preferable to use the published stable version in a 
separate *virtual environment* in your projects source folder: 

	py -m venv .venv # creates the environment
	.venv\Scripts\Activate.bat # might also be .venv\bin\Activate.bat

More info on this topic can be found here: https://docs.python.org/3/library/venv.html

The current stable version can be installed via a pip-command:

	py -m pip install dss-netapi-python --user

If you already have a installed version of `dss-netapi-python` 
in your local environment it can be updated using the following pip-command:

	py -m pip install --upgrade dss-netapi-python

## Configuration
The NetAPIClient makes requests to another server. Users have to 
authenticate to the server to allow authorization to the requested resources. 

Clients of the NetAPI can be configured via the file `~/.netapi/config` 
(~ is the usual abbreviation of the current user's home directory). 
An example of such a configuration file can be found below:

	[default] #<1>
	host=https://qknow-dc.dev.plattform-gmbh.de #<2>
	token=atoken #<3>

	[qknow-live] #<4>
	host=https://qknow-dc.live.plattform-gmbh.de
	token=anothertoken	
----
1. A profile `default` is defined
2. The URL of the host where the NetAPI-Server resides
3. An authentication token.
4. A second profile `qknow-live` is defined

These profiles can be used thto construct a suitable instance 
for the communication with the server. 
This will be demonstrated in the following source code examples.

# Usage and examples
This section makes examples how to use the *dss-netapi-python* package.

### Example 1: Reading a graph
Demonstrates the most basic form of interaction with the NetAPI: reading a graph.

```
from netapi import * #<1>

client = NetAPIClient.fromConfig("default") #<2>

req = GraphQueryRequest()\
      .setSource("InputStreamReplayToSource", "MiniGraph.dgs") #<3>
res = client.query(req) #<4>

graphModel = res.getGraphModel() #<5>
graph = graphModel.asMultiDiGraph() #<6>

print(graph)
```
---
1. Imports the netapi-module
2. Creates a new instance of the NetAPIClient from the profile "default" using the configuration file.
3. Creates a request using the a InputStreamReplayToSource and a well-known file (actually a file for test-cases)
4. Sends the query and receives the response object
5. Extracts the generic graph model
6. Creates a networkx-view of the graph model. In this case a directed graph allowing for multiple edges between nodes.

### Example 2: Tagging
TODO

### Example 3: Aggregating nodes
TODO

### Example 4: Filter nodes and edges
- Wenn man Prädikate definiert, wird "true" für Java klein geschrieben.
Nicht wie bei Python groß.
z.B setSelection(Selection().setNodePredicate("attributes.egoA=true"))


# Developing
Sources:
- https://docs.python-guide.org/writing/structure/
- https://docs.python.org/3/library/unittest.html

## Installing the development version
In rare cases you might want to use the development version. 
The development version can be installed as a regular pip-module. 
The source code can be accessed via a git repository. 
If you have the necessary user authentication, it can be cloned like this:

	git clone https://gitea.plattform-gmbh.de/PlattformGmbH/datacollector.git

After cloning the git repository the pip-module actually has to be installed:

	cd datacollector/netapi-python
	py -m pip install -e .

When changing / updating the source code it is automatically reflected in 
the pip-module. Thus a simple `git pull` of
