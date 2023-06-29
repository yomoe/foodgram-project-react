# Продуктовый помощник

Foodgram - это "Продуктовый помощник", онлайн-сервис, где пользователи могут публиковать рецепты, подписываться на других пользователей, добавлять понравившиеся рецепты в избранное и скачивать список продуктов для приготовления блюд. Это удобный инструмент для обмена рецептами и планирования покупок продуктов.
## Доступы на сайт

Сайт доступен по адресу: https://i.zifir.io

Логин/пароль для входа в админку: `admin@zifir.io` `7*K&fQ&DX2m8`

Демо-аккаунты:

`user1@example.com` `p@ssw0rd1`

`user2@example.com` `p@ssw0rd1`

`user3@example.com` `p@ssw0rd1`

`user4@example.com` `p@ssw0rd1`

`user5@example.com` `p@ssw0rd1`

## Использованные технологии

![Docker](https://img.shields.io/badge/Docker-2496ed?style=for-the-badge&logo=docker&logoColor=white)![Postgres](https://img.shields.io/badge/Postgres-336791?style=for-the-badge&logo=Postgresql&logoColor=white)![Python](https://img.shields.io/badge/Python-30363d?style=for-the-badge&logo=Python&logoColor=yellow)![Django](https://img.shields.io/badge/Django-103e2e?style=for-the-badge&logo=Django&logoColor=white)![NodeJS](https://img.shields.io/badge/NodeJS-404137?style=for-the-badge&logo=Node.JS&logoColor=83cd29)

## Функционал сайта

* **Публикация рецептов**: Пользователи могут публиковать свои рецепты с указанием ингредиентов, времени приготовления и подробного описания процесса. К каждому рецепту можно прикрепить изображение.
* **Подписка на авторов**: Пользователи могут подписываться на других пользователей, чтобы следить за их новыми рецептами.
* **Избранное**: Пользователи могут добавлять понравившиеся рецепты в список "Избранное" для быстрого доступа к ним в будущем.
* **Список покупок**: Пользователи могут добавлять рецепты в список покупок. Сервис автоматически сгенерирует список всех необходимых для приготовления блюд ингредиентов.
* **Фильтрация по тегам**: Пользователи могут фильтровать рецепты по тегам, чтобы быстро найти нужные рецепты.
* **Регистрация и авторизация**: Сервис предлагает систему регистрации и авторизации пользователей.

## Подготовка к запуску

Установите Docker и Docker-compose на сервер.
```
sudo apt update
```
```
sudo apt install curl
``` 
```
curl -fSL https://get.docker.com -o get-docker.sh
```
```
sudo sh ./get-docker.sh
```
```
sudo apt-get install docker-compose-plugin
```

Клонируйте репозиторий:
```
git clone https://github.com/yomoe/foodgram-project-react.git
```
В папке с проектом переименуйте файл `.env.example` в `.env` и заполните его своими данными:

`POSTGRES_USER` - имя пользователя для базы данных

`POSTGRES_PASSWORD` - пароль для базы данных

`POSTGRES_DB` - имя базы данных

`SECRET_KEY` - секретный ключ для Django

`DEBUG` - режим отладки Django

`ALLOWED_HOSTS` - список разрешенных хостов

`START` - задачи при старте контейнера

`IMPORT_DATA` - добавление демоданных в базу: ингредиенты, теги, рецепты, пользователи

`DB_HOST` - имя хоста базы данных

`DB_PORT` - порт базы данных

`NGINX_PORT` - порт Nginx

`DOCKER_LOGIN` - логин от Docker Hub

## Запуск проекта

Находясь в папке с проектом запустите проект командой:
```
sudo docker compose -f docker-compose.production.yml up -d
```

## Настройка CI/CD
Файл workflow уже написан. Он находится в директории .github/workflows/main.yml
Для его работоспособности добавьте секреты в GitHub Actions:

`DOCKER_PASSWORD` - пароль от Docker Hub

`DOCKER_USERNAME` - логин от Docker Hub

`HOST` - ip адрес сервера

`USER` - имя пользователя на сервере

`SSH_KEY` - приватный ключ для подключения к серверу

`SSH_PASSPHRASE` - пароль от приватного ключа

`TELEGRAM_TO` - id пользователя в Telegram

`TELEGRAM_TOKEN` - токен бота в Telegram
