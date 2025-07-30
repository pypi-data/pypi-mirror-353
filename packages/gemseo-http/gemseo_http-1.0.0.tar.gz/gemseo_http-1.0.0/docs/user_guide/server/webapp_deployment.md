<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->
# Webapp

## Development
It is possible to create a development environment using the following command:

`tox -e py[39, 310, 311] --develop`

where the Python interpreter version should be selected.

To run the Webapp
in the activated tox environment,
use the following command in local:

`uvicorn.exe gemseo_http_server.app:app --reload`

The webapp will be reachable at <http://localhost:8000>.

You can also specify to `uvicorn` the `.env` file that you want to use, using the `--env-file <path>` option:

`uvicorn.exe gemseo_http_server.app:app --reload --env-file /the/path/to/my/env/file.env`

### Production

It is strongly recommended to read the [Security](security_notes.md) section,
and implement them.

Also, as `gemseo-http` is a FastAPI application,
it is recommended to read the [FastAPI deployment notes](https://fastapi.tiangolo.com/deployment/).
Have also a look at the [Uvicorn documentation](https://www.uvicorn.org/) if you use this ASGI server.

It is also recommended to expose the application as a service,
either using `Systemd` or `Docker`.

We recommend the following tree structure:

```
/opt/gemseo_http/bin # Contains the running script.
/opt/gemseo_http/log # Contains the log files.
/opt/gemseo_http/database # Contains the SQLite databases, if any.
/opt/gemseo_http/files # Contains the uploaded files.
/opt/gemseo_http/files/chunks # Contains the uploaded file chunks.
/opt/gemseo_http/workdir/ # The jobs workdir.

```
but you could use an arbitrary one.

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

uvicorn gemseo_http_server.app:app --host 0.0.0.0
```
but you could also opt to put all the environment variables in a `.env` file and source them using the
uvicorn `--env-file` option.

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
but you could also use `docker-compose` to manage the service.
