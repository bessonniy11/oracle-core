# Outline VPN на Linux: полная пошаговая инструкция

Этот гайд покрывает **оба реальных сценария**:

1. Установка официального `Outline Client` на Linux `x86_64`.
2. Установка на ARM-устройства (например, Raspberry Pi), где официального клиента обычно нет, через совместимый `shadowsocks-libev`.

---

## 0) Быстрая проверка архитектуры (обязательно)

```bash
uname -m
```

- `x86_64` -> можно ставить официальный Outline Client (`.AppImage`).
- `aarch64` / `arm64` -> `.AppImage` от Outline чаще всего **неподходящий** (обычно `x86-64`), нужен ARM-сценарий через `shadowsocks-libev`.

Проверка скачанного AppImage:

```bash
file ~/Desktop/Outline-Client*.AppImage
```

Если там `x86-64`, а у системы `aarch64`, клиент нативно не запустится.

---

## 1) Сценарий A: официальный Outline Client (Linux x86_64)

### 1.1 Скачивание и подготовка

```bash
mkdir -p ~/Applications
mv ~/Downloads/Outline-Client*.AppImage ~/Applications/Outline-Client.AppImage
chmod +x ~/Applications/Outline-Client.AppImage
```

### 1.2 Тестовый запуск

```bash
~/Applications/Outline-Client.AppImage
```

### 1.3 Ярлык на рабочем столе

```bash
cat > ~/Desktop/Outline-Client.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Outline Client
Comment=Outline VPN client
Exec=/home/$USER/Applications/Outline-Client.AppImage
Icon=network-vpn
Terminal=false
Categories=Network;
StartupNotify=true
EOF

chmod +x ~/Desktop/Outline-Client.desktop
```

### 1.4 Автозапуск после входа в систему

```bash
mkdir -p ~/.config/autostart
cp ~/Desktop/Outline-Client.desktop ~/.config/autostart/Outline-Client.desktop
```

---

## 2) Сценарий B: ARM Linux / Raspberry Pi (через shadowsocks-libev)

> Это не GUI-клиент Outline, а совместимый клиент по `ss://` ключу.  
> Работает стабильно, но по умолчанию это **локальный SOCKS5-прокси**, а не full-tunnel VPN всей системы.

### 2.1 Установка клиента

```bash
sudo apt update
sudo apt install -y shadowsocks-libev
```

### 2.2 Создание конфига `/etc/shadowsocks-libev/outline.json`

Пример (замени значения на свои из ключа Outline):

```bash
sudo install -d -m 755 /etc/shadowsocks-libev

sudo tee /etc/shadowsocks-libev/outline.json >/dev/null <<'EOF'
{
  "server": "YOUR_SERVER_IP_OR_DOMAIN",
  "server_port": YOUR_SERVER_PORT,
  "password": "YOUR_PASSWORD",
  "method": "chacha20-ietf-poly1305",
  "local_address": "127.0.0.1",
  "local_port": 1080,
  "mode": "tcp_and_udp"
}
EOF
```

### 2.3 Критично про права доступа

На многих системах сервис `shadowsocks-libev-local@.service` запускается с `DynamicUser=true`, поэтому файл с `600 root:root` может не читаться, и будет ошибка:

- `ERROR: Invalid config path`

Рабочий и простой вариант:

```bash
sudo chmod 644 /etc/shadowsocks-libev/outline.json
```

### 2.4 Включение автозапуска сервиса

```bash
sudo systemctl enable --now shadowsocks-libev-local@outline.service
sudo systemctl status shadowsocks-libev-local@outline.service --no-pager -l
```

Проверка порта:

```bash
ss -lntup | grep 1080
```

Ожидаемо: `127.0.0.1:1080` (TCP/UDP).

---

## 3) Использование прокси в браузере (ARM-режим)

Если сервис активен, но сайты идут как раньше, значит браузер не использует SOCKS-прокси.

Запуск Chromium через Outline:

```bash
chromium \
  --proxy-server="socks5://127.0.0.1:1080" \
  --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
  --user-data-dir="$HOME/.config/chromium-outline"
```

### 3.1 Надежный ярлык для Chromium через Outline

Создаем скрипт:

