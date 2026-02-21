# Frontend Spec: Голосовой UX независимо от браузера

## Цели frontend-части

- Единый UX голосового ввода на web/desktop/mobile.
- Минимальная зависимость от браузерных STT API.
- Явная диагностика и прозрачный fallback.

## Текущее отклонение

- Web: STT через Web Speech API, что ломается на части окружений (Raspberry Chromium).
- Desktop/mobile: нет единого "server audio first" поведения для TTS playback.

## Целевое поведение (MVP)

### Ввод голоса

- Основной путь:
  - запись микрофона -> отправка в backend STT -> получение partial/final текста.
- Fallback:
  - если backend STT недоступен, показать понятную ошибку и предложить ручной ввод.
  - локальный browser STT использовать только опционально по флагу.

### Озвучка ответа

- Основной путь:
  - если есть `audioUrl`, воспроизводить `audioUrl`.
- Fallback:
  - если `audioUrl` отсутствует/ошибка воспроизведения, использовать локальный TTS.

## UI/UX требования

- Индикаторы статуса:
  - `Слушаю...`
  - `Распознаю...`
  - `Готово`
  - `Ошибка микрофона/распознавания`
- Информирование о текущем режиме:
  - `Voice mode: server stt`
  - `Voice mode: local fallback`
- Кнопка микрофона должна явно отражать:
  - idle / recording / disabled / error.

## Диагностика в клиенте

- В debug-режиме выводить:
  - доступность микрофона,
  - выбранный voice mode,
  - stt session id / tts state / audio playback status.
- Добавить toggle `debugVoiceLogs` (например, через `--dart-define`).

## Feature flags (предложение)

- `USE_BACKEND_STT=true|false`
- `USE_LOCAL_WEB_STT_FALLBACK=true|false`
- `AUDIO_URL_PLAYBACK_FIRST=true|false`

## Кросс-платформенный план

- Web:
  - записывать аудио и отправлять на backend STT.
- Linux desktop:
  - тот же backend STT путь.
  - обязательный playback `audioUrl` как first-class.
- Android/iOS:
  - по возможности тоже унифицировать на backend STT для одинакового поведения.

## Критерии приемки frontend

- На Raspberry в браузере микрофон стабильно работает через backend STT.
- На desktop Linux вход/выход голоса работает без зависимости от конкретного браузера.
- При отказе STT/TTS пользователь получает понятное сообщение и рабочий fallback.
