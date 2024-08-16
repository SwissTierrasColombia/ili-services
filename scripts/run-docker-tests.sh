#!/usr/bin/env bash
#***************************************************************************
#                             -------------------
#       begin                : 2017-08-24
#       git sha              : :%H$
#       copyright            : (C) 2017 by OPENGIS.ch
#       email                : info@opengis.ch
#***************************************************************************
#
#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************
set -e

printf "Wait a moment while loading the PG database."
for i in {1..15}
do
  if PGPASSWORD=${ILISERVICES_DB_PASS} psql -h ${ILISERVICES_DB_HOST} -U ${ILISERVICES_DB_USER} -p ${ILISERVICES_DB_PORT} -l &> /dev/null; then
    break
  fi
  printf "\nAttempt $i..."
  sleep 2
done
printf "\nPostgreSQL ready!\n"

cd /app/iliservices
nose2
