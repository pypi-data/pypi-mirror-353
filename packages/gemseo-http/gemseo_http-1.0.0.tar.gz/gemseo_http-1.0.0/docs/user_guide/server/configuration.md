<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->
# Configuration

## Environment Variables

### Authentication Settings
- **GEMSEO_HTTP_SECRET_KEY**
  Secret key used for JSON Web Token encoding/decoding operations.

- **GEMSEO_HTTP_ALGORITHM**
  Algorithm used for JWT encoding/decoding processes.

- **GEMSEO_HTTP_ACCESS_TOKEN_EXPIRE_MINUTES**
  Duration (in minutes) before an access token expires.

### Storage Configuration
- **GEMSEO_HTTP_USER_DATABASE_PATH**
  File system path to the SQLite user database.

- **GEMSEO_HTTP_USER_FILE_DIRECTORY**
  Directory path where uploaded user files are stored.

- **GEMSEO_HTTP_USER_WORKSPACE_EXECUTION**
  Directory path where job executions are performed.

### Task Queue Configuration
- **GEMSEO_HTTP_HUEY_DATABASE_PATH**
  File system path to the Huey task manager database.

- **GEMSEO_HTTP_HUEY_IMMEDIATE_MODE**
  When enabled (`True`), Huey operates synchronously instead of asynchronously.
  Primarily used for testing purposes to avoid running a separate Huey worker.

- **GEMSEO_HTTP_HUEY_IMMEDIATE_MODE_IN_MEMORY**
  When enabled (`True`), Huey operates in memory without a message broker.
  Typically used in testing environments.

### Debug Settings
- **GEMSEO_HTTP_FASTAPI_DEBUG**
  Enable/disable FastAPI debug mode.

- **GEMSEO_HTTP_DATABASE_DEBUG**
  Enable/disable SQLModel debug mode.

These environment variables can be configured either by setting them manually in your system environment or by using a
`.env` file.
A template `.env` file with example configurations is provided in the root directory of the project.
