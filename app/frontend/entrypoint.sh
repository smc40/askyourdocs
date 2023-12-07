#!/bin/bash

set -e

sed -i "s#\"auth-server-url\":.*#\"auth-server-url\": \"${KEYCLOAK_URL}\",#" public/keycloak.json
sed -i "s#backendUrl: .*#backendUrl: '${BACKEND_URL}',#" src/config.js
npm run start
