#!/bin/bash
set -euo pipefail

APP_DIR=${APP_DIR:-/home/ubuntu/webapp}
REPO_URL=${REPO_URL:-https://github.com/pragul1512-afk/webapp.git}
BRANCH=${BRANCH:-main}
APP_USER=${APP_USER:-ubuntu}
SECRET_KEY=${SECRET_KEY:-change-me-please}
PORT=${PORT:-8000}
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx git

sudo mkdir -p "$APP_DIR"
sudo chown -R "$APP_USER:$APP_USER" "$APP_DIR"

if [ ! -d "$APP_DIR/.git" ]; then
  sudo -u "$APP_USER" git clone --branch "$BRANCH" "$REPO_URL" "$APP_DIR"
else
  sudo -u "$APP_USER" git -C "$APP_DIR" fetch origin "$BRANCH"
  sudo -u "$APP_USER" git -C "$APP_DIR" checkout "$BRANCH"
  sudo -u "$APP_USER" git -C "$APP_DIR" pull origin "$BRANCH"
fi

cd "$APP_DIR"
sudo -u "$APP_USER" python3 -m venv .venv
sudo -u "$APP_USER" bash -lc 'source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'

sudo cp "$SCRIPT_DIR/restaurant-app.service" /etc/systemd/system/restaurant-app.service
sudo sed -i "s|/home/ubuntu/webapp|$APP_DIR|g" /etc/systemd/system/restaurant-app.service
sudo sed -i "s|change-me-please|$SECRET_KEY|g" /etc/systemd/system/restaurant-app.service
sudo systemctl daemon-reload
sudo systemctl enable restaurant-app
sudo systemctl restart restaurant-app

sudo cp "$SCRIPT_DIR/nginx.conf" /etc/nginx/conf.d/restaurant-app.conf
sudo sed -i "s|/home/ubuntu/webapp|$APP_DIR|g" /etc/nginx/conf.d/restaurant-app.conf
sudo sed -i "s|8000|$PORT|g" /etc/nginx/conf.d/restaurant-app.conf
sudo nginx -t
sudo systemctl restart nginx

sudo -u "$APP_USER" bash -lc "cd '$APP_DIR' && source .venv/bin/activate && python seed.py"
