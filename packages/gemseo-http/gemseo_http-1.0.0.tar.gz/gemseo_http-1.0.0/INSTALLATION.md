# Installation of the package
<!--
 Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

 This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
 International License. To view a copy of this license, visit
 http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
 Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->


## Installation of the client

The `HTTPDiscipline` acts as a remote discipline proxy,
and enables to link automatically to a distant GEMSEO HTTP service.
It configures automatically by querying the distant service.
Its execution triggers the execution of a discipline remotely,
and the data (including files),
are automatically transferred back and forth,
and transparently for its user.

Install the latest stable version with `pip install gemseo-http`.
Note that all the dependencies will be downloaded hereafter,
including GEMSEO.
Note that this installation will only package the dependencies needed to run the client.

Install the development version with
`pip install gemseo-http@git+https://gitlab.com/gemseo/dev/gemseo-http.git@develop`.

See [pip](https://pip.pypa.io/en/stable/getting-started/) for more information.

## Installation of the server [webapp and worker]

Install the latest stable version,
including the server dependencies,
with `pip install gemseo-http[server]`.

Install the development version with
`pip install gemseo-http[server]@git+https://gitlab.com/gemseo/dev/gemseo-http.git@develop`.

### Setting up the SQLite Database [server only]

This section can be skipped if you are only using the client.

The web application and worker rely on an SQLite database to store essential data,
including user information,
job details,
and file records.


To set up the database, follow the steps described [here](user_guide/server/database_bootstrap.md)


### Overall server configuration

The application can be configured using environment variables,
that are parsed at runtime.
Those can be defined in a bash script,
or in a `.env` file.
A sample `.env` file is provided in the repository.

The environment variables are as follows:

`SECRET_KEY`: The secret key to encode/decode the JSON web tokens
default: 09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7

`ALGORITHM`: The algorithm to encode/decode the JSON web tokens.
default: HS256

`ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for the token.
default: 10080

`USER_DATABASE_PATH`: Path to the user database.
default:./database.db

`USER_FILE_DIRECTORY`: File workspace directory.
default:./files/

`USER_WORKSPACE_EXECUTION`: User workspace execution.
default:./workdir/

`HUEY_DATABASE_PATH`: Path to the Huey task manager database.
default:./huey.db

`HUEY_IMMEDIATE_MODE`: Whether to trigger the Huey immediate mode.
default: False

`HUEY_IMMEDIATE_MODE_IN_MEMORY`: Whether to trigger the Huey immediate mode in-memory.
default: False

`FASTAPI_DEBUG`: Whether to run FastAPI in debug mode.
default: False

`DATABASE_DEBUG`: Whether to run SQLModel in debug mode.
default: False


### Running the web application

#### Development mode
It is possible to create a development environment using the following command:

`tox -e py[39, 310, 311]

where the Python interpreter version should be selected.

In order to run the web application,
in the activated tox environment,
use the following command in local:

`uvicorn.exe gemseo_http.app.app:app --reload`

The webapp will be reachable at <http://localhost:8000>,
or at the URL you used to

#### Production

It is strongly recommended to read the [Security](#security-note) section,
and implement them.

Also, as `gemseo-http` web application is implemented using FastAPI,
it is recommended to read the following [FastAPI deployment notes](https://fastapi.tiangolo.org/deployment/).

It is also recommended to expose the application as a service,
either using `SystemD` or `Docker`.

Using `SystemD`, the following tree structure is also recommended:

```
/opt/gemseo_http/bin # Contains the running script.
/opt/gemseo_http/log # Contains the log files.
/opt/gemseo_http/database # Contains the SQLite databases, if any.
/opt/gemseo_http/files # Contains the uploaded files.
/opt/gemseo_http/files/chunks # Contains the uploaded file chunks.
/opt/gemseo_http/workdir/ # The jobs workdir.

```

and an example of the running script could be:

```bash
set -e

# Path to the Python environment where gemseo-http is installed
export PATH=/opt/miniconda3/envs/gemseo_http/bin/:$PATH

# Generate a key with: openssl rand -hex 32
export SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
export GAAS_ROOT_PATH=/opt/gemseo_http
export USER_DATABASE_PATH=$GAAS_ROOT_PATH/database/database.db
export USER_FILE_DIRECTORY=$GAAS_ROOT_PATH/files/
export USER_WORKSPACE_EXECUTION=$GAAS_ROOT_PATH/workdir/

uvicorn gemseo_http_server:gemseo_http_server --host 0.0.0.0
```

The service can be managed by to [systemd](https://systemd.io/) using a configuration file like this one:

```shell
[Unit]
Description=GEMSEO_HTTP
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=gemseo_http  # A user and a group gemseo_http have to be created
ExecStart=/usr/bin/bash /opt/gemseo_http/bin/run.sh

StandardOutput=append:/opt/gemseo_http/log/log.out
StandardError=append:/opt/gemseo_http/log/log.err


[Install]
WantedBy=multi-user.target
```

### Running the task manager

For asynchronous requests,
the Huey task manager has to be used to run the jobs.
It enables to decouple the web application from the execution of the jobs.


#### Development mode

To run Huey interactively, type the following command:

`huey_consumer.exe gemseo_http.app.gemseo_runner.huey`

Please have a look at the [Huey](https://huey.readthedocs.io/en/latest/) documentation to see the options available.
For instance, to have two runners using multithreading, use the following command:

`huey_consumer.exe gemseo_http.app.gemseo_runner.huey -k thread -w 2`

The current queuing system is done through SQLLite,
but it has to be noted that other queue managers such as Redis or RabbitMQ
can be user with Huey, but are not implemented yet in ``gemseo-http``.

#### Production

As for the web application, it is recommended to run the Huey worker as a service,\
 using, for instance, SystemD.

The following script could be used to run the Huey worker:

```bash
set -e

export PATH=/opt/miniconda3/envs/gemseo_as_a_service/bin/:$PATH

export GAAS_ROOT_PATH=/opt/gaas
export HUEY_DATABASE_PATH=$GAAS_ROOT_PATH/database/huey.db
export USER_DATABASE_PATH=$GAAS_ROOT_PATH/database/database.db
export USER_FILE_DIRECTORY=$GAAS_ROOT_PATH/files/
export USER_WORKSPACE_EXECUTION=$GAAS_ROOT_PATH/workdir/

huey_consumer gemseo_http_server.gemseo_runner.huey

(base) root@IPF7163:/opt/gaas/bin# set -e

export PATH=/opt/miniconda3/envs/gemseo_as_a_service/bin/:$PATH

export GAAS_ROOT_PATH=/opt/gaas
export HUEY_DATABASE_PATH=$GAAS_ROOT_PATH/database/huey.db
export USER_DATABASE_PATH=$GAAS_ROOT_PATH/database/database.db
export USER_FILE_DIRECTORY=$GAAS_ROOT_PATH/files/
export USER_WORKSPACE_EXECUTION=$GAAS_ROOT_PATH/workdir/

huey_consumer gemseo_http_server.gemseo_runner.huey
```

and the following SystemD script could be used to expose the runner as a system service:

```bash
[Unit]
Description=GEMSEO disciplines as a service worker
After=network.target
StartLimitIntervalSec=0
[Service]
Type=simple
Restart=always
RestartSec=1
User=root
ExecStart=/usr/bin/bash /opt/gaas/bin/run_worker.sh

StandardOutput=append:/opt/gaas/log/log_worker.out
StandardError=append:/opt/gaas/log/log_worker.err


[Install]
WantedBy=multi-user.target
```

### Security note

Please note that exposing an application to Internet can open a security breach.
Be sure to expose ``gemseo-http`` with the state-of-the-art methodology, such as:

- Exposing behind a reverse proxy with SSL/TLS encryption.
- Exposing behind a firewall.
- Exposing on a segregated host (e.g., a compromission of your host does not compromise your whole infrastructure)
- Run in a Docker environment or in a chroot jail

Please also check regularly the ``gemseo-http`` webpage to be sure to be up-to-date
with the package and its dependencies.
