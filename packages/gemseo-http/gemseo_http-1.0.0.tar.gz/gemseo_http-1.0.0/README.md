<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# gemseo-http

[![PyPI - License](https://img.shields.io/pypi/l/gemseo-http)](https://www.gnu.org/licenses/lgpl-3.0.en.html)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/gemseo-http)](https://pypi.org/project/gemseo-http/)
[![PyPI](https://img.shields.io/pypi/v/gemseo-http)](https://pypi.org/project/gemseo-http/)
[![Codecov branch](https://img.shields.io/codecov/c/gitlab/gemseo:dev/gemseo-http/develop)](https://app.codecov.io/gl/gemseo:dev/gemseo-http)

## Overview

`gemseo-http` is a [GEMSEO](https://gemseo.readthedocs.io/en/stable/) plugin designed to expose GEMSEO disciplines as web services.

It allows you to:

1.  **Expose GEMSEO Disciplines as Web Services:**
    *   Make your existing GEMSEO disciplines accessible over HTTP.
    *   Execute and linearize these disciplines remotely, either synchronously or asynchronously.
2.  **Utilize Remote Disciplines Locally:**
    *   Provides an `HTTPDiscipline` class that is a proxy to remote disciplines.
    *   Automatically configures this proxy to interact with a remote discipline service.

## Key Features

*   **Authentication:** Secure access using standard OAuth2/JWT.
*   **API Documentation:** Integrated Swagger UI available at the `/docs` endpoint for easy API exploration.
*   **File Handling:** Manages necessary file transfers for discipline execution between client and server.
*   **Asynchronous Execution:** Leverage [Huey](https://huey.readthedocs.io/en/latest/) for running discipline jobs asynchronously, potentially across multiple distributed nodes.
*   **Asynchronous Data Retrieval:** Fetch results from discipline executions asynchronously using long-polling.


## Bugs and questions

Please use the [gitlab issue tracker](https://gitlab.com/gemseo/dev/gemseo-http/-/issues)
to submit bugs or questions.

## Contributing

See the [contributing section of GEMSEO](https://gemseo.readthedocs.io/en/stable/software/developing.html#dev).

## Contributors

- Jean-Christophe Giret
- Antoine Dechaume
