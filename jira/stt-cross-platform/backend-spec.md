# Backend Spec: Унифицированный голосовой контур (STT/TTS)

## Цели backend-слоя

- Дать платформенно-независимый STT API.
- Возвращать стабильные TTS-артефакты (`audioUrl`) для клиента.
- Обеспечить трассируемость цепочки голосового запроса.

## Scope (MVP)

- STT endpoint (streaming preferred, batch fallback).
- TTS endpoint уже существует, но нужен единый контракт статусов и ошибок.
- Сервисные метрики, корреляционные идентификаторы, ограничение размеров аудио.
- Выбранный стек STT для MVP: `faster-whisper` (self-hosted) через отдельный локальный STT-сервис.

## Текущая реализация (MVP v1)

- Backend websocket endpoint: `WS /stt/stream` (в Node backend).
- STT backend-клиент: проксирует аудио в `STT_BASE_URL + /transcribe`.
- STT движок: Python FastAPI сервис `projects/backend/stt/faster-whisper/stt_local_server.py`.
- Формат обмена между Node backend и STT-сервисом: JSON с `audioBase64`.

### Переменные окружения (backend)

- `STT_BASE_URL` — адрес STT-сервиса (пример: `http://127.0.0.1:8090`)
- `STT_TIMEOUT_MS` — таймаут запроса в STT
- `STT_MAX_AUDIO_BYTES` — лимит аудио в одном запросе `/transcribe`
- `STT_STREAM_MAX_BUFFER_BYTES` — лимит буфера на websocket-сессию
- `STT_STREAM_PARTIAL_INTERVAL_MS` — минимальный интервал между partial
- `STT_DEFAULT_LANGUAGE` — язык по умолчанию

## API-контракты (предложение)

### 1) Streaming STT (предпочтительно)

- `WS /stt/stream`
- Вход:
  - `{"type":"start","language?","sessionId?"}`
  - бинарные аудио-чанки **или** `{"type":"chunk","audioBase64":"..."}`
  - `{"type":"commit"}` — получить финальный текст по текущему буферу
  - `{"type":"stop"}` — завершить сессию
  - `{"type":"ping"}` — heartbeat
- Выход:
  - `connected` / `started` / `pong`
  - `partial` (промежуточный текст),
  - `final` (финальный сегмент),
  - `error` (машиночитаемые коды).

### 2) Batch STT (fallback)

- `POST /stt/transcribe`
- Вход: `multipart/form-data`, поле `audio`, параметры `language`, `sessionId`.
- Выход:
  - `{ text, segments?, confidence?, latencyMs }`

### 3) Chat/TTS интеграция

- В текущем потоке сообщений assistant-ответ должен стабильно включать:
  - `audioUrl` (если TTS успешно),
  - `ttsState` (`ready|processing|failed|skipped`).

## Нефункциональные требования

- p95 latency (MVP целевые ориентиры):
  - partial STT < 800 мс,
  - final STT < 2000 мс,
  - TTS first-byte < 1500 мс.
- Таймауты и retry-политика с idempotency-key для batch STT.
- Ограничения:
  - max длина запроса по времени,
  - max размер аудио,
  - rate limit per client/user.

## Observability

- Логировать без PII/сырых аудиоданных (или с коротким TTL и маскированием).
- correlation id на весь запрос:
  - `stt_request_id`
  - `chat_request_id`
  - `tts_request_id`
- Метрики:
  - stt_error_rate, stt_latency_p50/p95
  - tts_audio_ready_rate
  - end_to_end_voice_turn_latency

## Ошибки (единый формат)

- Пример:
  - `{ code, message, retriable, details? }`
- Минимальные коды:
  - `STT_UNAVAILABLE`
  - `STT_BAD_AUDIO_FORMAT`
  - `STT_TIMEOUT`
  - `TTS_UNAVAILABLE`
  - `TTS_AUDIO_GENERATION_FAILED`

## Безопасность

- Проверка контента и лимитов до передачи в модель.
- Auth/tenant-проверки как для текстового чата.
- Защита от audio abuse:
  - размер/длительность/частота запросов.

## План миграции (без ломки текущего API)

1. Добавить новые STT endpoint'ы без удаления текущего поведения.
2. Включить feature flag для frontend: `USE_BACKEND_STT`.
3. Провести canary rollout (по устройствам/браузерам).
4. После стабилизации сделать backend STT default.
