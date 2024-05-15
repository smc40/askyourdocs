#!/bin/bash

docker rm $(docker ps -aq) -f

sudo rm -rf /opt/solr; sudo mkdir /opt/solr
sudo rm -rf /opt/askyourdocs/uploads; sudo mkdir -p /opt/askyourdocs/uploads


set -e
set -u

sudo chown 1001 /opt/solr
sudo chown 1001 /opt/askyourdocs/uploads

# docker compose -p ayd build --no-cache
docker compose -p ayd up -d
# docker-compose -p ayd up -d

docker exec -i ayd-postgres-1 psql -U "${AYD_PSQL_USER:-ayd_dba}" -d "${AYD_PSQL_DB:-ayd}" -a -f /user_scripts/user_entity_data.sql

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

