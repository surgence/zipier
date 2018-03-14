# zipier

This is an example project. Only the admin is operational. The project itself is a zapier exercise. You can create Webhooks actions in the admin and then run them through `./manage.py shell`

## Doing things locally

Initial Setup
==

#### Python

The Python3 version we are currently using is 3.5.
To start Python3 virtualenv using virtualenvwrapper:

```
mkvirtualenv --python=[path-to-py3-executable] [name-of-env]
```

Replace `[path-to-py3-executable]` with the path to the Python3 executable.
To find this out simply execute `which python3` on your machine

Once in the new virtualenv run:

```
pip install -r requirements-dev.txt
```

#### Database

To create the Postgres DB *locally* and an associated user with maxed-out privileges:

```
brew install postgres
```

Start the Postgres server

```
export PGDATA=/usr/local/var/postgres
postgres
```

Create the user and its database

```
psql -d postgres
CREATE DATABASE zipier encoding=utf8;
CREATE USER zipier;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO zipier;
ALTER USER zipier CREATEDB;
```

Run initial migrations
```
cp local_settings_example.py local_settings.py
./manage.py migrate
```

#### Frontend

No Frontend is included in this example


#### Finally

You should be good to go!

Create a superuser
```
./manage.py createsuperuser
```

Run the server:
```
./manage.py runserver
```

Build a Zip and a Action.

Use `shell` to fire the action.
