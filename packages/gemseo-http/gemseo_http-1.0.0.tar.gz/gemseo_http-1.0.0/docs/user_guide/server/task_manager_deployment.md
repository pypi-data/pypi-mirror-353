<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->
# Task manager
While the web application can execute synchronous jobs,
using asynchronous jobs is recommended for tasks with long execution times (more than a few seconds).

For such asynchronous requests,
the Huey task manager must be used to run the jobs.
This decouples the web application from job execution.
This is particularly beneficial for long-running jobs,
as it allows them to run in the background without blocking the web application.

It also enables to carry out maintenance tasks on the Webapp,
while the jobs are still being executed.

The current queuing system is done through SQLite,
but it has to be noted that other queue managers such as Redis or RabbitMQ
are supported by Huey, but are not implemented yet in ``gemseo-http``.

## Development mode

Huey can be run interactively in a development context.
To do so, type the following command while having the Python environment activated:

`huey_consumer.exe gemseo_http_server.gemseo_runner.huey`

Please have a look at the [Huey](https://huey.readthedocs.io/en/latest/) documentation to see the options available.
For instance, to have two runners using multithreading, use the following command:

`huey_consumer.exe gemseo_http_server.gemseo_runner.huey -k thread -w 2`


## Production

As for the web application, it is recommended to run the Huey worker as a service,\
 using, for instance, SystemD or `docker-compose`.

The following script could be used to run the Huey worker:

```bash
set -e

export PATH=/opt/miniconda3/envs/gemseo_as_a_service/bin/:$PATH

# Those could be also sourced using an .env.skel file.
export GEMSEO_HTTP_ROOT_PATH=/opt/gaas
export GEMSEO_HTTP_HUEY_DATABASE_PATH=$GEMSEO_HTTP_ROOT_PATH/database/huey.db
export GEMSEO_HTTP_USER_DATABASE_PATH=$GEMSEO_HTTP_ROOT_PATH/database/database.db
export GEMSEO_HTTP_FILE_DIRECTORY=$GEMSEO_HTTP_ROOT_PATH/files/
export GEMSEO_HTTP_WORKSPACE_EXECUTION=$GEMSEO_HTTP_ROOT_PATH/workdir/

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
