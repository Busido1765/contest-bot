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

## Deployment / Docker Compose

> `docker-compose.yml` в корне и `src/docker/docker-compose.yml` содержат одинаковый набор сервисов (`bot`, `bg`, `api`, `front`, `redis`) с `build`, `env_file: .env` и host-bind volumes `/var/bot/...`. Обычно достаточно работать с корневым файлом.

### A) Prerequisites

- Docker Engine (с поддержкой `docker compose` plugin).
- Git.
- Доступ на запись к директориям на хосте: `/var/bot/static` и `/var/bot/db`.

Проверка:

```bash
docker --version
docker compose version
```

### B) Setup `.env`

1. Скопируйте пример переменных в корне репозитория:

```bash
cp doc_2026-02-11_13-30-10.env.example .env
```

2. Обязательно проверьте/задайте минимум:

```env
BOT_TOKEN=<telegram_bot_token>
BOT_WEBAPP_NAME=<mini_app_short_name_from_@BotFather>
ROOT_ADMIN_TG_IDS=[123456789,987654321]
REDIS_PASS=<strong_password>
REDIS_BROKER_URI=redis://:<REDIS_PASS>@redis:6379/11
REDIS_BROKER_RESULT_BACKEND_URI=redis://:<REDIS_PASS>@redis:6379/12
```

3. Подготовьте директории данных на VPS (используются как bind mounts):

```bash
sudo mkdir -p /var/bot/static /var/bot/db
sudo chown -R $USER:$USER /var/bot
```

### C) First deploy (первый запуск)

Рекомендуемая команда (сборка + запуск в фоне):

```bash
docker compose up -d --build
```

Проверка состояния:

```bash
docker compose ps
```

### D) Update after code changes

Обычное обновление:

```bash
git pull
docker compose up -d --build
```

Обновление с полной пересборкой без кэша (когда нужно «чисто» пересобрать образы):

```bash
git pull
docker compose build --no-cache bot bg api front
docker compose up -d
```

> Legacy/альтернатива: ручные `docker build -f Dockerfile.* ...` обычно не нужны, т.к. текущий compose уже содержит `build` для `bot/bg/api/front`.

### E) Restart / Logs / Inspect env

Безопасный перезапуск (данные в `/var/bot/...` сохраняются):

```bash
docker compose down
docker compose up -d
```

Логи сервиса:

```bash
docker compose logs -f --tail=200 <service>
```

Примеры:

```bash
docker compose logs -f --tail=200 bot
docker compose logs -f --tail=200 api
```

Проверка env внутри контейнера:

```bash
docker compose exec -T <service> env | sort | grep -E "BOT_TOKEN|ROOT_ADMIN|REDIS"
```

Пример:

```bash
docker compose exec -T bot env | sort | grep -E "BOT_TOKEN|ROOT_ADMIN|REDIS"
```

### F) Clean reset (destructive)

Обычная остановка (safe):

```bash
docker compose down
```

Полный сброс окружения (destructive):

```bash
docker compose down -v
```

⚠️ **ВНИМАНИЕ:** `down -v` удаляет volumes/docker-тома проекта. Если вы храните критичные данные в Docker volumes, они будут потеряны. Для этого проекта основные данные вынесены в bind mounts (`/var/bot/static`, `/var/bot/db`), но команду всё равно используйте только осознанно.

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

Базовый сценарий обновления:

```bash
git pull
docker compose up -d --build
```

При необходимости очистите неиспользуемые образы:

```bash
docker image prune -f
```

> Legacy: ручные `docker build -f Dockerfile.* ...` оставляйте только как исключение (например, для отладки отдельных образов).

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
