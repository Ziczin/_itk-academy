#!/bin/bash
set -e

echo "Запуск миграций базы данных..."
alembic upgrade head || { echo "Ошибка миграции"; exit 1; }

echo "Запуск приложения..."
exec python main.py
