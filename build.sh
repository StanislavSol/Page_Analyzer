#!/usr/bin/env bash

make install && psql database -a  -f database.sql
