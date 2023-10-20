#!/bin/bash

set -e
set -u

docker compose -p ayd up solr -d
sudo chown 1001 /opt/solr
docker compose -p ayd up -d

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