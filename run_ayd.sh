#!/bin/bash

sudo rm -rf /opt/solr
sudo mkdir /opt/solr

set -e
set -u

sudo chown 1001 /opt/solr
docker compose -p ayd up -d

docker exec -i ayd-postgres-1 psql -U "${AYD_PSQL_USER:-ayd_dba}" -d $"${AYD_PSQL_DB:-ayd}" -a -f /user_scripts/user_entity_data.sql

url="http://localhost:8000/"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$url"  # Linux/Unix
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "$url"      # macOS
elif [[ "$OSTYPE" == "msys"* ]]; then
    start "$url"     # Windows (MSYS)
else
    echo "Unsupported operating system."
fi
