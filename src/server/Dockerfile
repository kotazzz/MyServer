# Используйте официальный образ Python
FROM python:3.11

# Установка переменной окружения для вывода сообщений в консоль без буферизации
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и код в контейнер
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY *.py /app/server/

# Команда, которая будет выполнена при запуске контейнера
CMD ["sanic", "server.main:app", "--port", "24551", "--host", "0.0.0.0", "--dev"]