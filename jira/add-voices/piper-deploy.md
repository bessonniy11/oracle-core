# Piper TTS: Деплой на сервере

## 0) Ключевая идея

Бекенд не читает модели напрямую. Модели читает отдельный TTS‑сервис (Piper), а бекенд обращается к нему по HTTP.

## 1) Структура файлов (рекомендуемая)

```
projects/backend/tts/piper/ru_RU/
  ru_RU-*.onnx
  ru_RU-*.onnx.json
```

Папка `projects/backend/tts/` должна быть в `.gitignore` (веса не коммитим).

## 2) Переменные окружения

### Для TTS‑сервиса (Piper)

- `PIPER_VOICES_DIR=/path/to/projects/backend/tts/piper/ru_RU`
- `PIPER_BIN=piper` (по умолчанию)

### Для backend

- `TTS_BASE_URL=http://127.0.0.1:8082`
- `TTS_DEFAULT_VOICE_ID=ru_RU-irina-medium` (или любой из `/tts/voices`)
- `TTS_FORMAT=wav`
- `TTS_TIMEOUT_MS=120000` (CPU)

## 3) Установка Piper на сервере

```bash
python3 -m venv /opt/piper-venv
source /opt/piper-venv/bin/activate
pip install -U piper-tts fastapi uvicorn pathvalidate
```

## 4) Запуск сервиса (systemd)

`/etc/systemd/system/piper-tts.service`

```
[Unit]
Description=Piper TTS Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/projects/backend/tts/piper
Environment=PIPER_VOICES_DIR=/path/to/projects/backend/tts/piper/ru_RU
ExecStart=/opt/piper-venv/bin/uvicorn piper_local_server:app --host 127.0.0.1 --port 8082
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Применить:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now piper-tts
sudo systemctl status piper-tts
```

## 5) Проверка

```bash
curl http://127.0.0.1:8082/voices
curl -X POST http://127.0.0.1:8082/speak -H "content-type: application/json" -d '{"text":"Привет","voiceId":"ru_RU-irina-medium"}'
```

## 6) Безопасность

- Сервис слушает только `127.0.0.1`.
- Внешний доступ — только через бекенд.

## 7) Очистка аудио

Пока PoC: аудио складывается локально. Нужен TTL‑клин (cron/worker) для удаления старых файлов.
