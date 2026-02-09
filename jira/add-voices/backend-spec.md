# Backend Spec: Advanced TTS (Add Voices) — MVP

## 1. Цели

- Добавить более естественные голоса
- Сохранить совместимость с текущим TTS
- Обеспечить масштабируемость и предсказуемую стоимость

## 2. Провайдеры

### 2.1 Основной (MVP)
- Qwen3‑TTS (self‑hosted)
- Формат: mp3
- Язык: ru‑RU

### 2.2 Fallback
- Системный TTS (Web Speech API / FlutterTTS)

## 3. Архитектура

- Бекенд приложения вызывает **TTS‑сервис** по HTTP
- TTS‑сервис изолирован (можно вынести на отдельный GPU‑сервер)
- Бекенд получает `audioUrl` и сохраняет в `messages.audioUrl`

## 4. Контракты API (TTS‑сервис)

### 4.1 GET /voices
Ответ:
- `id` (string)
- `name` (string)
- `lang` (string)
- `gender` (optional)
- `provider` (string)
- `quality` (optional)

### 4.2 POST /speak
Вход:
- `text` (string)
- `voiceId` (string)
- `format` (mp3)
- `speed` (optional)
- `pitch` (optional)
- `cacheKey` (optional)

Выход:
- `audioUrl` (string)
- `durationMs` (number)
- `cached` (boolean)

### 4.3 POST /preview
Вход:
- `voiceId`
- `format` (mp3)

Выход:
- `audioUrl`

## 5. Хранение и кэш

- Аудио складывается в локальное хранилище или S3‑совместимый бакет
- TTL для preview: 1–24 часа
- TTL для ответов: 1–7 дней (настройка)
- Кэш ключ: `voiceId + text_hash + format`

## 6. Нормализация текста

- Удалять emoji/markdown/служебные символы
- Заменять единицы измерения на слова (°C → «градусов Цельсия»)
- Удалять повторяющиеся пробелы

## 7. Безопасность

- Ограничение длины текста (например, 3–5k символов)
- Rate‑limit на пользователя/IP
- Санация входных данных
- Логи без текста пользователя (PII‑safe)

## 8. Наблюдаемость

- Метрики: latency, error‑rate, cache‑hit
- Логи ошибок с `requestId`
- Алерты при деградации

## 9. Инфраструктура

- GPU‑сервер (TBD: модель/VRAM/latency)
- Контейнеризация (Docker)
- Отдельный домен: `tts.<domain>`

## 10. Ограничения MVP

- Только ru‑RU
- Только mp3
- Без стриминга (batch)

## 11. Юридические вопросы (TBD)

- Лицензия Qwen3‑TTS
- Коммерческое использование
- Требования к атрибуции

## 12. Конфигурация (ENV)

- `TTS_PROVIDER=qwen3`
- `TTS_BASE_URL=https://tts.<domain>`
- `TTS_FORMAT=mp3`
- `TTS_LANG=ru-RU`
- `TTS_CACHE_TTL_SEC=86400`
- `TTS_TIMEOUT_MS=20000`
