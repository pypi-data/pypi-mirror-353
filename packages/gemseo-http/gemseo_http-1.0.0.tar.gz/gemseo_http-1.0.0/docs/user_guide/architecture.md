<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Architecture

## A client-server architecture

The gemseo-http plugin implements a client-server architecture, which relies on the HTTP protocol.
The server is a [FastAPI](https://fastapi.tiangolo.com/) server that enables to expose GEMSEO disciplines as a RESTful service.
On the server startup, the available disciplines are automatically detected by the factory mechanism,
and, for each discipline, the input and output grammars are exposed.

The server enables the execution of remote discipline by providing two modes:

- A synchronous mode, where the client waits for the server to return the result.
- An asynchronous mode, where the client can send a request to the server and get
a notification when the result is available.

In asynchronous mode, a message broker and a task manager are used to manage the execution of the discipline.
In gemseo-http, the message broker is an [SQLite](https://sqlite.org/) database but could be replaced by another message broker,
such as RabbitMQ or Redis.
The task manager is [Huey](https://huey.readthedocs.io/), which has been chosen as cross-platform and being able to run under Windows.

Also, the server enables the transfer of files between the client and the server, back and forth.

As the gemseo-http is stateless and that the transfer of files,
the execution of disciplines and the retrieval of the results
are carried out during different HTTP calls,
it is necessary to:

- Store the information of each discipline execution (parameters, inputs, outputs, ...) on the server side.
This is done using a SQL database. Currently, an SQLite database has been tested,
but a SQL server database such as PostgreSQL could be used as well.
- For a compute session, keep a session id on the client side.
This id is used to retrieve the information of the discipline execution.


![gemseo-http architecture](img/gemseo_http_architecture.png)
