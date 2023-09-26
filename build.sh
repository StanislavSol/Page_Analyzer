!/usr/bin/env bash
make install && psql -a --dbname=dbproject --file=database.sql
