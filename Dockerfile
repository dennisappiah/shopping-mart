FROM mysql:8

ENV MYSQL_ROOT_PASSWORD root
COPY ./data.sql /docker-entrypoint-initdb.d/data.sql