
# Foodgram-idze

Онлайн-сервис **"Foodgram-idze: ваш Продуктовый Помощник"** для любителей вкусной еды с акцентом.

Проект позволяет публиковать рецепты, подписываться на публикации других авторов, добавлять рецепты в «Избранное», а также вести онлайн и скачивать на свое устройство "Список покупок", необходимых для приготовления понравившихся блюд.



## Адрес и документация

Адрес проекта: **https://foodgram-idze.ddns.net/**

Документация к API находится в файле docs/openapi-schema.yml и доступна по эндпоинту ```/api/docs/```

## Технологии

- Python 3.9  
- Django
- Django Rest Framework
- Docker
- Gunicorn
- NGINX
- PostgreSQL
- GitHub Actions  


* Continuous Integration
* Continuous Deployment

## Деплой

- ### Запуск проекта локально:

Клонируйте репозиторий и перейдите в папку с файлом ```docker-compose.yml```:
```bash
  git clone git@github.com:ArnoSimonian/foodgram-project.git
  cd foodgram-project/infra/
```
Создайте в папке ```infra/``` файл ```.env``` с переменными окружения, следуя образцу заполнения:
```bash
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres  
POSTGRES_USER=postgres  
POSTGRES_PASSWORD=postgres  
DB_HOST=db  
DB_PORT=5432  
```
Соберите и запустите контейнеры через Docker Compose:
```bash
docker compose up --build
```
Выполните следующие команды для проведения миграций, сбора статики и наполнения базы тестовыми данными:
```bash
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py collectstatic
docker compose exec backend python manage.py load_data
```
Проект станет доступен по адресу [localhost/](http://localhost:80/)

- ### Запуск проекта на сервере:
Создайте папку `foodgram/` с файлом ```.env``` в домашней директории вашего сервера. Образец заполнения файла приведен выше.

Настройте в `nginx` перенаправление запросов на порт 8000:
```sh
location / {
        proxy_pass http://127.0.0.1:8000;
}
```
Получите HTTPS-сертификат для доменного имени:
```sh
sudo certbot --nginx
```
Добавьте в Secrets на GitHub Actions следующие переменные:

`DOCKER_USERNAME` _#  логин на Docker Hub_

`DOCKER_PASSWORD` _# пароль на Docker Hub_

`SSH_KEY` _# закрытый SSH-ключ для подключения к серверу_

`SSH_PASSPHRASE` _# пароль от этого ключа_

`USER` _#и мя пользователя на сервере_

`HOST` _# IP-адрес сервера_

`TELEGRAM_TO` _# ID телеграм-аккаунта для сообщений об успешном деплое_

`TELEGRAM_TOKEN` _# токен телеграм-бота_


При отправке коммита в ветку `master` с помощью `push` будет выполнен полный деплой проекта. Подробности в файле [main.yml](https://github.com/ArnoSimonian/foodgram-project/blob/master/.github/workflows/main.yml).
## Авторы

- Арно Симонян [@ArnoSimonian](https://github.com/ArnoSimonian)
