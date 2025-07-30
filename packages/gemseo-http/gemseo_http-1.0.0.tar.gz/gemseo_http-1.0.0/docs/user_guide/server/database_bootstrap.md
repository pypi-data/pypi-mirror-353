<!--
Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com

This work is licensed under the Creative Commons Attribution-ShareAlike 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by-sa/4.0/ or send a letter to Creative
Commons, PO Box 1866, Mountain View, CA 94042, USA.
-->

# Setting up the SQL database

The web application and worker rely on a SQL database to store essential data,
including user information,
job details,
and file records.


## Using Alembic (preferred)

[Alembic](https://alembic.sqlalchemy.org/en/latest/) is a Python library that helps you manage
the database migrations, based on the [SQLAlchemy](https://www.sqlalchemy.org/) or
 [SQLModel](https://sqlmodel.tiangolo.com/) ORM.

To bootstrap or to migrate an existing database, follow these steps:

1. Firstly, set up accordingly the alembic.ini file. Especially,
set correctly the `sqlalchemy.url` parameter to point to the database,
either a file or a remote database. For a database bootstrap,
the SQLite database file can be inexistent. In case of migration,
the path to the current database must be provided.
2. Then, run the following command:
```shell
alembic upgrade head
```
The database will either be created or migrated.

## Using the `gemseo-http` CLI

This method enables to bootstrap the database using the `gemseo-http` CLI.
In contrast to Alembic, this method does not require any configuration file,
but the migration to a more recent database would be more complex using Alembic.

To do so, follow these steps:

1. Navigate to the directory where you intend to store the database. For example:
   ```plaintext
   /opt/gaas/database/
   ```

2. Execute the following command to create the database:
   ```bash
   gemseo-http create-db
   ```

# Adding users

Currently, the only way to add users is through the command-line interface.

To add users to the database, use the command below:
   ```bash
   gemseo-http create-user-in-db <username> <password>
   ```
   Replace `<username>` and `<password>` with the desired credentials for the user.

With these steps, your database will be ready for use.
