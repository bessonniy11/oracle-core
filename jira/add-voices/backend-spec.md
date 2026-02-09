# Backend Spec: Advanced TTS (Add Voices) — PoC

## 1. Цели

- Добавить более естественные голоса
- Сохранить совместимость с текущим TTS
- Обеспечить масштабируемость и предсказуемую стоимость

## 2. Провайдеры

### 2.1 Основной (PoC)
- Qwen3‑TTS (self‑hosted)
- Модель: 0.6B
- Формат: mp3
- Язык: ru‑RU

### 2.2 Fallback
- Системный TTS (Web Speech API / FlutterTTS)

## 3. Архитектура

- Бекенд приложения вызывает TTS‑сервис по HTTP
- TTS‑сервис изолирован (можно вынести на отдельный GPU‑сервер)
- Бекенд получает `audioUrl` и сохраняет в `messages.audioUrl`

## 4. Контракты API (TTS‑сервис)

### 4.1 GET /voices
Ответ:
- `id` (string, stable)
- `name` (string)
- `lang` (string, e.g. `ru-RU`)
- `gender` (optional)
- `provider` (string)
- `quality` (optional: `low|medium|high`)
- `sampleUrl` (optional)
- `tags` (optional: string[])

### 4.2 POST /speak
Вход:
- `text` (string)
- `voiceId` (string)
- `format` (`mp3`)
- `speed` (optional, float, 0.5–1.5)
- `pitch` (optional, float, -5..+5)
- `cacheKey` (optional, string)
- `requestId` (optional, string)

Выход:
- `audioUrl` (string)
- `durationMs` (number)
- `cached` (boolean)

### 4.3 POST /preview
Вход:
- `voiceId` (string)
- `format` (`mp3`)

Выход:
- `audioUrl` (string)

### 4.4 Ошибки (единый формат)

- `code` (string, e.g. `TTS_TIMEOUT`, `VOICE_NOT_FOUND`)
- `message` (string)
- `requestId` (string)

## 5. Хранение и кэш

- Аудио складывается в локальное хранилище или S3‑совместимый бакет
- TTL для preview: 1–24 часа
- TTL для ответов: 1–7 дней (настройка)
- Кэш‑ключ: `voiceId + text_hash + format + speed + pitch`
- Очистка по TTL (cron/worker)

## 6. Нормализация текста

- Удалять emoji/markdown/служебные символы
- Заменять единицы измерения на слова (°C → «градусов Цельсия»)
- Удалять повторяющиеся пробелы
- Ограничивать длину текста до лимита

## 7. Безопасность

- Ограничение длины текста (например, 3–5k символов)
- Rate‑limit на пользователя/IP
- Санация входных данных
- Логи без текста пользователя (PII‑safe)
- Защита TTS‑сервиса (mTLS или сервисный ключ)

## 8. Наблюдаемость

- Метрики: latency, error‑rate, cache‑hit, queue‑depth
- Логи ошибок с `requestId`
- Алерты при деградации

## 9. Инфраструктура

- GPU‑сервер (TBD: модель/VRAM/latency)
- Контейнеризация (Docker)
- Отдельный домен: `tts.<domain>`

## 10. Ограничения PoC

- Только ru‑RU
- Только mp3
- Без стриминга (batch)
- Без voice‑cloning

## 11. Юридические вопросы (отложены)

- Юр‑проверка лицензий и условий использования перед коммерциализацией
- Проверка рисков voice‑impersonation

## 12. Конфигурация (ENV)

- `TTS_PROVIDER=qwen3`
- `TTS_BASE_URL=https://tts.<domain>`
- `TTS_FORMAT=mp3`
- `TTS_LANG=ru-RU`
- `TTS_CACHE_TTL_SEC=86400`
- `TTS_TIMEOUT_MS=20000`
- `TTS_AUTH_TOKEN=...`

## 13. Нефункциональные требования

- p95 latency для preview < 2s (цель)
- p95 latency для коротких ответов < 5s (цель)
- Ошибки TTS не должны ломать чат (fallback обязателен)
