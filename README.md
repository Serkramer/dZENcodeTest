# dZENcodeTest

## ⚙️ Установка и запуск проекта

### 1. Клонировать репозиторий

https://github.com/Serkramer/dZENcodeTest.git


### 2. Создать .env файл в корневой папке пректа со следующим содержимым:


#### DEBUG=False
#### SECRET_KEY=XXX

#### DB_NAME=XXX
#### DB_USER=XXX
#### DB_PASS=XXX
#### DB_HOST=XXX
#### DB_PORT=XXX

*вместо XXX подставьте ваши данные


### 3. Создать и запустить проект через докер

docker-compose up --build