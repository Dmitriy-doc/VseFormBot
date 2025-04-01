#!/bin/bash

echo "=== Установка VseFormBot на VPS ==="

# Обновляем пакеты
sudo apt update && sudo apt upgrade -y

# Устанавливаем зависимости
sudo apt install -y python3 python3-pip python3-venv git nginx

# Клонируем репозиторий
cd /opt
sudo git clone https://github.com/Dmitriy-doc/VseFormBot.git
cd VseFormBot

# Настройка виртуального окружения
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Создание .env
echo "Введите BOT_TOKEN:"
read BOT_TOKEN
echo "Введите WEBHOOK_URL:"
read WEBHOOK_URL

cat <<EOF | sudo tee .env > /dev/null
BOT_TOKEN=$BOT_TOKEN
WEBHOOK_URL=$WEBHOOK_URL
EOF

# Создание systemd сервиса
sudo bash -c 'cat > /etc/systemd/system/vseformbot.service' <<EOL
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

# Запуск сервиса
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable vseformbot
sudo systemctl start vseformbot

echo "=== VseFormBot установлен и запущен ==="
