# Tasks: STT/TTS Cross-Platform Reliability

> Отмечайте чекбоксы по мере выполнения задачи.  
> Не переходите к следующему этапу, пока не закрыты проверки текущего этапа.

## Этап 0. Подтверждение проблемы и рамок

- [ ] Зафиксировать воспроизводимость на Raspberry (web, Chromium): `SpeechRecognition -> error: network`.
- [ ] Зафиксировать успешный `getUserMedia` (микрофон и permissions корректны).
- [ ] Подтвердить целевую архитектуру: backend STT как основной путь.
- [ ] Подтвердить fallback-политику (локальный STT/TTS только как резерв).
- [ ] Проверка этапа: согласованные ADR/решения по API и rollout.

## Этап 1. Backend API для STT

- [x] Спроектировать контракты `WS /stt/stream` и `POST /stt/transcribe`.
- [x] Реализовать валидацию аудиоформатов, размеров и таймаутов.
- [x] Добавить единый error format с кодами retriable/non-retriable.
- [ ] Реализовать логирование с correlation id.
- [ ] Подзадачи:
  - [ ] Добавить integration tests для streaming STT.
  - [ ] Добавить integration tests для batch STT.
  - [ ] Добавить rate limiting и базовые лимиты.
- [ ] Проверка этапа: e2e тест STT endpoint'ов + latency smoke.

## Этап 2. Интеграция TTS статусов и audioUrl

- [ ] Унифицировать `ttsState` значения и договор по `audioUrl`.
- [ ] Гарантировать консистентный ответ assistant-message в API.
- [ ] Добавить метрики успешного формирования `audioUrl`.
- [ ] Подзадачи:
  - [ ] Тест: `audioUrl` присутствует при `ttsState=ready`.
  - [ ] Тест: корректный fallback при `ttsState=failed`.
- [ ] Проверка этапа: e2e от запроса к assistant до воспроизведения `audioUrl`.

## Этап 3. Frontend: voice pipeline refactor

- [ ] Внедрить backend STT клиент (streaming/batch).
- [ ] Ввести `voice mode` состояния в UI (server/local/error).
- [ ] Сделать `audioUrl playback first` во всех платформах.
- [ ] Сохранить локальный TTS как fallback.
- [ ] Исправить iOS web playback-policy кейс (Safari/Chrome): гарантировать запуск озвучки после пользовательского жеста (tap/click) и корректный fallback.
- [ ] Подзадачи:
  - [ ] Явные toast/snackbar сообщения для ошибок микрофона/STT/TTS.
  - [ ] Debug logs toggle (`debugVoiceLogs`) и диагностическая панель.
  - [ ] Защита от "молчаливого" падения микрофона.
- [ ] Проверка этапа: ручные сценарии на web + linux desktop + android (если входит в релиз).

## Этап 4. Кросс-браузерная валидация

- [ ] Прогнать сценарии: Chrome/Chromium/Firefox на целевых ОС.
- [ ] Отдельно прогнать iOS Safari/Chrome: chat playback + preview playback + fallback-поведение после жеста пользователя.
- [ ] Прогнать сценарии на Raspberry (VNC и локальная сессия при необходимости).
- [ ] Подтвердить стабильность частичных и финальных результатов STT.
- [ ] Подтвердить воспроизведение `audioUrl` и fallback TTS.
- [ ] Проверка этапа: тест-отчет и список residual risks.

## Этап 5. Релиз и наблюдаемость

- [ ] Включить rollout через feature flags.
- [ ] Запустить canary и мониторинг ошибок/latency.
- [ ] Подготовить rollback-план (быстрое отключение backend STT флага).
- [ ] Обновить пользовательскую и техническую документацию.
- [ ] Проверка этапа: релизный чек-лист подписан.

## Бэклог (после стабилизации)

- [ ] VAD и endpointing-тюнинг для снижения финальной задержки.
- [ ] Улучшение качества на шумных микрофонах.
- [ ] Автовыбор языка/локали.
- [ ] Offline/edge режим STT для ограниченных сетей.
