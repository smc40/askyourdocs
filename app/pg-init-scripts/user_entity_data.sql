COPY user_entity FROM '/docker-entrypoint-initdb.d/user_entity_data.csv' WITH CSV HEADER;
COPY CREDENTIAL FROM '/docker-entrypoint-initdb.d/user_credential_data.csv' WITH CSV HEADER;