```bash
mkdir -p ~/.local/bin

cat > ~/.local/bin/chromium-outline <<'EOF'
#!/usr/bin/env bash
exec chromium \
  --proxy-server="socks5://127.0.0.1:1080" \
  --host-resolver-rules="MAP * ~NOTFOUND , EXCLUDE 127.0.0.1" \
  --user-data-dir="$HOME/.config/chromium-outline"
EOF

chmod +x ~/.local/bin/chromium-outline
```

Создаем `.desktop`:

```bash
cat > ~/Desktop/Chromium-Outline.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Chromium via Outline
Comment=Chromium через Outline SOCKS5
Exec=/home/bessonniy11/.local/bin/chromium-outline
Icon=chromium-browser
Terminal=false
Categories=Network;WebBrowser;
StartupNotify=true
EOF

chmod +x ~/Desktop/Chromium-Outline.desktop
gio set ~/Desktop/Chromium-Outline.desktop metadata::trusted true
```

> Почему через скрипт: сложные аргументы в `Exec=` часто ломаются в `.desktop` и дают ошибку `Desktop entry contains no valid Exec line`.

---

## 4) Ярлыки управления сервисом (ON / OFF / STATUS)

```bash
cat > ~/Desktop/Outline-ON.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Outline ON
Comment=Запустить Outline proxy
Exec=lxterminal -e bash -lc "sudo systemctl start shadowsocks-libev-local@outline.service; systemctl --no-pager status shadowsocks-libev-local@outline.service; echo; read -p 'Нажми Enter для выхода...'"
Icon=network-vpn
Terminal=false
Categories=Network;
StartupNotify=true
EOF

cat > ~/Desktop/Outline-OFF.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Outline OFF
Comment=Остановить Outline proxy
Exec=lxterminal -e bash -lc "sudo systemctl stop shadowsocks-libev-local@outline.service; systemctl --no-pager status shadowsocks-libev-local@outline.service; echo; read -p 'Нажми Enter для выхода...'"
Icon=network-offline
Terminal=false
Categories=Network;
StartupNotify=true
EOF

cat > ~/Desktop/Outline-STATUS.desktop <<'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=Outline STATUS
Comment=Проверить статус Outline proxy
Exec=lxterminal -e bash -lc "systemctl --no-pager status shadowsocks-libev-local@outline.service; ss -lntup | grep 1080 || true; echo; read -p 'Нажми Enter для выхода...'"
Icon=utilities-system-monitor
Terminal=false
Categories=Network;
StartupNotify=true
EOF

chmod +x ~/Desktop/Outline-ON.desktop ~/Desktop/Outline-OFF.desktop ~/Desktop/Outline-STATUS.desktop
```

---

## 5) Диагностика и частые ошибки

### Ошибка: `Invalid config path`

Проверить:

```bash
sudo ls -l /etc/shadowsocks-libev/outline.json
sudo python3 -m json.tool /etc/shadowsocks-libev/outline.json >/dev/null && echo "JSON OK"
systemctl cat shadowsocks-libev-local@.service
```

Обычно решается:

```bash
sudo chmod 644 /etc/shadowsocks-libev/outline.json
sudo systemctl restart shadowsocks-libev-local@outline.service
```

### Сервис активен, но "VPN не работает"

Это значит браузер/приложение не использует SOCKS.  
Проверка IP:

```bash
curl -4 https://api.ipify.org ; echo
curl -4 --socks5-hostname 127.0.0.1:1080 https://api.ipify.org ; echo
```

IP должны отличаться.

### `Desktop entry contains no valid Exec line`

Лечится выносом команды в отдельный скрипт и запуском скрипта через `Exec=...` (см. раздел 3.1).

---

## 6) Безопасность

- Не публикуй `ss://` ключи в чатах/репозиториях.
- Если ключ уже утек, выпусти новый в Outline Manager и старый отключи.
- Файл `outline.json` с правами `644` удобен для `DynamicUser=true`, но менее приватен на многопользовательской системе.

---

## 7) Что считать "готово"

- Сервис `shadowsocks-libev-local@outline.service` в статусе `active (running)`.
- Порт `127.0.0.1:1080` слушается.
- Chromium через отдельный ярлык `Chromium via Outline` открывает сайты через другой внешний IP.
- После перезагрузки сервис стартует автоматически.
