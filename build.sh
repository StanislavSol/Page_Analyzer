!/usr/bin/env bash
make install && psql -a --dbname=$DAT$DATABASE_URL --file=database.sql
