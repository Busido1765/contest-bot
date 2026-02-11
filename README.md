# Contest Bot

Репозиторий содержит инфраструктуру для запуска Telegram-бота конкурсов и связанного Web App (mini app).

## Что внутри

Проект запускается набором контейнеров:

- `bot` — основной Telegram-бот.
- `bg` — фоновые задачи (Celery worker + beat).
- `api` — HTTP API (FastAPI/uvicorn).
- `front` — мини-приложение (Node/Yarn dev server на 3000).
- `redis` — брокер и backend для фоновых задач.

## Текущий практический приоритет

Если ваша цель сейчас — **быстро поднять бота и адаптировать контент под свой проект**, используйте краткий сценарий ниже.

Более подробное техническое ревью и идеи улучшений на будущее вынесены в отдельный файл:
- `docs/infra-review.md`

---

## Быстрый старт (рекомендуется для первого запуска)

### 1) Подготовьте `.env`

В репозитории есть пример env-файла: `doc_2026-02-11_13-30-10.env.example`.

1. Создайте `.env` рядом с `docker-compose.yml`.
2. Заполните минимум:

```env
BOT_TOKEN=<telegram_bot_token>
ROOT_ADMIN_TG_IDS=[123456789,987654321]
REDIS_PASS=<strong_password>

# В Docker-сети используйте host redis
REDIS_BROKER_URI=redis://:<REDIS_PASS>@redis:6379/11
REDIS_BROKER_RESULT_BACKEND_URI=redis://:<REDIS_PASS>@redis:6379/12
```

> В исходном примере env Redis указан через `localhost`; для Docker-сети обычно корректнее `redis`.

### 2) Подготовьте директории данных на хосте

```bash
sudo mkdir -p /var/bot/static /var/bot/db
sudo chown -R $USER:$USER /var/bot
```

### 3) Соберите образы

`docker-compose.yml` использует готовые имена образов, поэтому сначала соберите их вручную:

```bash
docker build -f Dockerfile.bot -t sl-tg-bot .
docker build -f Dockerfile.cron -t sl-tg-bot-bg .
docker build -f Dockerfile.api -t sl-tg-bot-api .
docker build -f Dockerfile.miniapp -t sl-tg-bot-miniapp .
```

### 4) Запустите контейнеры

```bash
docker compose up -d
docker compose ps
```

### 5) Проверьте логи ключевых сервисов

```bash
docker compose logs -f bot
docker compose logs -f api
docker compose logs -f bg
docker compose logs -f front
docker compose logs -f redis
```

---

## Что проверить после запуска

- Бот отвечает в Telegram.
- Админ с ID из `ROOT_ADMIN_TG_IDS` имеет доступ к админ-функциям.
- API отвечает (напрямую или через прокси).
- Mini app открывается.
- Фоновые задачи выполняются без ошибок.

---

## Nginx (если нужен reverse proxy)

В `nginx.conf` есть пример:
- `/` -> `https://localhost:3000/` (mini app)
- `/bot/api/` -> `http://localhost:8000/api/` (backend API)

Что сделать:
1. Положить конфиг в `/etc/nginx/sites-available/<your-domain>.conf`.
2. Проверить `server_name` и пути до TLS-сертификатов.
3. Включить сайт симлинком в `sites-enabled`.
4. Проверить конфиг: `sudo nginx -t`.
5. Перезапустить Nginx: `sudo systemctl reload nginx`.

> Если mini app внутри контейнера работает по HTTP, обычно используют `proxy_pass http://localhost:3000/;`.

---

## Обновление на сервере

Типовой сценарий:

```bash
git pull
docker build -f Dockerfile.bot -t sl-tg-bot .
docker build -f Dockerfile.cron -t sl-tg-bot-bg .
docker build -f Dockerfile.api -t sl-tg-bot-api .
docker build -f Dockerfile.miniapp -t sl-tg-bot-miniapp .
docker compose up -d
```

При необходимости очистите неиспользуемые образы:

```bash
docker image prune -f
```

---

## Быстрый troubleshooting

- `bot`/`api` падает сразу:
  - проверьте заполнение `.env`;
  - проверьте корректность `BOT_TOKEN`;
  - проверьте `REDIS_PASS` и Redis URI (host `redis`, корректный DB).
- Нет доступа к Web App/API через домен:
  - проверьте `nginx -t`;
  - проверьте TLS-сертификаты и `server_name`;
  - проверьте firewall/security group.
- Celery не выполняет задачи:
  - проверьте логи `bg`;
  - проверьте `REDIS_BROKER_URI` и `REDIS_BROKER_RESULT_BACKEND_URI`.

---

Если позже понадобится, можно добавить отдельный `docker-compose.prod.yml` с:
- `build`-секциями,
- healthcheck’ами,
- отключением публикации внутренних портов наружу.
