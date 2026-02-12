#!/usr/bin/bash

cp -r ./src/docker/* .

docker build -f Dockerfile.bot . --tag sl-tg-bot
docker build -f Dockerfile.cron . --tag sl-tg-bot-bg
docker build -f Dockerfile.api . --tag sl-tg-bot-api
docker build -f Dockerfile.miniapp . --tag sl-tg-bot-miniapp
docker compose up --build -d
