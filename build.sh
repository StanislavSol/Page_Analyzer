!/usr/bin/env bash
make install && psql -a --dbname=$DATABASE_URL --file=database.sql
