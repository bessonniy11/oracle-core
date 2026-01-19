# План развертывания backend на VPS (Ubuntu 22.04)

## 0. Предварительные условия
- SSH доступ к серверу (root@5.8.76.233).
- Открытый порт API (3000) внутрь; внешний доступ через nginx.
- Репозиторий: https://github.com/bessonniy11/oracle-core-backend/tree/start_dev

## 1. Базовые пакеты и Node.js
```bash
apt update && apt upgrade -y
apt install -y curl git ufw
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
```

## 2. PostgreSQL
```bash
apt install -y postgresql postgresql-contrib
sudo -u postgres psql -c "CREATE USER oracle_core WITH PASSWORD 'strong_pass';"
sudo -u postgres psql -c "CREATE DATABASE oracle_core OWNER oracle_core;"
```

## 3. Клонирование проекта
```bash
mkdir -p /opt/oracle-core
cd /opt/oracle-core
git clone -b start_dev https://github.com/bessonniy11/oracle-core-backend.git backend
cd backend
npm install
```

## 4. .env бэкенда
`/opt/oracle-core/backend/.env`:
```
DATABASE_URL=postgres://oracle_core:strong_pass@localhost:5432/oracle_core
NODE_ENV=production
PORT=3000
AI_API_KEY=...
AI_MODEL=gemini-2.5-flash
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://oracle.ibessonniy.ru,https://api.oracle.ibessonniy.ru
JSON_BODY_LIMIT=1mb
RATE_LIMIT_PER_MIN=60
AI_TIMEOUT_MS=30000
AI_MAX_INPUT_CHARS=16000
```

## 5. Миграции
```bash
npm run migration:run
```

## 6. Запуск через PM2
```bash
npm install -g pm2 ts-node typescript
pm2 start node_modules/.bin/ts-node --name oracle-core-api -- src/index.ts
pm2 save
pm2 startup systemd
pm2 logs oracle-core-api --lines 50
```

## 7. Firewall (по желанию)
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp   # если нужен прямой доступ, иначе можно не открывать
ufw enable
```

## 8. Обновления/деплой
```bash
cd /opt/oracle-core/backend
git pull
npm install
npm run migration:run
pm2 restart oracle-core-api
```

## 9. Перезапуск после правок .env
```bash
cd /opt/oracle-core/backend
pm2 restart oracle-core-api
pm2 logs oracle-core-api --lines 50
```

## 10. Проверка
- `curl http://127.0.0.1:3000/personas`
- Убедиться, что порт 3000 слушает: `ss -tulpn | grep 3000`

## 11. Nginx и HTTPS для API
- DNS: A-запись `api.oracle.ibessonniy.ru -> 5.8.76.233`
- Конфиг `/etc/nginx/sites-available/api-oracle`:
```
server {
    listen 80;
    server_name api.oracle.ibessonniy.ru;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- Включить: `ln -sf /etc/nginx/sites-available/api-oracle /etc/nginx/sites-enabled/api-oracle`
- Удалить default, перезагрузить: `rm /etc/nginx/sites-enabled/default; nginx -t && systemctl reload nginx`
- SSL: `certbot --nginx -d api.oracle.ibessonniy.ru -m bessonniy11@gmail.com --agree-tos --redirect`
- Проверка: `curl -v https://api.oracle.ibessonniy.ru/personas`

## 12. Настройки фронтенда
- Прод: `--dart-define=API_BASE_URL=https://api.oracle.ibessonniy.ru`
- Dev локально: `--dart-define=API_BASE_URL=http://localhost:3000` (порт 5173 для web dev)
- Убедиться, что CORS_ORIGINS содержит домены фронта.

## 13. Деплой фронта
- Сборка web прод: `flutter build web --release --dart-define=API_BASE_URL=https://api.oracle.ibessonniy.ru`
- Залить статику на `oracle.ibessonniy.ru`.
- Проверить, что запросы идут к `https://api.oracle.ibessonniy.ru/*`.
