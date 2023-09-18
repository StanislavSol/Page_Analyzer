!/usr/bin/env bash
make install && psql -a --dbname=DB_Page_analyzer --file=database.sql
