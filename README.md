# Проект: Foodgram
### Дипломный проект *Яндекс.Практикум* курса Backend-разработчик(python)

Проект Foodgram дает возможность пользователям создавать и хранить рецепты на онлайн-платформе. Кроме того, можно скачать список продуктов, необходимых для приготовления блюда, просмотреть рецепты друзей и добавить любимые рецепты в список избранных.

## Технологии
1. Python
2. Django
3. Django REST Framework
4. Djoser
5. SQLite
6. Postman
7. PostgreSQL
8. Gunicorn
9. Nginx
10. React
11. Docker
12. GitHub Actions

## Запуск проекта (только backend)

### Требования
* Python 3.9+

1. Клонирование репозитория и переход в директорию проекта
``` bash
    git clone https://github.com/ZoroMak/foodgram-st.git
    cd foodgram-st/backend
```

2. Создание и активация виртуального окружения
``` bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
```

3. Установка зависимостей
``` bash
    pip install --upgrade pip
    pip install -r requirements.txt
```

4. Настройка переменных окружения (backend/.env)

* Необязательно, но см. **.env_example**

5. Применение миграций и загрузка данных
``` bash
    python manage.py makemigration
    python manage.py migrate
    python manage.py load_ingredients
```

6. Сбор статических файлов
``` bash
    python manage.py collectstatic --noinput
```

7. Запуск проекта
``` bash
    python manage.py runserver
```

8. Открытие в браузере

* Сайт: http://127.0.0.1:8000
* Админка: http://127.0.0.1:8000/admin


## Запуск проекта локально из корневой директории проекта

1. Описать файл infra/.env (см. .env_example)

2. Запустить Docker compose и выполнить следующие команды:
``` bash
sudo docker compose -f infra/docker-compose.yml up -d
docker-compose exec foodgram-backend python manage.py collectstatic
docker-compose exec foodgram-backend cp -r /app/collected_static/. /static/static/
```

## Запуск проекта на удаленном сервере

1. Установить docker compose на сервер

2. Скачать файл [docker-compose.production.yml](https://github.com/ZoroMak/foodgram-st/blob/main/docker-compose.production.yml) на сервер.

3. На сервере в директории с файлом **docker-compose.production.yml** создать файл  **.env** (см. .env-example):

4. Запустить Docker compose:
``` bash
sudo docker compose -f docker-compose.production.yml up -d
```

## Автор проекта [**Зоров Максим**](https://github.com/ZoroMak)