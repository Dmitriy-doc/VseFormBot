#!/bin/bash

echo "=== Установка VseFormBot на VPS ==="

# 1. Обновляем пакеты
apt update && apt upgrade -y

# 2. Устанавливаем зависимости
apt install -y python3 python3-pip python3-venv git nginx

# 3. Клонируем репозиторий
cd /opt
git clone https://github.com/Dmitriy-doc/VseFormBot.git
cd VseFormBot

# 4. Настройка виртуального окружения
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Создание .env
echo "Введите BOT_TOKEN:"
read BOT_TOKEN
echo "Введите WEBHOOK_URL:"
read WEBHOOK_URL

cat <<EOF > .env
BOT_TOKEN=$BOT_TOKEN
WEBHOOK_URL=$WEBHOOK_URL
EOF

# 6. Создание systemd сервиса
cat <<EOL > /etc/systemd/system/vseformbot.service
[Unit]
Description=VseFormBot Telegram Bot
After=network.target

[Service]
User=root
WorkingDirectory=/opt/VseFormBot
ExecStart=/opt/VseFormBot/.venv/bin/python3 /opt/VseFormBot/bot.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 7. Запуск сервиса
systemctl daemon-reexec
systemctl daemon-reload
systemctl enable vseformbot
systemctl start vseformbot

echo "=== VseFormBot установлен и запущен ==="
