# Contest Bot

Репозиторий содержит инфраструктуру для запуска Telegram-бота конкурсов и связанного Web App (mini app).

## Что внутри

Проект запускается набором контейнеров:

- `bot` — основной Telegram-бот.
- `bg` — фоновые задачи (Celery worker + beat).
- `api` — HTTP API (FastAPI/uvicorn).
- `front` — mini app в production-режиме (статическая сборка, отдаётся через Nginx **внутри контейнера** на порту 80).
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

#### Что такое `BOT_WEBAPP_NAME`

Это **не произвольное имя из кода** и не username бота.  
Это `short name` вашего Telegram Mini App (часть URL после имени бота):

```
https://t.me/<bot_username>/<BOT_WEBAPP_NAME>?startapp=...
```

Как получить/проверить:
1. Откройте `@BotFather` -> выберите бота.
2. Команда `/myapps` (или `/newapp` / `/editapp` в зависимости от интерфейса).
3. Найдите ваш Mini App и посмотрите его `short name` (slug).
4. Это значение и нужно записать в `.env` как `BOT_WEBAPP_NAME`.

Если Mini App не создан, сначала создайте его в BotFather и задайте домен (HTTPS).

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

> После изменений: `front` больше не запускается через Vite dev server — собирается `yarn build` и отдаётся встроенным Nginx (production-подход).

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

Важно: в проекте уже есть Nginx внутри контейнера `front`, он раздаёт статику mini app.
Хостовый Nginx (устанавливается на VPS) нужен отдельно только для домена/HTTPS (443) и проксирования к контейнерам.

В `nginx.conf` есть пример:
- `/` -> `http://localhost:3000/` (mini app, Nginx-контейнер front)
- `/bot/api/` -> `http://localhost:8000/api/` (backend API)

Что сделать:
1. Положить конфиг в `/etc/nginx/sites-available/<your-domain>.conf`.
2. Проверить `server_name` и пути до TLS-сертификатов.
3. Включить сайт симлинком в `sites-enabled`.
4. Проверить конфиг: `sudo nginx -t`.
5. Перезапустить Nginx: `sudo systemctl reload nginx`.

> Для production-конфига из этого репозитория `front` слушает HTTP на порту 80 внутри контейнера и публикуется как `3000:80`, поэтому upstream прокси: `http://localhost:3000/`.

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
  - проверьте firewall/security group;
  - если видите `ERR_CONNECTION_CLOSED`, чаще всего Nginx проксирует mini app на неверный upstream (например, `https://localhost:3000` вместо `http://127.0.0.1:3000` для Vite в контейнере).
- `nginx: command not found` или `nginx.service not found`:
  - у вас не установлен Nginx (или используется другой reverse proxy/панель);
  - либо установите и настройте Nginx, либо откройте внешний 443/80 на другой прокси (Caddy/Traefik) до `front`/`api`;
  - проверьте, что контейнер `front` действительно запущен: `docker compose ps front`;
  - проверьте логи фронта: `docker compose logs -f --tail=200 front`.
- `curl -I http://127.0.0.1:3000/` возвращает `Empty reply from server`:
  - обычно фронт отвечает по HTTPS (Vite basic SSL) или процесс фронта не поднялся;
  - проверьте протокол: `curl -kI https://127.0.0.1:3000/`;
  - либо отключите HTTPS в Vite и используйте HTTP upstream в прокси (см. `src/miniapp/vite.config.ts`).
- Celery не выполняет задачи:
  - проверьте логи `bg`;
  - проверьте `REDIS_BROKER_URI` и `REDIS_BROKER_RESULT_BACKEND_URI`.

---

Если позже понадобится, можно добавить отдельный `docker-compose.prod.yml` с:
- `build`-секциями,
- healthcheck’ами,
- отключением публикации внутренних портов наружу.


## Готовый чеклист для VPS (production)

Ниже команды для Ubuntu/Debian сервера, где домен уже указывает на ваш VPS.

Этот чеклист именно для **хостового Nginx**.
Nginx внутри `front` уже есть и дополнительно не ставится — ставим только reverse proxy на самом VPS.

1. Установите Nginx и Certbot:

```bash
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx
```

2. Убедитесь, что DNS уже указывает на сервер:

```bash
dig +short contestbotcurling.ru
curl -I http://contestbotcurling.ru
```

3. Задеплойте контейнеры проекта:

```bash
cd ~/contest-bot
git pull
docker compose up -d --build
```

4. Создайте Nginx site config из `nginx.conf` проекта:

```bash
sudo cp ~/contest-bot/nginx.conf /etc/nginx/sites-available/contestbotcurling.ru.conf
sudo ln -sf /etc/nginx/sites-available/contestbotcurling.ru.conf /etc/nginx/sites-enabled/contestbotcurling.ru.conf
sudo rm -f /etc/nginx/sites-enabled/default
```

5. Проверьте Nginx и перезагрузите:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

6. Выпустите/подключите TLS-сертификат через Certbot:

```bash
sudo certbot --nginx -d contestbotcurling.ru -m you@example.com --agree-tos --no-eff-email
```

7. Проверка доступности backend/frontend:

```bash
curl -I http://127.0.0.1:3000/
curl -I http://127.0.0.1:8000/api/health || true
curl -I https://contestbotcurling.ru/
curl -I https://contestbotcurling.ru/bot/api/
```

8. Если что-то не работает — сразу смотрите логи:

```bash
sudo journalctl -u nginx -n 200 --no-pager
docker compose logs -f --tail=200 front api bot
```
