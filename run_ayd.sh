#!/bin/bash

set -e
set -u

docker compose -p ayd up solr -d
sudo chown 1001 /opt/solr
docker compose -p ayd up -d

docker exec -i ayd-postgres-1 psql -U $AYD_PSQL_USER -d $AYD_PSQL_DB -a -f /user_scripts/user_entity_data.sql

url="http://localhost:3000/"

if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "$url"  # Linux/Unix
elif [[ "$OSTYPE" == "darwin"* ]]; then
    open "$url"      # macOS
elif [[ "$OSTYPE" == "msys"* ]]; then
    start "$url"     # Windows (MSYS)
else
    echo "Unsupported operating system."
fi