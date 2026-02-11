# Contest Bot

Репозиторий содержит инфраструктуру для запуска Telegram-бота конкурсов и связанного Web App (mini app).

По структуре видно, что проект запускается набором контейнеров:

- `bot` — основной Telegram-бот.
- `bg` — фоновые задачи (Celery worker + beat).
- `api` — HTTP API (FastAPI/uvicorn).
- `front` — мини-приложение (Node/Yarn dev server на 3000).
- `redis` — брокер и backend для фоновых задач.

## 1. Требования к серверу

Минимально:

- Linux-сервер с установленными Docker и Docker Compose plugin.
- Открытые порты:
  - `443` — для HTTPS через Nginx.
  - `3000` — если нужен прямой доступ к mini app (обычно закрывают и отдают через Nginx).
  - `8000` — если нужен прямой доступ к API (обычно закрывают и отдают через Nginx).
  - `6379` — Redis (рекомендуется не публиковать наружу и ограничить firewall).
- Домен и TLS-сертификат (если используете Nginx из `nginx.conf`).

## 2. Подготовка переменных окружения

В репозитории есть пример env-файла: `doc_2026-02-11_13-30-10.env.example`.

1. Создайте `.env` рядом с `docker-compose.yml`.
2. Скопируйте значения из примера и заполните своими данными.

Базовый шаблон:

```env
BOT_TOKEN=<telegram_bot_token>
ROOT_ADMIN_TG_IDS=[123456789,987654321]

# Redis auth (используется в docker-compose для redis-server --requirepass)
REDIS_PASS=<strong_password>

# Укажите Redis URI с паролем и нужными DB
REDIS_BROKER_URI=redis://:<REDIS_PASS>@redis:6379/11
REDIS_BROKER_RESULT_BACKEND_URI=redis://:<REDIS_PASS>@redis:6379/12
```

Примечания:

- `ROOT_ADMIN_TG_IDS` — список Telegram ID администраторов, которым разрешён админ-доступ к боту.
- В примере из репозитория Redis указан как `localhost`; в Docker-сети корректнее использовать хост `redis`.
- Не храните реальные токены и пароли в git.

## 3. Подготовка директорий для данных

Сервисам пробрасываются volumes:

- `/var/bot/static/` -> `/app/static/`
- `/var/bot/db/` -> `/app/db/`

Создайте их на сервере заранее:

```bash
sudo mkdir -p /var/bot/static /var/bot/db
sudo chown -R $USER:$USER /var/bot
```

## 4. Сборка Docker-образов

`docker-compose.yml` использует **готовые имена образов**, а не `build`-секции, поэтому сначала нужно собрать образы вручную.

Из корня проекта:

```bash
docker build -f Dockerfile.bot -t sl-tg-bot .
docker build -f Dockerfile.cron -t sl-tg-bot-bg .
docker build -f Dockerfile.api -t sl-tg-bot-api .
docker build -f Dockerfile.miniapp -t sl-tg-bot-miniapp .
```

## 5. Запуск контейнеров

```bash
docker compose up -d
```

Проверка статуса:

```bash
docker compose ps
docker compose logs -f bot
```

При первом запуске проверьте логи всех ключевых сервисов:

```bash
docker compose logs -f api
docker compose logs -f bg
docker compose logs -f front
docker compose logs -f redis
```

## 6. Настройка reverse proxy (Nginx)

В файле `nginx.conf` есть пример проксирования:

- `/` -> `https://localhost:3000/` (mini app)
- `/bot/api/` -> `http://localhost:8000/api/` (backend API)

Что сделать:

1. Положить конфиг в `/etc/nginx/sites-available/<your-domain>.conf`.
2. Проверить `server_name` и пути до TLS-сертификатов.
3. Включить сайт симлинком в `sites-enabled`.
4. Проверить конфиг: `sudo nginx -t`.
5. Перезапустить Nginx: `sudo systemctl reload nginx`.

> Если mini app работает по HTTP внутри контейнера, обычно используют `proxy_pass http://localhost:3000/;`. Проверьте это в вашем окружении.

## 7. Чек-лист после развёртывания

- Бот отвечает в Telegram.
- Админ с ID из `ROOT_ADMIN_TG_IDS` имеет доступ к админ-функциям.
- API отвечает через прокси endpoint `/bot/api/`.
- Mini app открывается по домену.
- Фоновые задачи выполняются без ошибок (логи `bg`).
- Redis доступен только из доверенной сети.

## 8. Обновление на сервере

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

## 9. Быстрый troubleshooting

- Контейнер `bot`/`api` падает сразу:
  - проверьте заполнение `.env`;
  - проверьте корректность `BOT_TOKEN`;
  - убедитесь, что Redis URI содержит пароль и правильный хост `redis`.
- Нет доступа к Web App/API через домен:
  - проверьте `nginx -t`;
  - проверьте TLS-сертификаты и `server_name`;
  - проверьте открытые порты firewall/security group.
- Celery не выполняет задачи:
  - проверьте логи `bg`;
  - проверьте `REDIS_BROKER_URI` и `REDIS_BROKER_RESULT_BACKEND_URI`.

---

Если нужно, можно дополнительно добавить отдельный `docker-compose.prod.yml` с `build`-секциями, healthcheck'ами и отключением публикации внутренних портов наружу.
