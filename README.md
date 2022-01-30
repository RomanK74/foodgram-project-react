[![codestyle PEP8, build and deploy](https://github.com/RomanK74/foodgram-project-react/actions/workflows/main.yaml/badge.svg)](https://github.com/RomanK74/foodgram-project-react/actions/workflows/main.yaml)

# Foodgram

### Описание

Проект Foodgram позволяет размещать рецепты, делиться и скачивать списки продуктов

### Регистрация пользователя

Регистрация проходит по форме регистрации на сайте

### Установка
Проект собран в Docker 20.10.06 и содержит четыре образа:

1. backend - образ бэка проекта
2. frontend - образ фронта проекта
3. postgres - образ базы данных PostgreSQL v 13.02
4. nginx - образ web сервера nginx

### Клонирование репозитория:

https://github.com/RomanK74/foodgram-project-react.git

#### Запуск проекта:
- Установите Docker
- Выполнить команду docker pull kroman74/foodgram

#### Первоначальная настройка Django:
- docker-compose exec web python manage.py migrate --noinput
- docker-compose exec web python manage.py collectstatic --no-input 

#### Загрузка тестовой фикстуры в базу:
docker-compose exec web python manage.py loaddata fixtures.json

#### Создание суперпользователя:
- docker-compose exec web python manage.py createsuperuser

#### Реквизиты администратора:
- email: admin@gmail.com
- password : admin
